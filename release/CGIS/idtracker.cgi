#!/usr/local/bin/perl

######################################################
#              
#      Program: idtracker.cgi
#      Author : Michael Lee, Foretec Seminars, Inc
#      Last Modified Date: 3/25/2002
#  
#      This Web application provides ID Draft Tracking and Maintaining 
#      capability to IESG Members
#
#####################################################

use lib '/export/home/mlee/RELEASE';
use CGI;
use IETF_UTIL;
use IETF_DBUTIL;

$ENV{"PROG_NAME"} = "idtracker.cgi";    #ENV Variable to be used by lib. files
$LOG_PATH = "/export/home/mlee/LOGs";
if (defined($ENV{HTTP_USER_AGENT})) {   # Get the version of client browser
   my $user_agent = $ENV{HTTP_USER_AGENT};
   @version_temp = split ' ',$user_agent;
   $browser_version = $version_temp[0];
} else {
   $browser_version = "Unknown Version";
}
my $q = new CGI;
$program_name = $ENV{"PROG_NAME"};

$fColor = "7DC189";
$sColor = "CFE1CC";
$menu_fColor = "F8D6F8";
$menu_sColor = "E2AFE2";

$private_txt = qq{<font color="red" size="-1">[private]</font>}; #Private Comment
$public_txt = qq{<font color="blue" size="-1">[public]</font>};  #Public Comment
$table_header = qq{<table cellpadding="1" cellspacing="0" border="0">
};
$form_header = qq{<form action="$program_name" method="POST" name="form1">
};
$form_header_search = qq{<form action="$program_name" method="POST" name="search_form">
};
$error_msg = qq{
<h2>There is a fatal error raised while processing your request</h2>
};


$db_mode = 0;    # To determine which database engine should be used
$INFORMIX = 1;   # Use Informix DB Engine
$MYSQL = 2;      # Use MySQL DB Engine
$CURRENT_DATE = "CURRENT_DATE"; # "TODAY" for Informix, "CURRENT_DATE" for MySQL
$CONVERT_SEED = 1; # To convert date format to fit into the current database engine
$ADMIN_MODE = 0;
my $html_txt;
my $refer = $ENV{HTTP_REFERER};  # To force user access this site only through 
 				 # the login screen
my $refer2 = $refer;
$refer = rm_tr($refer);
my @temp = split '/', $refer;
$refer = $temp[2];
$devel = "";


# The following lines need to be improved to decide which DB engine to be used
   
if ($refer eq "ran" or $refer eq "10.27.4.92" or $refer eq "localhost" or $refer eq "datatracker.ietf.org" or $refer eq "draft_tracker.ietf.org" or $q->param("command") eq "view_comment"){ #INFORMIX
   $_ = $ENV{HTTP_REFERER};
   if (/devel/) { #development mode
     ($db_mode,$CURRENT_DATE,$CONVERT_SEED,$is_null) = init_database($MYSQL);
     $ENV{"DBNAME"} = "ietf_test";
     $devel = "devel/";
   }elsif (/mysql/) {
     $db_mode = $MYSQL;
     $ENV{"DBNAME"} = "ietf";
     $devel = "mysql/";
   } else { #real mode
     ($db_mode,$CURRENT_DATE,$CONVERT_SEED,$is_null) = init_database($MYSQL);
   }
   
} else {
   $html_txt = login_screen("Please Login");
}




