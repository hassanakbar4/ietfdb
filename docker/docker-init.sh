#!/bin/bash

echo "Gathering info ..."
MYSQLDIR="$(mysqld --verbose --help 2>/dev/null | awk '$1 == "datadir" { print $2; exit }')"
if [ ! "$USER" ]; then
    echo "Environment variable USER is not set -- will set USER='django'."
    USER="django"
fi

echo "Checking if MySQL base data exists ..."
if [ ! -d $MYSQLDIR/mysql ]; then
    echo "WARNING: Expected the directory $MYSQLDIR/mysql/ to exist -- have you downloaded and unpacked the IETF binary database tarball?"
fi

echo "Checking if MySQL is running ..."
if ! /etc/init.d/mysql status; then
    echo "Starting mysql ..."
    /etc/init.d/mysql start
fi

echo "Checking if the IETF database exists at $MYSQLDIR ..."
if [ ! -d $MYSQLDIR/ietf_utf8 ]; then
    if [ -z "$DATADIR" ]; then
	echo "DATADIR is not set, but the IETF database needs to be set up -- can't continue, exiting the docker init script."
	exit 1
    fi
    ls -l $MYSQLDIR

    if ! /etc/init.d/mysql status; then
	echo "Didn't find the IETF database, but can't set it up either, as MySQL isn't running."
    else
	echo "Creating database ..."
	mysqladmin -u root --default-character-set=utf8 create ietf_utf8

	echo "Setting up permissions ..."
	mysql -u root ietf_utf8 <<< "GRANT ALL PRIVILEGES ON ietf_utf8.* TO django@localhost IDENTIFIED BY 'RkTkDPFnKpko'; FLUSH PRIVILEGES;"

	echo "Fetching database ..."       
	DUMPDIR=/home/$USER/$DATADIR
	wget -N -P $DUMPDIR http://www.ietf.org/lib/dt/sprint/ietf_utf8.sql.gz

	echo "Loading database ..."
	gunzip < $DUMPDIR/ietf_utf8.sql.gz \
	    | pv --progress --bytes --rate --eta --cursor --size $(gzip --list --quiet $DUMPDIR/ietf_utf8.sql.gz | awk '{ print $2 }') \
	    | sed -e 's/ENGINE=MyISAM/ENGINE=InnoDB/' \
	    | mysql --user=django --password=RkTkDPFnKpko -s -f ietf_utf8 \
	    && rm /tmp/ietf_utf8.sql.gz
    fi
fi

if ! id -u "$USER" &> /dev/null; then
    echo "Creating user '$USER' ..."
    useradd -s /bin/bash -G staff $USER
fi

if [ ! -d /opt/home/$USER ]; then
    echo "Setting up python virtualenv at /opt/home/$USER ..."
    mkdir -p /opt/home/$USER
    chown $USER /opt/home/$USER
    mkdir /opt/home/$USER/datatracker
    virtualenv --system-site-packages /opt/home/$USER/datatracker
fi

echo "Activating a virtual python environment ..."
cat /opt/home/$USER/datatracker/bin/activate >> /etc/bash.bashrc
. /opt/home/$USER/datatracker/bin/activate

if ! python -c "import django"; then
    echo "Installing requirements ..."
    pip install -r /usr/local/share/datatracker/requirements.txt
fi

if [ ! -f /opt/home/$USER/datatracker/lib/site-python/settings_local.py ]; then
    echo "Setting up a default settings_local.py ..."
    mkdir -p /opt/home/$USER/datatracker/lib/site-python/
    cp /usr/local/share/datatracker/settings_local.py /opt/home/$USER/datatracker/lib/site-python/
fi

chown -R $USER /opt/home/$USER

cd /home/$USER/$CWD || cd /home/$USER/

echo "Done!"

su $USER
