import sys
import optparse
import os
import lxml.etree
from svgcheck.checksvg import checkTree
from svgcheck.__init__ import __version__
from rfctools_common import log
from rfctools_common.parser import XmlRfcParser, XmlRfcError, CACHES


def display_version(self, opt, value, parser):
    print(__version__)
    sys.exit()


def clear_cache(cache_path):
    XmlRfcParser('', cache_path=cache_path).delete_cache()
    sys.exit()


def main():
    # Populate the options
    formatter = optparse.IndentedHelpFormatter(max_help_position=40)
    optionparser = optparse.OptionParser(usage='svgcheck SOURCE [OPTIONS] '
                                         '...\nExample: svgcheck draft.xml',
                                         formatter=formatter)

    parser_options = optparse.OptionGroup(optionparser, 'Parser Options')
    parser_options.add_option('-N', '--no-network', action='store_true', default=False,
                              help='don\'t use the network to resolve references')
    parser_options.add_option('-X', "--no-xinclude", action='store_true', default=False,
                              help='don\'t resolve xi:include elements')

    parser_options.add_option('-C', '--clear-cache', action='store_true', dest='clear_cache',
                              default=False, help='purge the cache and exit')
    parser_options.add_option('-c', '--cache', dest='cache',
                              help='specify a primary cache directory to write to;'
                              'default: try [ %s ]' % ', '.join(CACHES))

    parser_options.add_option('-d', '--rng', dest='rng', help='specify an alternate RNG file')
    optionparser.add_option_group(parser_options)

    other_options = optparse.OptionGroup(optionparser, 'Other options')
    other_options.add_option('-q', '--quiet', action='store_true',
                             help='don\'t print anything')
    other_options.add_option('-o', '--out', dest='output_filename', metavar='FILE',
                             help='specify an explicit output filename')
    other_options.add_option('-v', '--verbose', action='store_true',
                             help='print extra information')
    other_options.add_option('-V', '--version', action='callback', callback=display_version,
                             help='display the version number and exit')
    optionparser.add_option_group(other_options)

    svg_options = optparse.OptionGroup(optionparser, 'SVG options')
    svg_options.add_option('-r', '--repair', action='store_true', default=False,
                           help='Repair the SVG so it meets RFC 7966')
    optionparser.add_option_group(svg_options)

    # --- Parse and validate arguments --------------

    (options, args) = optionparser.parse_args()

    # Setup warnings module
    # rfclint.log.warn_error = options.warn_error and True or False
    log.quiet = options.quiet and True or False
    log.verbose = options.verbose

    if options.cache:
        if not os.path.exists(options.cache):
            try:
                os.makedirs(options.cache)
                if options.verbose:
                    log.write('Created cache directory at',
                              options.cache)
            except OSError as e:
                print('Unable to make cache directory: %s ' % options.cache)
                print(e)
                sys.exit(1)
        else:
            if not os.access(options.cache, os.W_OK):
                print('Cache directory is not writable: %s' % options.cache)
                sys.exit(1)

    if options.clear_cache:
        clear_cache(options.cache)

    sourceText = None
    if len(args) < 1:
        sourceText = sys.stdin.read()
        source = os.getcwd() + "/stdin"
    else:
        source = args[0]
        if not os.path.exists(source):
            sys.exit('No such file: ' + source)

    # Setup warnings module
    # rfclint.log.warn_error = options.warn_error and True or False
    log.quiet = options.quiet and True or False
    log.verbose = options.verbose

    # Parse the document into an xmlrfc tree instance
    parser = XmlRfcParser(source, verbose=options.verbose,
                          preserve_all_white=True,
                          quiet=options.quiet,
                          cache_path=options.cache,
                          no_network=options.no_network,
                          no_xinclude=options.no_xinclude)
    try:
        xmlrfc = parser.parse(remove_pis=True, remove_comments=False,
                              strip_cdata=False, textIn=sourceText)
    except XmlRfcError as e:
        log.exception('Unable to parse the XML document: ' + source, e)
        sys.exit(1)
    except lxml.etree.XMLSyntaxError as e:
        # Give the lxml.etree.XmlSyntaxError exception a line attribute which
        # matches lxml.etree._LogEntry, so we can use the same logging function
        log.exception('Unable to parse the XML document: ' + source, e.error_log)
        sys.exit(1)

    # Check that

    if not checkTree(xmlrfc.tree):
        if options.repair:
            if options.output_filename is None:
                file = sys.stdout
            else:
                file = open(options.output_filename, 'w')
            file.write(lxml.etree.tostring(xmlrfc.tree.getroot(),
                                           xml_declaration=True,
                                           encoding='utf-8',
                                           doctype=xmlrfc.tree.docinfo.doctype,
                                           pretty_print=True).decode('utf-8'))
        log.error("File does not conform to SVG requirements")
        sys.exit(1)

    log.info("File conforms to SVG requirements.")
    sys.exit(0)


if __name__ == '__main__':
    major, minor = sys.version_info[:2]
    if major == 2 and minor < 7:
        print("")
        print("The svgcheck script requires python of 2.7 or higher.")
        print("Can't proceed, quitting.")
        exit()

    main()