$html_top = qq{
<html>
<HEAD><TITLE>IESG ID Tracker v3.21 -- $browser_version</title>
<STYLE TYPE="text/css">
<!--

	  TD {text-decoration: none; color: #000000; font: 9pt arial;} 
	  A:Link {color: #0000ff; text-decoration:underline}
	  A:Hover {color: #ff0000; text-decoration:underline}
      A:visited {color: #0000ff; text-decoration:underline}
	  #largefont {font-weight: bold; color: #000000; font: 18pt arial}
	  #largefont2 {font-weight: bold; color: #000000; font: 16pt arial}
	  #largefont_red {font-weight: bold; color: #ff0000; font: 16pt arial}
-->
</STYLE>

</head>
<body link="blue" vlink="blue">
};
$html_bottom = qq{
<!-- begin new footer -->
<HR>
<A HREF="https://datatracker.ietf.org/cgi-bin/request.cgi">Version Control and Request Status</a>
<p>
<i>This page produced by the <A HREF="mailto:iesg-secretary\@ietf.org">IETF Secretariat</a> 
for the <A HREF="mailto:iesg\@ietf.org">IESG</A></i>
<p>
</body>
</html>
};
unless ($db_mode) {
   $html_body = $html_txt;
} else {
   $html_body = get_html_body($q);
}

#Main body of HTML

print <<END_HTML;
Content-type: text/html
$html_top
$html_body
$html_bottom
END_HTML



###########################################
#
#  Function : get_html_body
#  parameters:
#    $q : main cgi variable
#  result : body of HTML text
#
#  get_html_body calls appropriate function to generate the body of HTML.
#  get_html_body calls functions based on "command" cgi variable
#
########################################### 
sub get_html_body {
   my $q = shift;   # CGI variable
   my $command = $q->param("command");
   my $loginid = $q->param("loginid");
   my $switch = "-deploy";
   my $html_txt;
   if (my_defined($loginid)) {
         my $user_level = db_select("select user_level from iesg_login where id=$loginid");
         unless ($user_level) {
	           $ADMIN_MODE = 1;
		       my $admin_menu = get_admin_menu($loginid);
		       $html_top .= qq {
$admin_menu
};
	      }
         else {
           $html_top .= qq {
   $form_header
   <input type="hidden" name="command" value="gen_agenda">
   <input type="hidden" name="loginid" value="$loginid">
   <center><font color="red">NEW</font><input type="submit" value="              Draft Telechat Agenda                 "><font color="red">NEW</font></center>
   </form>

};
        }
   }
   unless (my_defined($command)) { # If no command passed, display login screen
      return login_screen();
   }
   elsif ($command eq "search_list") { # Display Search page
      if (defined($q->param("search_button"))) {
	     $html_txt = search_list ($q);
	  } elsif (defined($q->param("add_button"))) {
	     $html_txt = add_id_search ($q);
	  }
      
   }
   elsif ($command eq "verify_login") { # Verify login information passed in
      return verify_login ($q);
   }
   elsif ($command eq "main_menu") { # Display Main page
      return main_menu ();
   }
   elsif ($command eq "view_comment") { # Display Comment popup window
      return view_comment ($q);
   } elsif ($command eq "action") {
      $script_name = $q->param("cat");
	  system ("/export/home/mlee/RELEASE/gen_${script_name}_html.pl $switch");
      $func = "gen_${script_name}(\$q)";
      $html_txt .= eval($func);
   } elsif ($q->param("command") eq "edit_delete") {
      $gID = $q->param("gID");
	  if (defined($q->param("delete"))) {
		 db_update("delete from group_internal where group_acronym_id = $gID");
		 $html_txt .= gen_pwg($q);
      } elsif (defined($q->param("edit"))) {
	     $html_txt .= edit_pwg($q);
	  }
   } elsif ($q->param("command") eq "add_delete_pwg") {
      if (defined($q->param("delete"))) {
	     $html_txt .= delete_pwg($q->param("filename"));
	  } else {
         $html_txt .= add_pwg($q)
      }
   } elsif ($q->param("command") eq "add_db") {
      $html_txt .= add_db($q);
   } elsif ($q->param("command") eq "edit_db") {
      $html_txt .= edit_db($q);
   }
   else { # Generate a page depends on "command"
      my $func = "${command}(\$q)";
	  $html_txt = eval($func);
   }

# Display footer with "main" and "go back" button
   $html_txt .= qq {
   $form_header
   <input type="hidden" name="command" value="main_menu">
   <input type="hidden" name="loginid" value="$loginid">
   <input type="submit" value="Main Menu">
   <input type="button" name="back_button" value="BACK" onClick="history.go(-1);return true">
   </form>
   };
   return $html_txt;
}

###################################################
# Function: get_admin_menu
###################################################
sub get_admin_menu {
   my $loginid = shift;
   my $html_txt = qq {
   <center>
   $table_header
   <tr>
   $form_header
   <td>
   <input type="hidden" name="command" value="gen_agenda">
   <input type="hidden" name="loginid" value="$loginid">
   <input type="submit" value="Draft Telechat Agenda">
   </td>
   </form>

   $form_header
   <td>
   <input type="hidden" name="command" value="gen_pwg">
   <input type="hidden" name="loginid" value="$loginid">
   <input type="submit" value="Proposed Working Group">
   </td>
   </form>

   $form_header
   <td>
   <input type="hidden" name="command" value="gen_template">
   <input type="hidden" name="loginid" value="$loginid">
   <input type="submit" value="Templates">
   </td>
   </form>

   $form_header
   <td>
   <input type="hidden" name="command" value="gen_single">
   <input type="hidden" name="loginid" value="$loginid">
   <input type="submit" value="Generate Singles">
   </td>
   </form>

   </tr>
   </table>
   </center>
   };
   return $html_txt;
   
}

###################################################
#
#    Function : verify_login
#    Parameters :
#      $q : CGI variable
#    return : if valid login information, call main_menu to display main screen,
#             otherwise, re-call login_screen to display login screen with error message
#
#    This function receives login information from login screen and display appropriate
#    screen.
#
###################################################
sub verify_login {
   my $q = shift;
   my $html_txt;
   my $method = $ENV{REQUEST_METHOD};
   unless ($method eq "POST") { # Only accept information from HTML form
      $html_txt = login_screen("Please login");
	  return $html_txt;
   }
   my $login_name = $q->param("login_name");
   my $password = $q->param("password");
   $login_name = db_quote($login_name);
   my $sqlStr = "select count(*) from iesg_login where login_name = $login_name";
   my $count = db_select($sqlStr);
   if ($count == 1) { # login account found. Now, verify the password encrypted
      my ($loginid,$pass,$user_level) = db_select("select id,password,user_level from iesg_login where login_name = $login_name");
	  $pass = rm_tr($pass);
      if (crypt($password,$pass) eq $pass) {
         my $user_level = db_select("select user_level from iesg_login where id=$loginid");
         unless ($user_level) {
	           $ADMIN_MODE = 1;
		       my $admin_menu = get_admin_menu($loginid);
		       $html_top .= qq {
$admin_menu
};
	      }
         else {
           $html_top .= qq {
   $form_header
   <input type="hidden" name="command" value="gen_agenda">
   <input type="hidden" name="loginid" value="$loginid">
   <center><font color="red">NEW</font><input type="submit" value="              Draft Telechat Agenda                 "><font color="red">NEW</font></center>
   </form>

};
        }

          $html_txt = main_menu($loginid);
      } else {
          $html_txt = login_screen("Invalid...Try Again");
      }
	  
   } else { # login account not found
      $html_txt = login_screen("Invalid...Try Again");
   }
   return $html_txt;
}


#####################################################
#
# Functoin login_screen
# Parameters:
#   $err_msg : Error message, if existed
# return: HTML text for login screen
#
# This function displays the login screen with appropriate error message
#
####################################################
sub login_screen {
   my $err_msg = shift;
   my $html_txt;
   $html_txt = qq{
      <b>Login Screen</b><br>
	  <font color="red"><b>$err_msg</b></font>
	  $form_header
	  <input type="hidden" name="command" value="verify_login">
	  $table_header
	  <tr><td>Login Name:</td>
	  <Td><input type="text" name="login_name"></td>
	  </tr>
	  <tr><td>Password:</td>
	  <td><input type="password" name="password"></td>
	  </tr>
	  </table>
	  <input type="submit" value="Login"> <input type="reset">
	  </form>
   };
   return $html_txt;
}

#########################################################
#
#   Function main_menu
#   Parameters:
#     $loginid : login id, to pull data from database.
#   return: HTML text of main screen with Search table and 
#           Draft list which's been assigned to current user
#
#########################################################
sub main_menu {
   my $loginid = shift;
   unless (my_defined($loginid)) {
      if (my_defined($q->param("loginid"))) {
	     $loginid = $q->param("loginid");
	  } else {
         return login_screen("Page Expired... Please login");
	  }
   }
   my $html_txt = "";
   my $search_html = search_html($loginid);
   $html_txt .= qq{<CENTER>$search_html</CENTER>};
   my $count = db_select("select count(*) from id_internal where job_owner = $loginid");
   if ($count < 1) {
      $html_txt .= qq {<h3>No Document Assigned currently</h3>};
   } else {
   $html_txt .= qq {<h3>Currently Assigned Document</h3>};
   my $sqlStr;
   if ($db_mode == $MYSQL) {
   $sqlStr = qq{ 
select state.id_document_tag, state.status_date,state.event_date,
state.job_owner, state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,1
from id_internal state
left outer join internet_drafts id on state.id_document_tag = id.id_document_tag
where state.job_owner = $loginid
   AND state.primary_flag = 1
   order by state.cur_state, state.cur_sub_state_id, id.filename
   };
   } else {
      return "ERROR\n";
   }
   #return $sqlStr;
   my @docList = db_select_multiple($sqlStr);  # Generate a list of data pulled from DB
   $html_txt .= display_all(@docList,$loginid);# Generate a HTML text to display the list
   }
   
   return $html_txt;
}

#########################################################
#
#   Function : search_html
#   Parameters:
#      $loginid - loing id of current user
#      $ballot_id - ballot_id, optional
#      $add_sub_flag - To indicate adding sub action, optional
#   return : HTML text to display search table
#
########################################################
sub search_html {
   my $loginid = shift;
   my $ballot_id = shift;
   my $add_sub_flag = shift;
   my $dTag = shift;
   my $button_str;
   my $msg_str = "";
   
   my $default_job_owner = $q->param("search_job_owner");
   my $default_group_acronym = $q->param("search_group_acronym");
   my $default_area_acronym = $q->param("search_area_acronym");
   my $default_filename = $q->param("search_filename");
   my $default_rfcnumber = $q->param("search_rfcnumber");
   my $default_cur_state = $q->param("search_cur_state");
   my $default_sub_state_id = $q->param("sub_state_id");
   my $default_status_id = $q->param("search_status_id");
   my $area_option_str = get_area_option_str($default_area_acronym);
   my $state_option_str = get_option_str("ref_doc_states_new",$default_cur_state);
   my $status_option_str = get_option_str("id_status",$default_status_id);
   my $sub_state_option_str = get_sub_state_select($default_sub_state_id);
   my $max_id = db_select("select max(sub_state_id) from sub_state");
   $max_id++;

   if (defined($add_sub_flag)) {
      $button_str = qq {
	  <input type="hidden" name="ballot_id" value="$ballot_id">
	  <input type="hidden" name="dTag" value="$dTag">
<TD ALIGN="CENTER" colspan="2"><input type="submit" value="PROCEED" name="add_button" onClick="return validate_input();"></td>
};
   } else {
      $button_str = qq {
<TD ALIGN="CENTER"><INPUT TYPE="submit" VALUE="SEARCH" name="search_button">
<input type="button" value="Clear Fields" onClick="clear_fields();">
</TD>
<td ALIGN="CENTER"><input type="submit" value="ADD" name="add_button" onClick="return validate_input();"></td>
};
      $msg_str = qq {<font color="red" size="-1">**Just click 'SEARCH' button to view entire list of active draft**</font>};
   }
   my $ad_option_str = get_ad_option_str($default_job_owner); # HTML SELECT OPTIONS for Area Directors
   my $html_txt = qq {
   <script language="javascript">
   function validate_input () {
          filename = document.search_form.search_filename.value;
	  temp_val = filename.substring(0,1);
	  if (temp_val == " ") {
	     alert("File name cannot start with a space");
	     return false;
	  }

   	  if ( (document.search_form.search_filename.value == "" || document.search_form.search_filename.value == "null")
		&& (document.search_form.search_rfcnumber.value == "" || document.search_form.search_rfcnumber.value == "null") ){
		 alert("Either File Name or RFC Number field must be filled");
		 return false;
	  }
      return true;
   }
   
   function clear_fields() {
      document.search_form.search_job_owner.selectedIndex=0;
      document.search_form.search_status_id.selectedIndex=0;
      document.search_form.search_area_acronym.selectedIndex=0;
      document.search_form.search_cur_state.selectedIndex=0;
      document.search_form.sub_state_id.selectedIndex=$max_id;
	  document.search_form.search_group_acronym.value = "";
	  document.search_form.search_filename.value = "";
	  document.search_form.search_rfcnumber.value = "";
      return true;
   }
   </script>
		$form_header_search
        $table_header
<input type="hidden" name="command" value="search_list">
<input type="hidden" name="loginid" value="$loginid">
<TR BGCOLOR="silver"><Th colspan="2">ID - Search Criteria</Th></TR>
<TR><TD colspan="2">
$table_header
  <TR><TD ALIGN="right">
  <B>Shepherding AD:</B></TD>
  <TD><select name="search_job_owner">
  <option value="0"></option>
  $ad_option_str</select>&nbsp;&nbsp;&nbsp;<B>Group Acronym:</B><INPUT TYPE="text" NAME="search_group_acronym" VALUE="$default_group_acronym" SIZE="6" MAXLENGTH="10">
  &nbsp;&nbsp;&nbsp;
  <B>Status:</B><SELECT NAME="search_status_id"><OPTION VALUE="">All</OPTION>
  $status_option_str</SELECT>
  </TD></TR>
  <TR><TD ALIGN="right"><B>Draft State:</B></TD>
  <TD><SELECT NAME="search_cur_state"><OPTION VALUE="">
  $state_option_str
  </SELECT>&nbsp;&nbsp;&nbsp;
  <b>sub state</b>: $sub_state_option_str
  </TD></TR>
  <TR><TD ALIGN="right"><B>Filename:</B>                          </TD>
  <TD><INPUT TYPE="text" NAME="search_filename" SIZE="15" MAXLENGTH="60" VALUE="$default_filename">
  &nbsp;&nbsp;&nbsp;<B>RFC Number:</B><INPUT TYPE="text" NAME="search_rfcnumber" SIZE="5" MAXLENGTH="10" VALUE="$default_rfcnumber">
  <B>Area Acronym:</B><select name="search_area_acronym">
  <option value=""></option>
  $area_option_str
  </select>

  </TD></TR>
</TABLE>
</TD></TR>
<TR BGCOLOR="silver">$button_str
</TR>
</TABLE>
</FORM>
<HR>
   };
   return $html_txt;
}

##########################################################################
# 
#   Function : search_list
#   Parameters :
#     $q : CGI variables
#   return : HTML text of search resulted list of draft
#
#########################################################################
sub search_list {
   my $q = shift;
   my $loginid = $q->param("loginid");
   my $search_html = search_html($loginid);
   my $html_txt .= qq{<CENTER>$search_html</CENTER>};
   $html_txt .= "<b>Search Result</b><br>\n";
   my @idList;
   my @rfcList;
   if (my_defined($q->param("search_filename"))) {
      $_ = $q->param("search_filename");
	  s/-\d\d.txt//;
	  $q->param(search_filename => $_);
   }
   if (my_defined($q->param("search_group_acronym"))) {
      my $group_acronym = lc($q->param("search_group_acronym"));
      $group_acronym = db_quote($group_acronym);
	  my $gID = db_select("select acronym_id from acronym where acronym = $group_acronym");
	  unless ($gID) {
	     return "<h3>Fatal Error: Invalid WG $group_acronym</h3>";
      }
   }

   my @docList;
    
   if (my_defined($q->param("search_filename"))) {  # Searching ID
      $sqlStr = process_id ($q);
	  #return $sqlStr; 
	  @docList = db_select_multiple($sqlStr);
   } elsif (my_defined($q->param("search_rfcnumber"))) {  # Searching RFC
      $sqlStr = process_rfc ($q);
	  #return $sqlStr; 
	  @docList = db_select_multiple($sqlStr);
   } else {   #searching both ID and RFC
      if ( my_defined($q->param("search_group_acronym")) or my_defined($q->param("search_status_id")) or my_defined($q->param("search_area_acronym")) ) {  
         $sqlStr = process_id ($q);
	     #return $sqlStr; 
	     my @idList = db_select_multiple($sqlStr);
         $sqlStr = process_rfc ($q);
	     #return $sqlStr; 
	     my @rfcList = db_select_multiple($sqlStr);
         #Combine IDs and RFCs result
         push @docList, @idList;
         push @docList, @rfcList;
	  } else {
	    $sqlStr = process_id_rfc($q);
		#return $sqlStr;
		@docList = db_select_multiple($sqlStr);
	  }
   }   
   $html_txt .= display_all(@docList,$loginid);
   return $html_txt;
}

#############################################################
#
#   Function process_id
#   parameters :
#     $q : CGI variables
#   return : SQL statement which performs search on IDs

#############################################################
sub process_id {
   my $q = shift;
   my $sqlStr = qq{
   select state.id_document_tag, state.status_date,state.event_date,state.job_owner,
   state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,id.filename
   from id_internal state, internet_drafts id};
   my $where_clause = qq {
   where id.id_document_tag = state.id_document_tag
   AND state.rfc_flag = 0
   };
   if (my_defined($q->param("search_filename"))) {
      my $filename = "%";
	  $filename .= rm_hd(rm_tr($q->param("search_filename")));
	  $filename .= "%";
      $filename = db_quote($filename);
	  $where_clause .= "AND id.filename like $filename and state.rfc_flag = 0\n";
   }
   if (my_defined($q->param("search_group_acronym"))) {
      my $group_acronym = lc($q->param("search_group_acronym"));
      $group_acronym = db_quote($group_acronym);
	  my $gID = db_select("select acronym_id from acronym where acronym = $group_acronym");
	  $where_clause .= "AND id.group_acronym_id = $gID\n";
   }
   if (my_defined($q->param("search_assigned_to")) and substr($q->param("search_assigned_to"),0,1) ne "-") {
	  my $assigned_to .= db_quote($q->param("search_assigned_to"));
	  $where_clause .= "AND state.assigned_to = $assigned_to\n";
   }
   if (my_defined($q->param("search_cur_state"))) {
	  my $cur_state .= $q->param("search_cur_state");
	  $where_clause .= "AND state.cur_state = $cur_state\n";
          if (my_defined($q->param("sub_state_id"))) {
             my $max_id = db_select("select max(sub_state_id) from sub_state");
             my $sub_state_id .= $q->param("sub_state_id");
             if ($sub_state_id <= $max_id) {
                $where_clause .= "AND state.cur_sub_state_id = $sub_state_id\n";
             }
          }
   }

   if (my_defined($q->param("search_status_id"))) {
	  my $status_id .= $q->param("search_status_id");
	  $where_clause .= "AND id.status_id = $status_id\n";
   }
   if ($q->param("search_job_owner") > 0) {
      my $job_owner = $q->param("search_job_owner");
	  $where_clause .= "AND state.job_owner = $job_owner\n";
   }
   if (my_defined($q->param("search_area_acronym"))) {
      my $area_acronym_id = $q->param("search_area_acronym");
	  my $group_id_set = "";
	  my @groupList = db_select_multiple("select group_acronym_id from area_group where area_acronym_id = $area_acronym_id");
	  my @group_id_set;
	  for $array_ref (@groupList) {
	     my ($val) = @$array_ref;
		 push @group_id_set,$val;
	  }
	  $group_id_set = join ",",@group_id_set;
	  $where_clause .= qq { AND ((id.group_acronym_id = 1027 AND state.area_acronym_id = $area_acronym_id) OR 
	  (id.group_acronym_id <> 1027 AND id.group_acronym_id in ($group_id_set))) 
	  };
   }
   $sqlStr .= $where_clause;
   $sqlStr .= "\n order by state.cur_state, state.cur_sub_state_id,id.filename\n";
   return $sqlStr;
}


sub process_id_rfc {
   my $q = shift;
   my $sqlStr;
   my $where_clause;
   if ($db_mode == $MYSQL) {
      $sqlStr = qq{
      select state.id_document_tag, state.status_date,state.event_date,state.job_owner,
      state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,1,id.filename
      from id_internal state left outer join internet_drafts id on id.id_document_tag = state.id_document_tag};
      $where_clause = qq {
      where state.primary_flag = 1 
      };
   } else {
      $sqlStr = qq{
      select state.id_document_tag, state.status_date,state.event_date,state.job_owner,
      state.cur_state,state.assigned_to,state.rfc_flag,state.ballot_id,1,id.filename
      from id_internal state, outer internet_drafts id};
      $where_clause = qq {
      where id.id_document_tag = state.id_document_tag
      AND state.primary_flag = 1
      };
   }
   if (my_defined($q->param("search_filename"))) {
      my $filename = "%";
	  $filename .= rm_hd(rm_tr($q->param("search_filename")));
	  $filename .= "%";
      $filename = db_quote($filename);
	  $where_clause .= "AND id.filename like $filename and state.rfc_flag = 0\n";
   }
   if (my_defined($q->param("search_rfcnumber"))) {
	     $_ = $q->param("search_rfcnumber");
  	     s/(\D+)(\d+)(\D+)/$2/;
		 my $rfc_number = $_;
         $where_clause .= "AND state.id_document_tag = $rfc_number and state.rfc_flag = 1\n";
   }
   if (my_defined($q->param("search_assigned_to")) and substr($q->param("search_assigned_to"),0,1) ne "-") {
	  my $assigned_to .= db_quote($q->param("search_assigned_to"));
	  $where_clause .= "AND state.assigned_to = $assigned_to\n";
   }
   if (my_defined($q->param("search_cur_state"))) {
	  my $cur_state .= $q->param("search_cur_state");
	  $where_clause .= "AND state.cur_state = $cur_state\n";
   
          if (my_defined($q->param("sub_state_id"))) {
             my $max_id = db_select("select max(sub_state_id) from sub_state");
             my $sub_state_id .= $q->param("sub_state_id");
             if ($sub_state_id <= $max_id) {
                $where_clause .= "AND state.cur_sub_state_id = $sub_state_id\n";
             }
          }
   }

   if (my_defined($q->param("search_status_id"))) {
	  my $status_id .= $q->param("search_status_id");
	  $where_clause .= "AND id.status_id = $status_id\n";
	  if ($status_id == 2) {
	     $where_clause .= "AND state.rfc_flag = 0\n";
      }
   }
   if ($q->param("search_job_owner") > 0) {
      my $job_owner = $q->param("search_job_owner");
	  $where_clause .= "AND state.job_owner = $job_owner\n";
   }
   $sqlStr .= $where_clause;
   $sqlStr .= "\n order by state.cur_state, state.cur_sub_state_id,id.filename\n";
   return $sqlStr;
}




##################################################
#
#   Function : process_rfc
#   Parameters :
#      $q : CGI variables
#   return : SQL statement which will perform search on RFCs
#
##################################################
sub process_rfc {
   my $q = shift;
   my $dName = uc($q->param("search_id_document_name"));
   my $gAcronym = $q->param("search_group_acronym");
   my $filename = $q->param("search_rfcnumber");
   my $sqlStr = qq{
   select state.id_document_tag, state.status_date,state.event_date,state.job_owner,
   state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,rfc.rfc_number
   from id_internal state, rfcs rfc
   };
   my $where_clause = qq {
   where rfc.rfc_number = state.id_document_tag
   AND state.rfc_flag = 1
   };
      if (my_defined($dName)) {
         $dName = rm_hd(rm_tr($dName));
	 $dName .= "%";
         $dName = db_quote($dName);
         $where_clause .= "AND rfc_name_key like $dName\n";
      }
      if (my_defined($gAcronym)) {
         $gAcronym = db_quote($gAcronym);
         $where_clause .= "AND group_acronym = $gAcronym\n";
      }
      if (my_defined($filename)) {
	     $_ = $filename;
  	     s/(\D+)(\d+)(\D+)/$2/;
		 $rfc_number = $_;
         $where_clause .= "AND rfc_number = $rfc_number\n";
      }
   if (my_defined($q->param("search_assigned_to")) and substr($q->param("search_assigned_to"),0,1) ne "-") {
	  my $assigned_to .= db_quote($q->param("search_assigned_to"));
	  $where_clause .= "AND state.assigned_to = $assigned_to\n";
   }
   if (my_defined($q->param("search_cur_state"))) {
	  my $cur_state .= $q->param("search_cur_state");
	  $where_clause .= "AND state.cur_state = $cur_state\n";
          if (my_defined($q->param("sub_state_id"))) {
             my $max_id = db_select("select max(sub_state_id) from sub_state");
             my $sub_state_id .= $q->param("sub_state_id");
             if ($sub_state_id <= $max_id) {
                $where_clause .= "AND state.cur_sub_state_id = $sub_state_id\n";
             }
          }
   }


   if ($q->param("search_job_owner") > 0) {
      my $job_owner = $q->param("search_job_owner");
	  $where_clause .= "AND state.job_owner = $job_owner\n";
   }
   if (my_defined($q->param("search_status_id"))) {
	  my $status_id .= $q->param("search_status_id");
	  if ($status_id == 2) {
	     $where_clause .= "AND rfc.rfc_number = 999999\n";
      }
   }
   if (my_defined($q->param("search_area_acronym"))) {
      my $area_acronym_id = $q->param("search_area_acronym");
	  $where_clause .= qq {AND  state.area_acronym_id = $area_acronym_id
	  };
   }
   $sqlStr .= $where_clause;
   $sqlStr .= "\n order by state.cur_state, state.cur_sub_state_id, rfc.rfc_number\n";
   return $sqlStr;
}

###################################################
#
#   Function : process_add_id
#   Parameters:
#     $q : CGI variables
#   return : SQL statement 
#
##################################################
sub process_add_id {
   my $q = shift;
   my $dTag = $q->param("dTag");
   my $sqlStr;
   $dName = uc($q->param("search_id_document_name"));
   $gAcronym = $q->param("search_group_acronym");
   $filename = $q->param("search_filename");
   $StatusId = $q->param("search_status_id");
   my $ballot_id = $q->param("ballot_id");
   unless (my_defined($ballot_id)) {
      $ballot_id = 0;
   }
   
   my $whereClause = "";
   if (my_defined($dTag)) {
      $whereClause .= "AND a.id_document_tag <> $dTag\n";
   }
   if (my_defined($StatusId)) {
      $whereClause .= "AND status_id = $StatusId\n";
   }
      if (my_defined($dName)) {
	     $dName .= "%";
         $dName = db_quote($dName);
         $whereClause .= "AND id_document_key like $dName\n";
      }
      if (my_defined($gAcronym)) {
         $gAcronym = db_quote($gAcronym);
         $sqlStr = "select acronym_id from acronym where acronym = $gAcronym";
	     my $gID = db_select($sqlStr);
         $whereClause .= "AND group_acronym_id = $gID\n";
      }
      if (my_defined($filename)) {
	     $filename = "%${filename}%";
         $filename = db_quote($filename);
         $whereClause .= "AND filename like $filename\n";
      }
	  if ($db_mode == $INFORMIX) {
         $sqlStr = qq{
         select a.id_document_tag,filename,b.id_document_tag
         from internet_drafts a, outer id_internal b
		 Where a.id_document_tag = b.id_document_tag AND b.ballot_id <> $ballot_id
         $whereClause
         };
      } else {
         $sqlStr = qq{
         select a.id_document_tag,filename,b.id_document_tag
         from internet_drafts a left outer join id_internal b 
		 on (a.id_document_tag = b.id_document_tag AND b.ballot_id <> $ballot_id)
		 Where 0 = 0
         $whereClause
         };
	  }

   return $sqlStr;
}

######################################
#
#   Function : process_add_rfc
#   Parameters :
#      $q : CGI variables
#   return : SQL statement that search on RFCs
#
######################################
sub process_add_rfc {
   my $q = shift;
   my $dTag = $q->param("dTag");
   my $sqlStr;
   $dName = uc($q->param("search_id_document_name"));
   $gAcronym = $q->param("search_group_acronym");
   $filename = $q->param("search_rfcnumber");
   my $ballot_id = $q->param("ballot_id");
   unless (my_defined($ballot_id)) {
      $ballot_id = 0;
   }
   
   my $whereClause = "";
   if (my_defined($dTag)) {
      $whereClause .= "AND a.rfc_number <> $dTag\n";
   }
      if (my_defined($dName)) {
	     $dName .= "%";
         $dName = db_quote($dName);
         $whereClause .= "AND rfc_name_key like $dName\n";
      }
      if (my_defined($gAcronym)) {
         $gAcronym = db_quote($gAcronym);
         $whereClause .= "AND group_acronym = $gAcronym\n";
      }
      if (my_defined($filename)) {
	     $_ = $filename;
  	     s/(\D+)(\d+)(\D+)/$2/;
		 $rfc_number = $_;
         $whereClause .= "AND rfc_number = $rfc_number\n";
      }
	  if ($db_mode == $INFORMIX) {
      $sqlStr = qq{
      select rfc_number,rfc_name,b.id_document_tag
      from rfcs a, outer id_internal b
	  WHERE a.rfc_number = b.id_document_tag AND b.ballot_id <> $ballot_id
      $whereClause
      };
      } else {
         $sqlStr = qq{
         select rfc_number,rfc_name,b.id_document_tag
         from rfcs a left outer join id_internal b 
		 on (a.rfc_number = b.id_document_tag AND b.ballot_id <> $ballot_id)
		 Where 0 = 0
         $whereClause
         };
	  }
   
   return $sqlStr;
}

##########################################################
#
#   Function : add_id_search
#   Parameters :
#     $q : CGI variables
#   return : HTML text: List of draft if search result is more than one.
#                       View Draft page of search result if only one result
#
#########################################################
sub add_id_search {
   my $q = shift;
   my $loginid = $q->param("loginid");
   my $html_txt = "Search Result";
   if (my_defined($q->param("search_group_acronym"))) {
      my $group_acronym = lc($q->param("search_group_acronym"));
      $group_acronym = db_quote($group_acronym);
	  my $gID = db_select("select acronym_id from acronym where acronym = $group_acronym");
	  unless ($gID) {
	     return "<h3>Fatal Error: Invalid WG $group_acronym</h3>";
      }
   }
   if (my_defined($q->param("search_filename"))) {  # Search on IDs
      $_ = $q->param("search_filename");
	  s/-\d\d.txt//;
          $_ = rm_tr($_);
	  $q->param(search_filename => $_);
      $sqlStr = process_add_id ($q);
	  $rfc_flag = 0;
   } else {					    # Search on RFCs
      $sqlStr = process_add_rfc ($q);
	  $rfc_flag = 1;
   }
   my $ballot_id = $q->param("ballot_id");
   my $add_str = "Add";
   my $add_name = "Add";
   unless (my_defined($ballot_id)) { # Add New Ballot
      $ballot_id = 0;
   } else { 			     # Add an action to existing ballot
      $add_str = "Add to Action";
	  $add_name = "add_existing";
   }
   
#return $sqlStr;

   $html_txt = qq{$table_header
   <tr><th>File Name</th></tr>
   };
   my @list = db_select_multiple($sqlStr);
   for $array_ref (@list) {
     my ($dTag,$document_name,$internal_exist) = @$array_ref;
	 unless (defined($internal_exist) and $ballot_id==0) {
        if ($#list == 0) {
	       $q->param(dTag => $dTag);
		   $q->param(rfc_flag => $rfc_flag);
		   $q->param(ballot_id => $ballot_id);
		   $q->param(dName => $document_name);
#		   if ($cnt > 0) {
#		      $q->param(add_existing => $ballot_id);
#		   }
		   if ($internal_exist > 0) {
		      $q->param(add_existing => $ballot_id);
		   }
           return add_id_confirm($q);
        }
		unless ($internal_exist) {
		   $add_name = "add_new";
		} else {
		   $add_name = "add_existing";
		}
	    $button_str = qq{<input type="submit" value="$add_str" name="$add_name">};
	 } else {
	    $button_str = "<font color=\"red\">EXISTS</font>";
	 }
     $html_txt .= qq{
		$form_header
		<input type="hidden" name="command" value="add_id_confirm">
		<input type="hidden" name="dTag" value="$dTag">
		<input type="hidden" name="rfc_flag" value="$rfc_flag">
		<input type="hidden" name="dName" value="$document_name">
		<input type="hidden" name="loginid" value="$loginid">
		<input type="hidden" name="ballot_id" value="$ballot_id">
		<tr><Td>$document_name</td>
		<td>${button_str}</td></tr>
		</form>
      };
   } #for
   $html_txt .= "</table>\n";
   
   return $html_txt;
}

#################################################
#
#   Function : add_existing
#   Parameters :
#      $q : CGI variables
#   return : HTML text to display view draft page after change the ballot id of 
#            existing ballot
#
#################################################
sub add_existing {
   my $q = shift;
   my $ballot_id = $q->param("ballot_id");
   my $dTag = $q->param("dTag");
   my $sqlStr = qq {update id_internal
   set ballot_id = $ballot_id,
   primary_flag = 0
   where id_document_tag = $dTag
   };
#   return $sqlStr;
   return $error_msg unless (db_update($sqlStr));
   return view_id($q);
}

#####################################################
#
#   Function : add_id_confirm
#   Parameters :
#     $q : CGI variables
#   return : HTML text to display form to enter additional information to be inserted as a ballot
#
#####################################################
sub add_id_confirm {
   my $q = shift;
   if (defined($q->param("add_existing"))) { # ballot already existed, No additional information needed
      return add_existing($q);
   }
   my $rfc_flag = $q->param("rfc_flag");
   my $dTag = $q->param("dTag");
   my $dName = $q->param("dName");
   my $loginid = $q->param("loginid");
   my $ballot_id = $q->param("ballot_id");
   my $html_txt = "<b>Add ID - $dName</b>";
   my $job_owner = $loginid;
   my $ad_option_str = get_ad_option_str($job_owner);
   my $state_option_str = get_option_str("ref_doc_states_new");
   my $area_acronym_str = "";
   my $area_option_str = get_area_option_str();
   my $sub_state_select_str = get_sub_state_select(-2);
   my $gID = db_select("select group_acronym_id from internet_drafts where id_document_tag = $dTag");
   my $wg_mode = 0;
   if ($gID == 1027) {
      $area_acronym_str = qq {
	  <tr><td>Area Acronym:</td>
	  <td><select name="area_acronym_id">
	  <option value=""></option>
	  $area_option_str
	  </select></td>
	  </tr>
	  };
	  $wg_mode = 1;
   }
   my $length_validate = "";
   my $length_validate_form = "";
   if ($db_mode != $MYSQL) {
      $length_validate = qq {
	<SCRIPT Language="JavaScript">   
	function validate_fields (str) {
	  if (str.length > 255) {
	     alert ("Comment field can not exceed 255 in length");
		 document.search_form.comment.focus();
		 return false;
	  }
	  return true;
	}
	</script>
	  };
	  $length_validate_form = qq { onClick="return validate_fields(document.search_form.comment.value);"};
   }
   
   $html_txt .= qq{
   $length_validate
   $table_header
   $form_header_search
   <input type="hidden" name="command" value="add_id_db">
   <input type="hidden" name="rfc_flag" value="$rfc_flag">
   <input type="hidden" name="dTag" value="$dTag">
   <input type="hidden" name="loginid" value="$loginid">
   <input type="hidden" name="ballot_id" value="$ballot_id">
   <input type="hidden" name="wg_mode" value="$wg_mode">
   $area_acronym_str
   <tr><td>Current State: </td>
   <td>
   <select name="current_state">
   $state_option_str
   </select>
   $sub_state_select_str
   </td></tr>
   <tr>
   <td>Shepherding AD:</td>
   <td><select name="job_owner">
   $ad_option_str
   </select></td>
   </tr>
   <tr>
   <td>Due Date:<br>(YYYY-MM-DD)</td>
   <td><input type="text" name="status_date"></td>
   </tr>
   <tr>
   <td>Comment:</td>
   <td><textarea name="comment" rows="3" cols="75" wrap="virtual"></textarea> <input type="checkbox" name="public_flag"> Public</td>
   </tr>
   <tr>
   <td colspan="2"><input type="submit" value="SUBMIT" $length_validate_form></td>
   </tr>
   </form>
   </table>
   };
   return $html_txt;
}

#######################################################
#
#   Function : get_ad_option_str
#   Parameters:
#      $id - record id
#   return : HTML text to display options of Area Directors
#
#######################################################
sub get_ad_option_str {
   my $id = shift;
   my $ad_option_str = "";
   $sqlStr = qq{
select id, login_name from iesg_login where user_level = 1 or user_level = 3
};
   my @list = db_select_multiple($sqlStr);
   for $array_ref (@list) {
     my ($pID,$login_name) = rm_tr(@$array_ref);
	 my $selected = "";
	 if (defined($id)) {
	    if ($pID == $id) {
	       $selected = "selected";
        }
	 }
     $ad_option_str .= qq{
      <option value="$pID" $selected>$login_name</option>
     };
   }
   return $ad_option_str;
}

############################################
#
#   Function : add_id_db
#   Parameters :
#      $q - CGI variables
#   return : HTML text to display main screen
#
#   This function add new ballot and comment to database
#
###########################################
sub add_id_db {
   my $q = shift;
   my $id_document_tag = $q->param("dTag");
   my $ballot_id = $q->param("ballot_id");
   my $primary_flag = 0;
   my $area_acronym_id = $q->param("area_acronym_id");
   my $cur_state = $q->param("current_state");
   my $rfc_flag = $q->param("rfc_flag");
   my $comment = $q->param("comment");
   my $job_owner= $q->param("job_owner");
   my $loginid = $q->param("loginid");
   my $public_flag = $q->param("public_flag");
   my $mark_by = $loginid;
   my $table_name = "id_internal";
   my $token_name = db_quote(get_mark_by($job_owner));
   my $wg_mode = $q->param("wg_mode");
   my $sub_state_id = $q->param("sub_state_id");
   return "<h3>Fatal Error: You didn't set Area Acronym</h3>" if ($wg_mode and !my_defined($area_acronym_id));
   $sqlStr = qq {
   select email_address from email_addresses e,iesg_login i
   where i.id = $job_owner
   AND i.person_or_org_tag = e.person_or_org_tag
   AND e.email_priority = 1
   };
   my $token_email = db_quote(rm_tr(db_select($sqlStr)));
   my $version = db_select("select revision from internet_drafts where id_document_tag = $id_document_tag");
   $version = db_quote($version);
   if ($rfc_flag) {
      $table_name = "id_internal";
   }
   my $status_date = db_quote(convert_date($q->param("status_date"),$CONVERT_SEED));
   my $assigned_to = $q->param("assigned_to");
   if (substr($assigned_to,0,1) eq "-") {
      $assigned_to = "Unassigned";
   }
   $assigned_to = db_quote($assigned_to);
   if ($ballot_id == 0) {  # if new action
      $ballot_id = db_select("select max(ballot_id) from id_internal");
	  $primary_flag = 1;
      unless (my_defined($ballot_id)) {
         $ballot_id = 1;
      } else {
         $ballot_id++;
      }
   }
   my $group_flag = db_select("select equiv_group_flag from ref_doc_states_new where document_state_id = $cur_state");
   unless (my_defined($area_acronym_id)) {
      $sqlStr = qq { select a.acronym_id from acronym a, area_group c, internet_drafts i
      where i.id_document_tag = $id_document_tag and i.group_acronym_id = c.group_acronym_id and
      c.area_acronym_id = a.acronym_id
      };
      $area_acronym_id = db_select($sqlStr);
   }
  # my ($first_name,$last_name) = db_select("select first_name, last_name from iesg_login where id = $job_owner");
  # my $token_name = rm_tr($first_name) . " ";
  # $token_name .= rm_tr($last_name);
   
  # my $token_email = rm_tr(db_select("select e.email_address from email_addresses e, iesg_login i where i.id = $job_owner and i.person_or_org_tag = e.person_or_org_tag"));
  # ($token_name,$token_email) = db_quote($token_name,$token_email);


   $sqlStr = qq {
   insert into $table_name
   (id_document_tag,rfc_flag,group_flag,cur_state,prev_state,assigned_to,status_date,event_date,mark_by,job_owner,ref_history,ballot_id,primary_flag,area_acronym_id,token_name,email_display,token_email,cur_sub_state_id,prev_sub_state_id)
   values ($id_document_tag,$rfc_flag,$group_flag,$cur_state,$cur_state,$assigned_to,$status_date,$CURRENT_DATE,$mark_by,$job_owner,999999,$ballot_id,$primary_flag,$area_acronym_id,$token_name,$token_name,$token_email,$sub_state_id,0)
   };
   #return $sqlStr;
   return $error_msg unless (db_update($sqlStr));
   
   ################### Update Comment Log ####################
   my $new_mark_by = get_mark_by($loginid);
   my $log_txt = "Draft Added by $new_mark_by";
   $log_txt = db_quote($log_txt);
   #return update_comment_log($loginid,$id_document_tag,$version,$mark_by,$cur_state,$cur_state,$comment,$log_txt,$public_flag);
   
   unless (update_comment_log($loginid,$id_document_tag,$version,$mark_by,$cur_state,$cur_state,$comment,$log_txt,$public_flag)) {
      db_update("delete from id_internal where id_document_tag = $id_document_tag");
	  return "$error_msg";
   }   

   my $html_txt = main_menu($loginid);
   return $html_txt;
}

#############################################################
#
# Function : update_commment_log
# Parameters:
#   $loginid - login id of current user
#   $document_id - id of current draft that this comment is belong to
#   $version - version of current docuement
#   $mark_by - Marked by
#   $cur_state - Current state of draft
#   $prev_state - Previous state of draft
#   $comment - Text of comment
#   $log_txt - Text of comment that indicates the state changes
#   $public_flag - Indicate that the current comment is private or public
# return : 0 if updating database failed
#          1 if successful 
#
#############################################################
sub update_comment_log {
   my ($loginid,$document_id,$version,$mark_by,$cur_state,$prev_state,$comment,$log_txt,$public_flag,$id_status_log) = @_;
   
   ##################### Add log to indicate state changed ######################
   my $cur_time = db_quote(get_current_time());

   if (my_defined($log_txt) and is_unique_comment($loginid,$log_txt,$document_id)) {
  # if (my_defined($log_txt)) {
      $sqlStr = qq {
       insert into document_comments
      (document_id,public_flag,comment_date,comment_time,version,comment_text,created_by,result_state,origin_state)
   	   values
	   ($document_id,1,$CURRENT_DATE,$cur_time,$version,$log_txt,$mark_by,$cur_state,$prev_state)
        };
        #return $sqlStr;
        return 0 unless (db_update($sqlStr));
   }
   ##################### Add log to indicate Intended_status changed ######################
#   if (my_defined($id_status_log) and is_unique_comment($loginid,$id_status_log,$document_id)) {
   if (my_defined($id_status_log)) {
#      $id_status_log = db_quote($id_status_log);
      $id_status_log = format_textarea($id_status_log);
      $sqlStr = qq {
       insert into document_comments
      (document_id,public_flag,comment_date,comment_time,version,comment_text,created_by,result_state,origin_state)
   	   values
	   ($document_id,1,$CURRENT_DATE,$cur_time,$version,$id_status_log,$mark_by,$cur_state,$prev_state)
        };
        #return $sqlStr;
        return 0 unless (db_update($sqlStr));
   }
   #################### Add Comment if any #############################
   if (my_defined($comment)) {
     $comment =~ s/</&lt;/g;
     $comment =~ s/>/&gt;/g;

      $comment = db_quote($comment);
	  #return $comment;
	  unless (is_unique_comment($loginid,$comment,$document_id)) {
	     return 0;
	  }
	  if ($public_flag eq "on") {
	     $public_flag_val = 1;
	  } else {
	     $public_flag_val = 0;
	  }
	  
      $sqlStr = qq {
	  insert into document_comments
	  (document_id,public_flag,comment_date,comment_time,version,comment_text,created_by,result_state,origin_state)
	  values
	  ($document_id,$public_flag_val,$CURRENT_DATE,$cur_time,$version,$comment,$mark_by,$cur_state,$cur_state)
	  };
	  #return $sqlStr;
	  
      return 0 unless (db_update($sqlStr));
   }
   return 1;
}


################################################################
#
# Function : get_option_str
# Parameters:
#   $table_name : Table where the data pulled from
#   $selected_id : currently selected record id
# return : HTML text of options of SELECT tag
#
################################################################
sub get_option_str {
   my $table_name = shift;
   my $selected_id = shift;
   $selected_id = 0 unless my_defined($selected_id);
   $option_str = "";
   $sqlStr = qq{
   select * from $table_name order by 1
   };
   my @list = db_select_multiple($sqlStr);
   for $array_ref (@list) {
     my ($id,$val) = @$array_ref;
      if (defined($selected_id) and $selected_id == $id) {
         $selected = "selected";
      } else {
         $selected = "";
      }
      $option_str .= qq{
      <option value="$id" $selected>$val</option>
      };
   }
   return $option_str;
}

############################################################
#
# Function : get_mark_by
# Parameters:
#   $loginid - login id of current user
# return : string of first name and last name pulled from iesg_login table
#
############################################################
sub get_mark_by {
   my $loginid = shift;
   my $new_mark_by = rm_tr(db_select("select login_name from iesg_login where id = $loginid"));
   return $new_mark_by;
}


############################################################
#
# Function : detach_ballot
# Parameters:
#   $q - CGI variables
# return : HTML text to display view draft page
#
#   This function separates the current draft from it's action group
# 
############################################################
sub detach_ballot {
   my $q = shift;
   my $dTag = $q->param("dTag");
   my $new_ballot = db_select("select max(ballot_id) from id_internal");
   $new_ballot++;      # Get a new ballot id
   my $sqlStr = qq {
   update id_internal
   set ballot_id = $new_ballot,
       primary_flag = 1,
	   event_date = $CURRENT_DATE
   where id_document_tag = $dTag
   };
   return $error_msg unless (db_update($sqlStr));
   return view_id($q);
}


############################################################
#
# Function : view_id
# Parameters:
#   $q : CGI variables
# return : HTML text to view draft
#
# Many main feature of this application can be performed within this page.
# One can change state of draft, update any information, view action group
# if existed, add a draft to current action group, detach current draft from its
# action group, add a comment about current draft, and view any previous comment.
#
############################################################
sub view_id {
   my $q = shift;
   my $dTag = $q->param("dTag");
   my $rfc_flag = $q->param("rfc_flag");
   my $loginid = $q->param("loginid");
   my $from_field = "";
   if ($rfc_flag == 1) {
	   $sqlStr = qq{
	   select rfc.rfc_name, rfc.online_version, state.status_date,state.note,state.agenda,state.event_date,state.area_acronym_id,
	   state.cur_state,state.prev_state,state.cur_sub_state_id,state.prev_sub_state_id,state.group_flag,state.assigned_to,state.job_owner,state.ballot_id, rfc.intended_status_id
	   
	   from rfcs rfc ,
	   id_internal state
	   where rfc.rfc_number = state.id_document_tag
	   AND state.id_document_tag = $dTag
	   AND state.rfc_flag = 1
	   };

   } else {
	   $sqlStr = qq{
	   select id.filename, id.revision, state.status_date,state.note,state.agenda,state.event_date,state.area_acronym_id,
	   state.cur_state,state.prev_state,state.cur_sub_state_id,state.prev_sub_state_id,state.group_flag,state.assigned_to,state.job_owner,state.ballot_id,id.intended_status_id
	   from internet_drafts id,
	   id_internal state
	   where id.id_document_tag = state.id_document_tag
	   AND state.id_document_tag = $dTag
	   AND state.rfc_flag = 0
	   };
   }
   #return $sqlStr;
   my ($filename,$revision,$status_date,$note,$agenda,$event_date,$area_acronym_id,$cur_state,$prev_state,$cur_sub_state_id,$prev_sub_state_id,$group_flag,$assigned_to,$job_owner,$ballot_id,$status_id) = rm_tr(db_select($sqlStr));
   my $id_status_option_str = get_id_status_option_str($status_id,$rfc_flag); 
   if ($rfc_flag == 1) {
      $revision = "RFC";
   }
   $note = unformat_textarea($note);
   my $checked = "";
   $checked = "checked" if ($agenda == 1);
   my $ballot_count = db_select("select count(*) from id_internal where ballot_id = $ballot_id");
   my $ad_option_str = get_ad_option_str($job_owner); #Get Area Directors List
   my $action_html = "";
   my $action_list_html = "";
   my $detach_button = "";
   if ($ballot_count > 1) { # If an action group existed
      # Create Detach Button
      $detach_button = qq {$form_header  
      <input type="hidden" name="command" value="detach_ballot">
      <input type="hidden" name="loginid" value="$loginid">
	  <input type="hidden" name="dTag" value="$dTag">
	  <input type="hidden" name="rfc_flag" value="$rfc_flag">
	  <td>
	  <input type="submit" value="Separate from Action">
     </td></form>
	  };
      # Create a short cut to action list
      $action_list_html = "<div align=\"right\"><a href=\"#action\">Action List</a></div>";
      # Create an action list
      $action_html .= "<a name=\"action\"></a><table border=\"1\" bgcolor=\"black\"> <tr><td><font color=\"white\"><h3>Actions</h3></font>\n";
      if ($db_mode == $MYSQL) {
         $from_field = qq {from id_internal state left outer join internet_drafts id
	 on state.id_document_tag = id.id_document_tag
	 left outer join rfcs rfc on state.id_document_tag = rfc.rfc_number};
         $outer_where = "";
      } 
      my $sqlStr = qq{
      select state.id_document_tag, state.status_date,state.event_date,state.job_owner,
      state.cur_state,state.cur_sub_state_id,state.assigned_to,state.rfc_flag,state.ballot_id,1,id.filename
      $from_field
      where state.ballot_id = $ballot_id
      AND state.primary_flag = 1
      $outer_where
      };
      #return $sqlStr;
	  my @action_list = db_select_multiple($sqlStr);
	  $action_html .= display_all(@action_list,$loginid);
	  $action_html .= "</td></tr></table>";
   }
   # Create Add Sub draft button
   my $add_sub_html = qq {
   $form_header
   <input type="hidden" name="command" value="add_action">
   <input type="hidden" name="loginid" value="$loginid">
   <input type="hidden" name="ballot_id" value="$ballot_id">
   <input type="hidden" name="dTag" value="$dTag">
   <td><input type="submit" value="Add an action (ballot)"></td></form>
	  };
   my $html_txt = "";
   my $prev_state_txt = db_select("select document_state_val from ref_doc_states_new where document_state_id = $prev_state");
   if ($prev_sub_state_id > 0) {
     my $prev_sub_state = get_sub_state($prev_sub_state_id);
     $prev_state_txt .= " -- $prev_sub_state";
   }
   my $cur_state_txt = db_select("select document_state_val from ref_doc_states_new where document_state_id = $cur_state");
   if ($cur_sub_state_id > 0) {
     my $cur_sub_state = get_sub_state($cur_sub_state_id);
     $cur_state_txt .= " -- $cur_sub_state";
   }

   my $next_state_option_str = get_option_str("ref_doc_states_new");
   my $next_state_buttons_str = get_next_state_button_str($cur_state);
   my $sub_state_select_str = get_sub_state_select(-1);
   my $row_color = $fColor;

   
   my $area_acronym_str = "";
   my $area_option_str = get_area_option_str($area_acronym_id);
   my $gID = db_select("select group_acronym_id from internet_drafts where id_document_tag = $dTag");
   if ($gID == 1027) {
      $area_acronym_str = qq {
	  <tr><td>Area Acronym:</td>
	  <td><select name="area_acronym_id">
	  $area_option_str
	  </select></td>
	  </tr>
	  };
   }

   my $ballot_link = "";
   my $ballot_exist = 0;
   my $ballot_name = $filename;
   if ($rfc_flag==1) {
      $ballot_name = "rfc${dTag}";
   }
   if (-e "/usr/local/etc/httpd/htdocs/IESG/EVALUATIONS/${ballot_name}.bal") {
      $ballot_link = "<a href=\"https://www.ietf.org/IESG/EVALUATIONS/${ballot_name}.bal\" TARGET=\"_blank\">[Open Ballot]</a>";
	  $ballot_exist = 1;
   }
   $status_date = convert_date($status_date,1);
   my $length_validate = "";
   my $length_validate_form = "";
   if ($db_mode != $MYSQL) {
      $length_validate = qq {
	<SCRIPT Language="JavaScript">   
	function validate_fields (str) {
	  if (str.length > 255) {
	     alert ("Comment field can not exceed 255 in length");
		 document.f.comment.focus();
		 return false;
	  }
	  return true;
	}
	</script>
	  };
	  $length_validate_form = qq { onClick="return validate_fields(document.f.comment.value);"};
   }
   $html_txt .= qq{
	<SCRIPT Language="JavaScript">   
	function MM_openBrWindow(theURL,winName,features) { //v2.0
	  window.open(theURL,winName,features);
	}
	function MM_closeBrWindow(winName) { //v2.0
	  window.close(winName);
	}
	$length_validate
	</script>

   $table_header
   <tr bgcolor="BEBEBE" align="center"><th colspan="2"><div id="largefont">View Draft</div> $action_list_html</th></tr>
   <form action="$program_name" method="POST" name="f">
   <input type="hidden" name="command" value="update_id">
   <input type="hidden" name="rfc_flag" value="$rfc_flag">
   <input type="hidden" name="dTag" value="$dTag">
   <input type="hidden" name="version" value="$revision">
   <input type="hidden" name="prev_state" value="$prev_state">
   <input type="hidden" name="cur_state" value="$cur_state">
   <input type="hidden" name="cur_sub_state_id" value="$cur_sub_state_id">
   <input type="hidden" name="prev_sub_state_id" value="$prev_sub_state_id">
   <input type="hidden" name="loginid" value="$loginid">
   <input type="hidden" name="old_id_intended_status" value="$status_id">
   <input type="hidden" name="old_status_date" value="$status_date">
   <input type="hidden" name="old_area_acronym_id" value="$area_acronym_id">
   <input type="hidden" name="old_job_owner" value="$job_owner">
   <input type="hidden" name="owner_mode" value="$owner_mode">
   <input type="hidden" name="old_group_flag" value="$group_flag">
   <input type="hidden" name="ballot_exist" value="$ballot_exist">
   <tr bgcolor="white"><td>Draft Name: </td><td>$filename $ballot_link</td></tr>
   <tr bgcolor="white"><td>Version: </td><td>$revision</td></tr>
   <tr bgcolor="white"><td>Intended Status: </td>
   <td>$status_value
   <select name="id_intended_status">
   $id_status_option_str
   </select>
   &nbsp; &nbsp; Agenda? <input type="checkbox" name="agenda" $checked>
   </td></tr>
   $area_acronym_str
   <tr bgcolor="white"><td>Previous State: </td>
   <td>
   $prev_state_txt
   </td></tr>
   <tr><td>Current State: </td>
   <td>
   $cur_state_txt
   </td></tr>
   <tr bgcolor="white"><td>Next State: </td>
   <td>
   <br>
   <select name="next_state">
   <option value="0">---Select Next State</option>
   $next_state_option_str
   </select> with sub state in   
   $sub_state_select_str 
   <a href="https://datatracker.ietf.org/cgi-bin/states_table.cgi" TARGET="_blank"> Show States Table</a>
   <br>
   or<br>
   $next_state_buttons_str
   <br>or<br>   
   <input type="submit" value="Back to Previous State" name="process_prev_button"><br><br>
   </td></tr>
   <tr bgcolor="white">
   <td>Shepherding AD:</td>
   <td>
   <select name="job_owner">
   $ad_option_str
   </select>
   <input type="submit" name="assign_to_me" value="Assign to me">
   </td>
   </tr>
   <tr bgcolor="white">
   <td>Due Date:<br>(YYYY-MM-DD)</td>
   <td><input type="text" name="status_date" value="$status_date">
   </td>
   </tr>
   <tr bgcolor="white"><td>Web Note:</td><td>
   <textarea name="note" rows="3" cols="55" wrap="virtual">$note</textarea>
   </td></tr>
   <tr bgcolor="white"><td>Comment:</td><td>
   <textarea name="comment" rows="10" cols="55" wrap="virtual"></textarea>
   <input type="checkbox" name="public_flag"> Public</td></tr>
   <tr bgcolor="white">
   <td width="140"><input type="submit" value="UPDATE" $length_validate_form><input type="reset" value="RESET"></td></form>
   <td>
   $table_header
   <tr>
   $add_sub_html
   $detach_button
   $form_header
   <input type="hidden" name="command" value="main_menu">
   <input type="hidden" name="loginid" value="$loginid">
   <td><input type="submit" value="Main Menu"></td></form>
   </tr>
   </table>
   </td>
   </tr>
   
   </table>
  
   <h3>Comment Log</h3>
   $table_header
   <tr bgcolor="$fColor"><th>Date</th><th>Version</th><th>Comment</th></tr>
   };
   $sqlStr = qq{
   select id,comment_date,version,comment_text,public_flag,created_by from document_comments
   where document_id = $dTag
   order by 1 desc
   };
   my @commentList = db_select_multiple($sqlStr);
   for $array_ref (@commentList) {
      my ($id,$comment_date,$version,$comment_text,$public_flag,$created_by) = @$array_ref;
	  $comment_date = convert_date($comment_date,1);
          $comment_text = format_textarea($comment_text); 
          $comment_text = reduce_text($comment_text,4);
	  if ($public_flag == 1) {
	     $pre_str = $public_txt;
	  } else {
	     $pre_str = $private_txt;
	  }
	  if ($row_color eq $fColor) {
	     $row_color = $sColor;
	  } else {
	     $row_color = $fColor;
	  }
	  my $button_str = "";
	  if ($created_by == $loginid) {
	     $button_str = qq{
	  $form_header
	  <input type="hidden" name="command" value="toggle_comment">
	  <input type="hidden" name="comment_id" value="$id">
	  <input type="hidden" name="loginid" value="$loginid">
	  <input type="hidden" name="dTag" value="$dTag">
	  <input type="hidden" name="rfc_flag" value="$rfc_flag">
	  <td>
	  <input type="submit" value="Toggle Private/Public">
	  </td>
	  </form>
		 };
	  }
	  $html_txt .= qq {
	  <tr bgcolor="$row_color"><td>$comment_date</td><td align="center">$version</td><td>$pre_str $comment_text</td>
	  <form>
	  <td>
	  <input type="button" value="View Detail" onClick="window.open('${program_name}?command=view_comment&loginid=$loginid&id=$id',null,'height=250,width=500,status=no,toolbar=no,menubar=no,location=no,resizable=yes,scrollbars=yes');">
	  </td>
	  </form>
	  $button_str
	  </tr>
	  };
   }
   $html_txt .= "</table><br><br>\n$action_html\n";
   return $html_txt;
}

###########################################################
#
# Function : toggle_comment
# Parameters :
#   $q - CGI variables
# return: Error message if updating database is failed
#         HTML text of view draft page if successful
#
# This function toggles the private/public flag of comment
#
###########################################################
sub toggle_comment {
   my $q = shift;
   my $comment_id = $q->param("comment_id");
   my $new_public_flag = db_select("select public_flag from document_comments where id=$comment_id");
   if ($new_public_flag == 1) {
     $new_public_flag = 0;
   } else {
     $new_public_flag = 1;
   }
   my $sqlStr = "update document_comments set public_flag = $new_public_flag where id = $comment_id";
   return $error_msg unless (db_update($sqlStr));
   return view_id($q);
}

###########################################################
#
# Function : update_id
# Parameters:
#    $q : CGI variables
# return: Error message if updating databse is failure
#         HTML text of view draft page if successful
#
# This function update any content of record 
#
##########################################################
sub update_id {
   my $q = shift;
   my $dTag = $q->param("dTag");
   my $ballot_id = db_select("select ballot_id from id_internal where id_document_tag=$dTag");
   my $rfc_flag = $q->param("rfc_flag");   # RFC or ID
   my $area_acronym_id = $q->param("area_acronym_id");
   my $update_area_acronym = "";
   if (my_defined($area_acronym_id)) {
      $update_area_acronym = "area_acronym_id = $area_acronym_id,";
   }
   my $agenda = $q->param("agenda");
   if ($agenda eq "on") {
      $agenda = 1;
   } else {
      $agenda = 0;
   }
   my $cur_state = $q->param("cur_state"); # Current State
   my $prev_state = $q->param("prev_state"); # Previous State
   my $next_state = $q->param("next_state"); # Next State
   my $cur_sub_state_id = $q->param("cur_sub_state_id");
   my $prev_sub_state_id = $q->param("sub_state_id");
   my $sub_state_id = $q->param("sub_state_id");
   my $loginid = $q->param("loginid"); # login id of current user
   #Convert date to appropriate format along with current Database
   my $status_date = $q->param("status_date");
   unless (validate_date($status_date)) {
      return qq {<h3>Invalid Due Date</h3>
<hr>
<li>Date should be in YYYY-MM-DD format<br>
<li>Date can't be prior to current date<br>
<li>Date can't be beyond two years after current date<br>
};
   }
   $status_date = convert_date($status_date,$CONVERT_SEED);
   my $mark_by = $loginid; # Marked by
   my $comment = $q->param("comment"); #Comment
   my $job_owner = $q->param("job_owner"); #Assigned to
   $job_owner = $loginid if (defined($q->param("assign_to_me")));
   my $note = $q->param("note");
   $note = db_quote(format_textarea($note)); 
   my $old_area_acronym_id = $q->param("old_area_acronym_id");
   my $old_status_date = convert_date($q->param("old_status_date"),$CONVERT_SEED);
   my $old_assigned_to = $q->param("old_assigned_to");
   my $old_job_owner = $q->param("old_job_owner"); 
   my $public_flag = $q->param("public_flag"); #Public or Private
   my $version = db_select("select revision from internet_drafts where id_document_tag = $dTag");
   $version = db_quote($version);
   my $html_txt = "Updated...";
   my $cur_time = db_quote(get_current_time());
   #my $process_prev_state = $q->param("process_prev_state");
   my $id_intended_status = $q->param("id_intended_status");
   my $old_id_intended_status = $q->param("old_id_intended_status");
   my $update_iis_sql = qq {update internet_drafts
   set intended_status_id = $id_intended_status
   where id_document_tag = $dTag
   };
   my $owner_mode = 1;
   if ($mark_by != $old_job_owner) {
      $owner_mode = 0;
   }
   #return $sqlStr;
   my $token_name = db_quote(get_mark_by($job_owner));
   $sqlStr = qq {
   select email_address from email_addresses e,iesg_login i
   where i.id = $job_owner
   AND i.person_or_org_tag = e.person_or_org_tag
   AND e.email_priority = 1
   };
   my $token_email = db_quote(rm_tr(db_select($sqlStr)));
   my $log_txt = "";
#   if ($process_prev_state != 0) {
   if (defined($q->param("process_prev_button"))) {
      $next_state = $prev_state;
      #return process_prev_state($q);
	  #return view_id($q);
   }
   if ($next_state == 0 and defined($q->param("next_state_button"))) {
      my $next_state_val = db_quote($q->param("next_state_button"));
	  $next_state = db_select("select document_state_id from ref_doc_states_new where document_state_val = $next_state_val");
          $sub_state_id = 99;
   }
   my $update_states_str = "";
   my $new_mark_by = get_mark_by($loginid);
   ################### Update Comment Log ####################
   if (($cur_state != $next_state and $next_state != 0) or ($cur_sub_state_id != $sub_state_id and $sub_state_id > -1)) {
     my $new_state_txt = "";
     my $origin_state_txt = "";
     my $new_sub_state = "";
     my $origin_sub_state = "";
     if ($next_state > 0) {
#	  if ($next_state == 15) {
#             $assigned_to = "IETF Secretary";
#          }
#	  if ($next_state == 11 || $next_state == 36) {
#	  }
#	  if ($next_state == 31) {
#             $assigned_to = "RFC Editor";
#          }
   
          $prev_state = $cur_state;
	  $cur_state = $next_state;
	  my $ballot_exist = $q->param("ballot_exist");
     } 
    if ($sub_state_id > -1) {
        $prev_state = $cur_state if ($next_state == 0);
        $prev_sub_state_id = $cur_sub_state_id;
        $cur_sub_state_id = $sub_state_id;
        $cur_sub_state_id = 0 if ($sub_state_id == 99);
        $new_sub_state = " -- " . get_sub_state($cur_sub_state_id);
        $origin_sub_state = " -- " . get_sub_state($prev_sub_state_id) if ($prev_sub_state_id > 0);
    }
     $new_state_txt = db_select("select document_state_val from ref_doc_states_new where document_state_id = $cur_state");
     $origin_state_txt = db_select("select document_state_val from ref_doc_states_new where document_state_id = $prev_state");

     $log_txt = qq {State Changes to <b>$new_state_txt $new_sub_state</b> from <b>$origin_state_txt $origin_sub_state</b> by <b>$new_mark_by</b>};
     $log_txt = db_quote($log_txt);
	 $update_states_str = qq{cur_state = $cur_state,
prev_state = $prev_state,
cur_sub_state_id = $cur_sub_state_id,
prev_sub_state_id = $prev_sub_state_id,
	 };
   }

   my $id_status_log = "";
   if ($id_intended_status != $old_id_intended_status) {
      my $new_status = rm_tr(db_select("select status_value from id_intended_status where intended_status_id = $id_intended_status"));
      my $old_status = rm_tr(db_select("select status_value from id_intended_status where intended_status_id = $old_id_intended_status"));
      $id_status_log .= qq {Intended Status has been changed to <b>$new_status</b> from <b>$old_status</b><br>};
   }
   if (my_defined($status_date) and $old_status_date ne $status_date) {
      $id_status_log .= "Due date has been changed to $status_date from $old_status_date<br>";
   } else {
      #$status_date = $old_status_date;
   }
   if (my_defined($area_acronym_id) and $old_area_acronym_id != $area_acronym_id) {
      my $new_aval = rm_tr(db_select("select acronym from acronym where acronym_id=$area_acronym_id"));
      my $old_aval = rm_tr(db_select("select acronym from acronym where acronym_id=$old_area_acronym_id"));
	  $id_status_log .= "Area acronymn has been changed to $new_aval from $old_aval<br>";
   #}
   #if (my_defined($assigned_to) and $old_assigned_to ne $assigned_to) {
   #   $id_status_log .= "responsible has been changed to $assigned_to from $old_assigned_to<br>";
   } else {
      $assigned_to = $old_assigned_to;
   }
   if ($old_job_owner != $job_owner) {
      $new_job_owner_str = get_mark_by($job_owner);
	  $old_job_owner_str = get_mark_by($old_job_owner);
	  $id_status_log .= "Shepherding AD has been changed to $new_job_owner_str from $old_job_owner_str<br>";
   }
   my $comment_added = "";
   if (my_defined($comment)) {
      $comment_added .= "A new comment added<br>";
   }
   my $email_txt = "";
   if (my_defined($id_status_log) or my_defined($comment_added)) {
      $email_txt = $id_status_log . " $comment_added ";
      $id_status_log .= "by <b>$new_mark_by</b>";
      $email_txt .= "by $new_mark_by";
	  $id_status_log = db_quote($id_status_log);
   }
   #$comment = format_textarea($comment);
   #return $comment;
   #return $id_status_log;

   return $error_msg unless (update_comment_log($loginid,$dTag,$version,$mark_by,$cur_state,$prev_state,$comment,$log_txt,$public_flag,$id_status_log));
   ($status_date,$assigned_to) = db_quote($status_date,$assigned_to);
   ###################### Update id_internal Table fields ####################
   my $sqlStr = qq { Update id_internal
   Set status_date = $status_date,
	   assigned_to = $assigned_to,
	   job_owner = $job_owner,
	   mark_by = $mark_by,
	   token_name = $token_name,
	   email_display = $token_name,
	   token_email = $token_email,
           note = $note,
           agenda = $agenda,
	   $update_states_str
	   event_date = $CURRENT_DATE,
	   $update_area_acronym
	   ref_history = 999999
   Where ballot_id = $ballot_id
   };
   #return $sqlStr;
   return $error_msg unless (db_update($sqlStr));
   if ($id_intended_status != $old_id_intended_status) {
      return $error_msg unless (db_update($update_iis_sql));
   }
   ################### Update Ballots ############################
#   if (my_defined($update_states_str)) {
#      my ($ballot_id,$group_flag) = db_select("select ballot_id,group_flag from id_internal where id_document_tag=$dTag");
#      $sqlStr = qq {
#update id_internal
#set group_flag = $group_flag
#where ballot_id =  $ballot_id
#};
#   #return $sqlStr;
#   return $error_msg unless db_update($sqlStr);
#   }
   if ((my_defined($email_txt) or my_defined($log_txt)) and $owner_mode == 0) {
      my $filename;
	  if ($rfc_flag) {
	     $filename = "RFC $dTag";
	  } else {
	     $filename = rm_tr(db_select("select filename from internet_drafts where id_document_tag = $dTag"));
	  }
      return "<h3>Failed to send an email to AD</h3>" unless (email_to_AD($filename,$email_txt,$log_txt,$old_job_owner,$loginid));
   }
   $html_txt = view_id($q);
   return $html_txt;
}

sub email_to_AD {
 #  return 1;
   $devel = "devel";
   my ($filename,$id_status_log,$log_txt,$ad_id,$other_ad_id) = @_;
   my $other_name = get_mark_by($other_ad_id);
   my $sqlStr = qq{
   select email_address from email_addresses e,iesg_login i
   where i.id = $ad_id
   AND i.person_or_org_tag = e.person_or_org_tag
   AND e.email_priority = 1
   };
   my $email_address = rm_tr(db_select($sqlStr));
   #$email_address = "mlee\@foretec.com" if (my_defined($devel));
   $id_status_log = unformat_textarea($id_status_log) if (my_defined($id_status_log));
   $log_txt = unformat_textarea($log_txt) if (my_defined($log_txt));
   open MAIL, "| /usr/lib/sendmail -t -i" or return 0;
   print MAIL <<END_OF_MESSAGE;
To: $email_address
From: "DraftTracker Mail System" <draft_tracker\@ietf.org>
Subject: $filename changed by $other_name

Please DO NOT reply on this email.

ID: $filename

$id_status_log
$log_txt
END_OF_MESSAGE

   close MAIL or return 0;
   return 1;
   
}



###################################
# Function: generate_error_log
# Parameters: 
#    $error_msg - Error message 
# return: none
#    This function appends error message to $LOG_PATH/process.log,
#    then terminate the program returning some value to sendmail
#    program so a sender can receive some sort of error message.
###################################
sub generate_error_log {
   my $error_msg = shift;
   open ERROR_LOG,">>$LOG_PATH/id_tracker_error.log" or return;
   print ERROR_LOG "$error_msg\n";
   close ERROR_LOG;
   return;
}


###########################################################
#
# Function is_unique_comment
# Parameters:
#   $loginid - login id of current user
#   $log_text - text of comment to be tested
#   $document_id - Document Id of current draft
# return: 1 if unique comment
#         0 if duplicate comment exists
#
###########################################################
sub is_unique_comment {
   my ($loginid,$log_txt,$document_id) = @_;
   my $sqlStr = "select count(*) from document_comments where created_by = $loginid AND comment_text = $log_txt AND document_id = $document_id and comment_date = $CURRENT_DATE";
   my $count = db_select($sqlStr);
   if ($count > 0) { #There is same comment already existed
     return 0;
   }
   return 1;
}

############################################################
#
# Function : view_comment
# Paramters:
#   $q - CGI variables
# return: HTML text to display detail information of selected comment
#
###########################################################
sub view_comment {
   my $q = shift;
   my $loginid = $q->param("loginid");
   my $id = $q->param("id");
   my $html_txt = "";
   
   my $sqlStr = qq {
   select document_id,rfc_flag,public_flag,comment_date,comment_time,
   version,comment_text,created_by,result_state,origin_state
   from document_comments
   where id = $id
   };
   #return $sqlStr;
   my ($document_id,$rfc_flag,$public_flag,$comment_date,$comment_time,$version,$comment_text,$created_by,$result_state,$origin_state) = db_select($sqlStr);
   my $origin_state_txt = db_select("select document_state_val from ref_doc_states_new where document_state_id = $origin_state");
   my $result_state_txt = db_select("select document_state_val from ref_doc_states_new where document_state_id = $result_state");
   $comment_date = convert_date($comment_date,1);
   my $created_by_str = get_mark_by($created_by);
   $html_txt .= qq {
   $table_header
   <tr><td><b>Date and Time:</td><td>$comment_date, $comment_time</td></tr>
   <tr><td><b>Version:</td><td>$version</td></tr>
   <tr><td><b>Commented by:</td><td>$created_by_str</td></tr>
   <tr><td><b>State before Comment:</td><td>$origin_state_txt</td></tr>
   <tr><td><b>State after Comment:</td><td>$result_state_txt</td></tr>
   <Tr><td><b>Comment:</td><td>$comment_text</td></tr>
   </table>
   <center><form>
   <input type="button" value="close" onClick="window.close();">
   </form></center>
   };
   return $html_txt;
}


###########################################################################
#
# Function get_id_status_option_str
# Parameters :
# return : HTML text to display options of ID intended_status
# 
##########################################################################
sub get_id_status_option_str {
   my $selected_id = shift;
   my $rfc_flag = shift;
   my $html_txt;
   my $table_name = "id_intended_status";
   $table_name = "rfc_intend_status" if ($rfc_flag);
   my @List = db_select_multiple("select intended_status_id,status_value from $table_name");
   for $array_ref (@List) {
      my ($id,$val) = @$array_ref;
      my $selected = "";
      $selected = "selected" if ($id == $selected_id);
      $val = rm_tr($val);

      $html_txt .= qq {<option value="$id" $selected>$val</option>
};
   }
   return $html_txt;
}

############################################################################
#
# Function  display_all
# Parameters :
#   @docList - list data to be displayed
# result: HTML text displaying the list
#
############################################################################
sub display_all {
   my @docList = @_;
   my $loginid = pop @docList;
   my $prev_state = 0;
   my $prev_sub_state = 0;
   my $html_txt = qq{
   $table_header};
   my $row_color = $menu_sColor;
   my $old_ballot = 0;
   my $count = 0;
   for $array_ref (@docList) {
      my ($dTag,$status_date,$event_date,$mark_by,$cur_state,$cur_sub_state,$assigned_to,$rfc_flag,$ballot_id,$all_list) = @$array_ref;
      $all_list = 0 unless my_defined($all_list);
      $all_list = 0 unless ($all_list =~ /^\d/);
	  $count++;
	  if (($cur_state != $prev_state or $cur_sub_state !=  $prev_sub_state) and $old_ballot != $ballot_id) {
             my $cur_state_val = rm_tr(db_select("select document_state_val from ref_doc_states_new where document_state_id = $cur_state"));
             $prev_state = $cur_state;
             $prev_sub_state = $cur_sub_state;
             my $cur_sub_state_val = "";
             if ($cur_sub_state > 0) {
               $cur_sub_state_val = " -- ";
               $cur_sub_state_val .= get_sub_state($cur_sub_state);
             }

                $html_txt .= qq{                 
                 </table>
                 <h3>In State: $cur_state_val $cur_sub_state_val</h3>
         <table bgcolor="#DFDFDF" cellspacing="0" cellpadding="0" border="0" width="800">
         <tr bgcolor="A3A3A3"><th>&nbsp;</th><th width="250">Name (Intended Status)</th><th>Ver</th><th>Shepherding AD</th><th>Due Date</th><th>Modified (EST)</th></tr>
               };

	  }
	  
	  my $pre_list;
	  if ($old_ballot != $ballot_id) {
	     $old_ballot = $ballot_id;
	     $pre_list = "<li>";
    	  if ($row_color eq $menu_fColor) {
	        $row_color = $menu_sColor;
	      } else {
	        $row_color = $menu_fColor;
	      }
	  } else {
	     $pre_list = "<dd><font size=\"-1\">";
	  }
	  my $ballot_list = "";
	  
	  $ballot_list = get_ballot_list($loginid,$ballot_id,$dTag,$row_color) if ($all_list == 1);
      $status_date = convert_date($status_date,1);
	  $event_date = convert_date($event_date,1);
	  $html_txt .= display_one_row($loginid,$ballot_id,$dTag,$rfc_flag,$assigned_to,$mark_by,$status_date,$event_date,$row_color,$pre_list);
	  $html_txt .= $ballot_list;
   }
   unless ($count) {
      return "<h3>No Record found</h3>\n";
   }
   $html_txt .= qq {</table>
   };   
   return $html_txt;

}

sub get_ballot_list {
   my $loginid = shift;
   my $ballot_id = shift;
   my $id_document_tag = shift;
   my $row_color = shift;
   my $html_txt = "";
   my $sqlStr;
   if ($db_mode == $MYSQL) {
      $sqlStr = qq {
select it.id_document_tag,id.filename,rfc.rfc_number,it.rfc_flag,it.assigned_to,it.job_owner,
it.status_date,it.event_date
from id_internal it
left outer join internet_drafts id on it.id_document_tag = id.id_document_tag
left outer join rfcs rfc on it.id_document_tag = rfc.rfc_number
where it.ballot_id = $ballot_id and it.id_document_tag <> $id_document_tag
order by id.filename, rfc.rfc_number
};
   } else {
      $sqlStr = qq {
select it.id_document_tag,id.filename,rfc.rfc_number,it.rfc_flag,it.assigned_to,it.job_owner,
it.status_date,it.event_date
from id_internal it, outer internet_drafts id, outer rfcs rfc
where it.ballot_id = $ballot_id
AND it.id_document_tag = id.id_document_tag and it.id_document_tag <> $id_document_tag
AND it.id_document_tag = rfc.rfc_number
order by id.filename, rfc.rfc_number
	  };
   }
   my @List = db_select_multiple($sqlStr);
   my $pre_list = "<dd><font size=\"-1\">";
   for $array_ref (@List) {
      my ($id_document_tag,$filename,$rfc_number,$rfc_flag,$responsible,$job_owner,$status_date,$event_date) = @$array_ref;
	  $responsible = rm_tr($responsible);
	  $html_txt .= display_one_row($loginid,$ballot_id,$id_document_tag,$rfc_flag,$responsible,$job_owner,$status_date,$event_date,$row_color,$pre_list);
   }
   return $html_txt;
}

sub display_one_row {
   my ($loginid,$ballot_id,$id_document_tag,$rfc_flag,$responsible,$job_owner,$status_date,$event_date,$row_color,$pre_list) = @_;
   my ($revision,$filename,$actual_file,$intended_status_str,$ballot_str);
   if ($ADMIN_MODE) {
	     $ballot_str = qq{[$ballot_id] <a href="http://cf.amsl.com/system/id/add/search_id3.cfm?id_document_tag=$id_document_tag&isnew=no&searchResults=$id_document_tag" 
		 onMouseOver="window.status='Detail of $id_document_tag';return true;" 
		 onMouseOut="window.status='';return true;"
		 TARGET="_blank">[detail]</a>};
   }
   if ($rfc_flag == 1) {
	     $revision = "RFC";
		 $filename = "rfc" . $id_document_tag;
		 $actual_file = "rfc/${filename}.txt";
		 $intended_status_str = db_select("select b.status_value from rfcs a, rfc_intend_status b where a.rfc_number = $id_document_tag and a.intended_status_id = b.intended_status_id");
   } else {
	     ($filename,$revision) = rm_tr(db_select("select filename,revision from internet_drafts where id_document_tag = $id_document_tag"));
		 $actual_file = "internet-drafts/${filename}-${revision}.txt";
		 $intended_status_str = db_select("select b.status_value from internet_drafts a, id_intended_status b where a.id_document_tag = $id_document_tag and a.intended_status_id = b.intended_status_id");
   }
   $status_date = convert_date($status_date,1);
   $event_date = convert_date($event_date,1);
   
   
   
   
   
   my $mark_by = get_mark_by($job_owner);
   my $html_txt = "";
	  $html_txt .= qq{
	  <tr bgcolor="$row_color">
       $form_header	  
	   <td>
       <input type="hidden" name="command" value="view_id">
	   <input type="hidden" name="dTag" value="$id_document_tag">
	   <input type="hidden" name="rfc_flag" value="$rfc_flag">
	   <input type="hidden" name="loginid" value="$loginid">
       <input type="submit" value="VIEW">
	  </td>
      </form>
	  
	  <Td nowrap>$pre_list <a href="http://www.ietf.org/$actual_file" TARGET=_BLANK>$filename ($intended_status_str)</a> $ballot_str</td>
          <td>$revision</td><td>$mark_by</td>
	  <td>$status_date</td><td>$event_date</td>
	  </tr>
	  };
   
   return $html_txt;   
}


###########################################################
#
# Function: get_next_state_button_str
# Parameter:
#   $cur_state - record id of current state
# return: HTML text to create next state buttons based on current state
#
# This function generate the HTML text for next state by looking up
# the table ref_next_states_new
#
###########################################################
sub get_next_state_button_str {
   my $cur_state = shift;
   my $html_txt = "";
   my @list = db_select_multiple("select next_state_id from ref_next_states_new where cur_state_id = $cur_state");
   for $array_ref (@list) {
      my ($state_id) = @$array_ref;
	  my $state_str = rm_tr(db_select("select document_state_val from ref_doc_states_new where document_state_id = $state_id"));
	  $html_txt .= qq {
		  <input type="submit" value="$state_str" name="next_state_button" >
	  };
   }
   return $html_txt;
}

#########################################################
#
# Function: process_prev_state
# Parameters:
#   $q - CGI variables
# result: error message if an error occurred during updating database
#
# This function processes the 'Back to Previous State' button
#
########################################################
sub process_prev_state {
   my $q = shift;
   my $dTag = $q->param("dTag");
   my $rfc_flag = $q->param("rfc_flag");
   my $cur_state = $q->param("cur_state");
   my $prev_state = $q->param("prev_state");
   my $next_state = $q->param("next_state");
   my $loginid = $q->param("loginid");
   my $status_date = db_quote(convert_date($q->param("status_date"),$CONVERT_SEED));
   my $mark_by = $loginid;
   my $assigned_to = db_quote($q->param("assigned_to"));
   my $comment = $q->param("comment");
   my $public_flag = $q->param("public_flag");
   my $version = db_select("select revision from internet_drafts where id_document_tag = $dTag");
   $version = db_quote($version);
   my $html_txt = "Updated...";
   my $cur_time = db_quote(get_current_time());
   my $process_prev_state = $q->param("process_prev_state");
   my $ref_history = db_select("select ref_history from id_internal where id_document_tag = $dTag");
   
   #my $sqlStr = qq {
   #select Max(id) from document_comments 
   #where document_id = $dTag
   #and result_state = $process_prev_state
   #and  id < $ref_history
   #};
   #my $id = db_select($sqlStr);
   #unless (my_defined($id)) {
   #   return;
   #}
   #my ($result_state,$origin_state) = db_select("select result_state, origin_state from document_comments where id = $id");

   $sqlStr = qq { Update id_internal
   Set cur_state = $prev_state,
       prev_state = $cur_state,
	   status_date = $status_date,
	   assigned_to = $assigned_to,
	   mark_by = $mark_by,
	   job_owner = $job_owner,
	   event_date = $CURRENT_DATE
   Where id_document_tag = $dTag
   };
   #return $sqlStr;
   return $error_msg unless (db_update($sqlStr));

   ################### Update Comment Log ####################
      my $new_state_txt = db_select("select document_state_val from ref_doc_states_new where document_state_id = $prev_state");
      my $origin_state_txt = db_select("select document_state_val from ref_doc_states_new where document_state_id = $cur_state");
      $prev_state = $cur_state;
	  $cur_state = $process_prev_state;
     my $new_mark_by = get_mark_by($loginid);
     $log_txt = qq {State Changes back to previous state <b>$new_state_txt</b> from <b>$origin_state_txt</b> by <b>$new_mark_by</b>};
     $log_txt = db_quote($log_txt);
   update_comment_log($loginid,$dTag,$version,$mark_by,$cur_state,$prev_state,$comment,$log_txt,$public_flag);
   return view_id($q);
   
}

######################################################
#
# Function : add_action
# Parameters:
#   $q - CGI variables
# result: HTML text of search table to add an action
#
######################################################
sub add_action {
   my $q = shift;
   my $loginid = $q->param("loginid");
   my $ballot_id = $q->param("ballot_id");
   my $dTag = $q->param("dTag");
   my $html_txt = qq {
   <h2>Add an Action</h2>
   };
   my $search_html = search_html($loginid,$ballot_id,1,$dTag);
   $html_txt .= qq {
   $search_html
   };
   return $html_txt;
}

########################################################
#
# Function: get_resp_optoin_str
# Parameters:
# return: HTML text to display options of "Responsible" Select field
#
########################################################
sub get_resp_option_str {
   my @list = db_select_multiple("select ref_resp_val from ref_resp");
   my $resp_option_str = "";
   for $array_ref (@list) {
     my ($resp_val) = @$array_ref;
     $resp_val = rm_tr($resp_val);
     $resp_option_str .= qq{
     <option value="$resp_val">$resp_val
     };
   }
   return $resp_option_str;
}

########################################################
#
# Function get_area_optio_str
# Parameters:
# result: HTML text to display the options of "Area" field
#
########################################################
sub get_area_option_str {
   my $select_id = shift;
   $select_id = 0 unless my_defined($select_id);
   my $area_option_str = "";
   @list = db_select_multiple("select a.area_acronym_id,b.acronym from areas a,acronym b where a.area_acronym_id = b.acronym_id AND a.status_id = 1");
   for $array_ref (@list) {
      my $selected = "";
      my ($aid,$aval) = @$array_ref;
	  $selected = "selected" if ($aid == $select_id);
      $aval = rm_tr($aval);
      $area_option_str .= qq {<option value="$aid" $selected>$aval</option>
      };
   }
   return $area_option_str;
}

sub gen_agenda {
   my $q = shift;
   my $loginid= $q->param("loginid");
   my @List = db_select_multiple("select document_state_id,document_state_val from ref_doc_states_new");
%group_name = {};
for $array_ref (@List) {
   my ($flag,$val) = @$array_ref;
   $group_name{$flag} = $val;
}
   my $admin_text = "";
   if ($ADMIN_MODE) {
     $admin_text = qq {
   <table><tr>
   $form_header
   <input type="hidden" name="command" value="action">
   <input type="hidden" name="loginid" value="$loginid">
   <input type="hidden" name="cat" value="agenda">
   <td><input type="submit" value = "Generate Web Page"></td>
   </form>
   $form_header
   <input type="hidden" name="command" value="clear_agenda">
   <input type="hidden" name="loginid" value="$loginid">
   <td><input type="submit" value = "Clear All" onClick="return window.confirm('You are about to clear all agenda');"></td>
   </form></tr></table>
   }
} 

 
   my $html_txt = qq{<center><h3>Draft Telechat Agendas</h3></center>
   $admin_text
   $form_header
   <input type="hidden" name="command" value="update_agenda">
   <input type="hidden" name="loginid" value="$loginid">
   <input type="submit" value="UPDATE">
   $table_header <tr><td>
   <div id="largefont">All Ballots</div>
	     <table cellpadding="0" cellspacing="0" border="0">
   };
   $oldGroup = 0;
   my $sqlStr;
   if ($db_mode == $MYSQL) {
      $sqlStr = qq{select a.rfc_flag,a.ballot_id,a.id_document_tag,i.filename,i.id_document_name,a.cur_state,a.agenda
	  from id_internal a
	  left outer join internet_drafts i on (
	     a.id_document_tag = i.id_document_tag
	  )
	  where a.primary_flag = 1
      order by a.cur_state, a.ballot_id
      };
   } else {
      $sqlStr = qq{select a.rfc_flag,a.ballot_id,a.id_document_tag,i.filename,i.id_document_name,a.cur_state,a.agenda
   from id_internal a, outer internet_drafts i
   where a.id_document_tag = i.id_document_tag
   AND i.b_approve_date is null
   AND a.primary_flag = 1
   order by a.cur_state, i.filename 
      };
   }
   
   @List = db_select_multiple($sqlStr);
   for $array_ref (@List) {
      my ($rfc_flag,$ballot_id,$document_tag,$filename,$doc_name,$gFlag,$agenda) = @$array_ref;
      if ($rfc_flag) {
		 $doc_name = db_select("Select rfc_name from rfcs where rfc_number = $document_tag");
		 $filename = "rfc${document_tag}.txt";
	  }
      if ($oldGroup != $gFlag) {
	     $oldGroup = $gFlag;
         $html_txt .= qq{
		 </table>
		 <br><div id="largefont2">$group_name{$gFlag}</div><br>
	     <table cellpadding="0" cellspacing="0" border="0">
	     };
	  }
	  $checkedStr = "";
	  if ($agenda) {
	     $checkedStr = "checked";
	  }
      if (my_defined($filename)) {
        $html_txt .= qq{<tr><td><input type="checkbox" value="on" name="$ballot_id" $checkedStr></td>
	  <td><li><a href="${program_name}?dTag=$document_tag&ballot=yes&loginid=$loginid&command=view_id&rfc_flag=$rfc_flag" 

	  onMouseOver="window.status='Edit document $document_tag';return true;" 
	  onMouseOut="window.status='';return true;"><b>$filename</b><font size=-1>($doc_name)</font></a></td></tr>
	  };
      }
   }
   $html_txt .= "</table>\n";
   $html_txt .= qq{
   <input type="submit" value="UPDATE">
   </form>
   </table>
   };
   $html_txt .= $admin_text;
   return $html_txt;
}

sub clear_agenda {
   my $q = shift;
   my $loginid = get_mark_by($q->param("loginid"));
   my $current_date = get_current_date();
   system "echo Agenda cleared by $loginid on $current_date>> /export/home/mlee/RELEASE/LOGS/tracker.log";
   db_update("UPDATE id_internal set agenda=0 where 0=0\n");
   my $html_txt = "</center>\n";
   $html_txt .= gen_agenda($q);
   return $html_txt;
}

sub update_agenda {
   my $q = shift;
   db_update("UPDATE id_internal set agenda=0 where 0=0\n");
   $sqlStr = "UPDATE id_internal set agenda=1 where \n";
   foreach ($q->param) {
      if (/^\d/) {
	     $sqlStr .= "ballot_id = $_ OR\n";
      }
   }
   chop($sqlStr);
   chop($sqlStr);
   chop($sqlStr);
   chop($sqlStr);
#   return $sqlStr;   
   db_update($sqlStr);
   my $html_txt = "</center>\n";
   $html_txt .= gen_agenda($q);
   return $html_txt;
}

sub get_sub_state {
  my $id = shift;
  return rm_tr(db_select("select sub_state_val from sub_state where sub_state_id = $id"));
}

sub get_sub_state_select {
  my $default_id = shift;
  my $default_str = "No Problem";
  my $html = qq {<select name="sub_state_id">
};
  if ($default_id == -1) {
    $html .= qq{ <option value="-1">--Select Sub State</option>
};
  }
  if ($default_id == -2) {
    $html .= qq{ <option value="0">--Select Sub State</option>
};        
  }       

  $html .= qq{
  <option value=0>$default_str</option>
};
  my @List = rm_tr(db_select_multiple("select sub_state_id,sub_state_val from sub_state order by 1"));
  for $array_ref (@List) {
    my ($id,$val) = @$array_ref;
    my $selected = "";
    $selected = "selected" if ($id == $default_id);
    $html .= "  <option value=$id $selected>$val</option>\n";
  }
  if ($default_id > -1) {
    my $max_id = db_select("select max(sub_state_id) from sub_state");
    $max_id++;
    $html .= "<option value=$max_id selected>--All Substates</option>\n";
  }
  $html .= "</select>\n";
  return $html;
}
  
sub gen_template {
   my $html_txt = qq {
   <h2>Templates</h2>
   Please put HTML code for each template<br>
   <h3>Agenda</h3>
   };
   my $text = db_select("select note from id_internal where group_flag=100");
   if (my_defined($text)) {
      $text = rm_tr($text);
   }
   $html_txt .= qq {
   <form action="http://10.27.30.48/DEV/system/update_template.cfm" method="POST">
   <textarea name="note" cols="70" rows="10" wrap="virtual">$text</textarea><br>
   <input type="submit" value="SUBMIT">
   </form>
   };
   return $html_txt;
}

sub gen_single {
   my $html_txt = qq{Single Page Generated};
   return $html_txt;
}
sub gen_pwg {
   my $q = shift;
   my $loginid = $q->param("loginid");
   my $html_txt = "$table_header <tr><td>\n";
   $html_txt .= "<center><br><div id=\"largefont\">Proposed Working Groups</div><br></center><div id=\"largefont2\">Current List</div><br>";
   $sqlStr=qq{select a.name,a.acronym,g.status_date,g.note,g.group_acronym_id
   from group_internal g, acronym a
   where g.group_acronym_id = a.acronym_id
   order by g.status_date DESC
   };
   my %aID;
   $html_txt .= "$table_header \n";
   my @List = db_select_multiple($sqlStr);
   for $array_ref (@List) {
      @row = @$array_ref;
      $ac=rm_tr($row[1]);
      $aID{$ac} = $row[4];
	  $dateStr = $row[2];
	  $dateStr = convert_date($dateStr);
      $html_txt .= qq{
	  $form_header
	  <input type="hidden" name="command" value="edit_delete">
	  <input type="hidden" name="loginid" value="$loginid">
	  <input type="hidden" name="gID" value="$row[4]">
	  <input type="hidden" name="acronym" value="$ac">
	  <input type="hidden" name="title" value="$row[0]">
	  <tr>
	  <td>$dateStr</td><td>$row[0] ($ac)</td>
	  <td><input type="submit" name="edit" value="EDIT"></td>
	  <td><input type="submit" name="delete" value="DELETE"></td>
	  </tr>
	  </form>
	  };
   }
   $html_txt .= "</table>\n";
   $html_txt .= qq{<br>
   <div id="largefont2">Possible List</div><br>
   $table_header
   };
   while ($filename=</usr/local/etc/httpd/htdocs/IESG/EVALUATIONS/*-charter.txt>) {
      open INFILE,$filename;
      $_ = <INFILE>;
      while (/^\W/) {
         $_ = <INFILE>;
      }
      chomp ($header = $_);
      @headAry = split '\(',$header;
      $name_val = $headAry[0];
      $ac_val = $headAry[1];
      @headAry = split '\)',$ac_val;
      $ac_val = $headAry[0];
	  if (!defined($aID{$ac_val})) {
         for ($loop=0;$loop<4;$loop++) {
            chomp($_ = <INFILE>);
         }
         @aryStr = split ':',$_;
         $dateStr = $aryStr[1];
         @dateParts = split '-',$dateStr;
         $day = $dateParts[0] + 1;
         $month = uc(substr($dateParts[1],0,3));
         $year = $dateParts[2];
         if (length($year) < 4) {
            $year = "20".$year;
         }
         $dateStr = $day."-".$month."-".$year;
		 my $token_list;
		 while (<INFILE>) {
            if (/.Area Director./) {
               $line = <INFILE>;
               chomp($line);
               while (length($line)) {
                  @temp = split ' ',$line;
                  $token_list .= "$temp[0] ";
                  $line = <INFILE>;
                  chomp($line);
                  chop($line);
				  chop($line);
                  chop($line);
				  chop($line);
               }
		       last;
		   }
		}
		 $html_txt .= qq{
		 $form_header
		 <input type="hidden" name="command" value="add_delete_pwg">
		 <input type="hidden" name="loginid" value="$loginid">
		 <input type="hidden" name="acronym" value="$ac_val">
		 <input type="hidden" name="status_date" value="$dateStr">
		 <input type="hidden" name="title_val" value="$name_val">
		 <input type="hidden" name="filename" value="$filename">
		 <input type="hidden" name="token_list" value="$token_list">
		 <tr>
		 <td>$month $day</td>
		 <td>$name_val ($ac_val)</td>
		 <td><input type="submit" value="ADD"></td>
		 <td><input type="submit" value="PERMANENT DELETE" name="delete"
		 onClick="return window.confirm('The file will be permanently removed from server');"></td>
		 </tr>
		 </form>
		 };
      }
      close (INFILE);
   }
   $html_txt .= qq{</table></td></tr></table>};  
   $html_txt .= qq{
   $form_header
   <input type="hidden" name="command" value="action">
   <input type="hidden" name="loginid" value="$loginid">
   <input type="hidden" name="cat" value="pwg">
   <input type="submit" value = "Generate Web Page">
   </form>
   };
   return $html_txt;
}

sub add_pwg {
   my $q = shift;
   my $ac_val = $q->param("acronym");
   my $status_date = $q->param("status_date");
   my $title_val = $q->param("title_val");
   my$token_list = $q->param("token_list");
   my $loginid = $q->param("loginid");
   my @list = split " ",$token_list;
   my $select_str = qq{<select name="token_name">};
   foreach $val (@list) {
      $select_str .= qq{
	     <option value="$val">$val</option>
	  };  
   }
   $select_str .= qq{</select>};
   
   $html_txt = "";
   $html_txt .= qq{<h4>Adding new PWG list</h4>
   $table_header <tr><td>
   $form_header
   <input type="hidden" name="acronym" value="$ac_val">
   <input type="hidden" name="command" value="add_db">
   <input type="hidden" name="loginid" value="$loginid">
   <font color="red"><b>$title_val ($ac_val)</b></font><br><br>
   Status Date: <input type="text" name="status_date" value="$status_date"><br>
   Token Name: $select_str<br>
   Note: <br>
   <textarea name="note" cols="40" rows="5" wrap="virtual"></textarea><br>
   <input type="submit" value="CONFIRM ADD">
   </form>
   </td></tr></table>
   };
   return $html_txt;
}

sub add_db {
   my $q = shift;
   my $ac_val = $q->param("acronym");
   my $status_date = $q->param("status_date");
   my $note = $q->param("note");
   my $token_name = $q->param("token_name");
   my $loginid = $q->param("loginid");
   $status_date = y_two_k($status_date);
   $status_date = db_quote($status_date);
   $note = db_quote($note);
   $ac_val = db_quote($ac_val);
   $token_name = db_quote($token_name);
   $sqlStr = "select acronym_id from acronym where acronym = $ac_val";
   my $gID = db_select($sqlStr);
   return "<b>ERROR: The group acronym can not be found</b>"  unless $gID;
   $sqlStr = qq{
   insert into group_internal (group_acronym_id,note,status_date,token_name)
   values ($gID,$note,$status_date,$token_name)
   };
   #return $sqlStr;
   db_update($sqlStr);
   my $html_txt = gen_pwg($q);
   return $html_txt;
}
sub edit_pwg {
   my $q = shift;
   my $gID = $q->param("gID");
   my $acronym = $q->param("acronym");
   my $title = $q->param("title");
   my $loginid = $q->param("loginid");
   my ($status_date,$note,$agenda,$token_name) = db_select("select status_date,note,agenda,token_name from group_internal where group_acronym_id = $gID");
   $note = rm_tr($note);
   $token_name = rm_tr($token_name);
   my $agenda_str = "";
   if ($agenda) {
     $agenda_str .= qq{
	    <input type="checkbox" checked name="agenda"><br>
	 };
   } else {
     $agenda_str .= qq{
	    <input type="checkbox" name="agenda"><br>
	 };

   }
   $html_txt = "";
   $html_txt .= qq{<h4>Edit PWG list</h4>
   $table_header
   <tr><td>
   $form_header
   <input type="hidden" name="acronym_id" value="$gID">
   <input type="hidden" name="command" value="edit_db">
   <font color="red"><b>$title ($acronym)</b></font><br><br>
   Status Date: <input type="text" name="status_date" value="$status_date"><br>
   Token Name: <input type="text" name="token_name" value="$token_name"><br>
   Check for Agenda: $agenda_str
   Note: <br>
   <textarea name="note" cols="40" rows="5" wrap="virtual">$note</textarea><br>
   <input type="submit" value="CONFIRM EDIT">
   </form>
   </td></tr></table>
   };
   return $html_txt;
}

sub edit_db {
   my $q = shift;
   my $gID = $q->param("acronym_id");
   my $status_date = $q->param("status_date");
   my $note = $q->param("note");
   my $agenda = $q->param("agenda");
   my $token_name = $q->param("token_name");
   if ($agenda eq "on") {
      $agenda_val = 1;
   } else {
      $agenda_val = 0;
   }
   $status_date = y_two_k($status_date);
   $status_date = db_quote($status_date);
   $note = db_quote($note);
   $token_name = db_quote($token_name);
   $sqlStr = qq{update group_internal set note = $note, status_date = $status_date, agenda=$agenda_val, token_name=$token_name
   where group_acronym_id = $gID};
   db_update($sqlStr);
   my $html_txt = gen_pwg($q);
   
   return $html_txt;
}

sub delete_pwg {
	     $filename = shift;
		 my $html_txt = "";
		 $cnt = unlink $filename;
         my @str = split '/',$filename;
	     my $filename_simple = $str[$#str];
		 if ($cnt) {
    	     $html_txt .= qq{<b>$filename</b> is deleted<br>};
	     } else {
    	     $html_txt .= qq{<b>$filename</b> cannot be deleted<br>};
		 }
    	return $html_txt;
}

sub y_two_k {
   my $ret_val = shift;
   return "" unless (my_defined($ret_val));
   $_ = $ret_val;
   if (/\//) {
      my @temp = split '\/';
	  if ($temp[2] < 50) {
		 $temp[2] = 2000 + $temp[2];
	  } 
	  $ret_val = join '/', @temp;
   } else {
      my @temp = split '-';
	  if ($temp[2] < 50) {
	     $temp[2] = $temp[2] + 2000;
	  } 
	  $ret_val = join '-', @temp;
   }
   return $ret_val;
}
