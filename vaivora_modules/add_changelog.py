import json
import sys
import os
import re
from datetime import datetime
from shlex import split
# important: do not refer to vaivora_modules; this is not used by vaivora directly
from disclaimer import disclaimer

# BGN CONST

json_file   =   "version.json"
changelogs  =   dict()
header_len  =   62
msg_buffer  =   200 # the 'safe' amount of characters not to exceed
max_msg_len =   2000-(header_len+msg_buffer)

# BGN VERS
milestone   =   "[m]"
incremental =   "[i]"
bugfix      =   "[n]" # nightly
# END VERS

categories  =   ["status", "version", "subversion", "bugfix"]
indent      =   '  '
acknowledge =   '* '
section     =   '+ '

# BGN REGEX
rgx_brackets    =   re.compile(r'\[[imn]\]', re.IGNORECASE)
rgx_nobrackets  =   re.compile(r'[imn]', re.IGNORECASE)
rgx_letter      =   re.compile(r'[a-z]', re.IGNORECASE)

rgx_indent      =   re.compile(r'[+-]i?', re.IGNORECASE)
rgx_plus        =   re.compile(r'^\+.*')
#rgx_section     =   re.compile(r'&s?', re.IGNORECASE)
rgx_mention     =   re.compile(r'@m? *', re.IGNORECASE)
rgx_finish      =   re.compile(r'\$x?', re.IGNORECASE)
#rgx_letter_pre  =   re.compile(r'[0-9]+pre-[0-9]+', re.IGNORECASE)
# END REGEX

# END CONST

def check_revisions(srv_ver):
    if srv_ver == "[m]1.0":
        return len(version_n)-1

    if not srv_ver:
        return 0
    count             =   -1

    aversion, asubver =   srv_ver.split('.')

    letter_check      =   rgx_letter.search(asubver)
    if not letter_check:
        hotfix  =   ''
        subver  =   asubver
    else:
        hotfix  = letter_check.group(0)
        subver  = rgx_letter.sub('', asubver)

    version_check     =   rgx_brackets.match(aversion)
    status            =   version_check.group(0)
    version           =   rgx_brackets.sub('', aversion)

    while version_n[count]  > version or subver_n[count] > subver or hotfix_n[count] > hotfix or \
         (version_n[count] == version and subver_n[count] == subver and hotfix_n[count] == hotfix and compare_status(status_n[count], status)):
        count -= 1

    return count+1


def get_current_version():
    """
    Function to return the current version as a 5-tuple.

    Returns:
        5-tuple:
            sta (str): index 0 of tuple; the STATUS, i.e. [m], [i], [n]
            ver (str, int): index 1 of tuple; the VERSION, e.g. the '1' in 1.0a
            svn (str, int): index 2 of tuple; the SUBVERSION, e.g. the '0' in 1.0a
            fix (str): index 3 of tuple; the BUGFIX, e.g. the 'a' in 1.0a; may be empty string
            msg (str): index 4 of tuple; the MESSAGE, i.e. what the fix was about
    """
    ver =   sorted(changelogs.keys())[-1]
    svn =   sorted(changelogs[ver].keys())[-1]
    fix =   sorted(changelogs[ver][svn].keys())[-1]
    msg =   changelogs[ver][svn][fix]['changelog']
    sta =   changelogs[ver][svn][fix]['status']
    return (sta, ver, svn, fix, msg)


def add_changelog(sta, ver, svn, fix, message):
    """
    Adds a changelog with version assigned. Pre-condition: sta, ver, svn, fix must be valid.
    
    Args:
        sta (str): index 0 of tuple; the STATUS, i.e. [m], [i], [n]
        ver (str, int): index 1 of tuple; the VERSION, e.g. the '1' in 1.0a
        svn (str, int): index 2 of tuple; the SUBVERSION, e.g. the '0' in 1.0a
        fix (str): index 3 of tuple; the BUGFIX, e.g. the 'a' in 1.0a; may be empty string
    
    Returns:
        True if succeeded; otherwise, False
    """

    try: # see if dict is already formed; if not, create them as necessary
        changelogs[ver][svn][fix]
    except:
        try:
            changelogs[ver][svn]
        except:
            changelogs[ver][svn]    =   dict()
        changelogs[ver][svn][fix]   =   dict()

    if not rgx_brackets.match(sta) and rgx_nobrackets.match(sta):
        sta =   '[' + sta + ']'

    changelogs[ver][svn][fix]['status']     =   sta
    changelogs[ver][svn][fix]['changelog']  =   message

    return save2json()


def get_index(sta, ver, svn, fix):
    """
    Gets index of version requested, in tuple form
    
    Args:
        sta (str): index 0 of tuple; the STATUS, i.e. [m], [i], [n]
        ver (str, int): index 1 of tuple; the VERSION, e.g. the '1' in 1.0a
        svn (str, int): index 2 of tuple; the SUBVERSION, e.g. the '0' in 1.0a
        fix (str): index 3 of tuple; the BUGFIX, e.g. the 'a' in 1.0a; may be empty string
    
    Returns:
        index in int if found, 0-base; otherwise, -1
    """
    for n, status, version, subver, hotfix in zip(range(len(version_n)), status_n, version_n, subver_n, hotfix_n):
        if sta == status and ver == version and svn == subver and fix == hotfix:
            return n
    return -1


def log2json():
    """
    Helper function to convert from source to json.
    Possibly obsolete, as migration was one-time. Kept for historical purpose.
    
    """
    # # create if it does not exist
    # if not os.path.isfile(json_file):
    #     open(json_file, 'w').close()
    # for i in range(len(version_n)):
    #     hotfix  =   '0' if not hotfix_n[i] else hotfix_n[i]
    #     # iterate
    #     if not version_n[i] in changelogs.keys():
    #         changelogs[version_n[i]]    =   dict()
    #     if not subver_n[i] in changelogs[version_n[i]].keys():
    #         changelogs[version_n[i]][subver_n[i]]   =   dict()
    #     if not hotfix in changelogs[version_n[i]][subver_n[i]]:
    #         changelogs[version_n[i]][subver_n[i]][hotfix]  =   dict()
    #     if not 'status' in changelogs[version_n[i]][subver_n[i]][hotfix].keys():
    #         changelogs[version_n[i]][subver_n[i]][hotfix]['status']     =   status_n[i]
    #     if not 'changelog' in changelogs[version_n[i]][subver_n[i]][hotfix].keys():
    #         changelogs[version_n[i]][subver_n[i]][hotfix]['changelog']  =   changelog[i]
    # with open(json_file, 'w') as jf:
    #     json.dump(changelogs, jf)
    pass


def json2log():
    """
    Helper function to convert json to logs. Called on script start.
                
    Returns:
        dict of json
    """
    with open(json_file, 'r') as f:
        return json.load(f)


def save2json():
    """
    Helper function to save logs to json. Should only be called after :func:`add_changelog`

    Returns:
        True if successful; otherwise, False
    """
    if not changelogs: # empty; do not overwrite
        return False
    try:
        with open(json_file, 'w') as f:
            json.dump(changelogs, f)
        return True
    except:
        return False


def ver_tup2str(sta, ver, svn, fix):
    """
    Converts a "version" from "tuple" (its components) to str
    
    Args:
        sta (str): index 0 of tuple; the STATUS, i.e. [m], [i], [n]
        ver (str, int): index 1 of tuple; the VERSION, e.g. the '1' in 1.0a
        svn (str, int): index 2 of tuple; the SUBVERSION, e.g. the '0' in 1.0a
        fix (str): index 3 of tuple; the BUGFIX, e.g. the 'a' in 1.0a; may be empty string
    
    Returns:
        str representation of version
    """
    if not rgx_brackets.match(sta) and rgx_nobrackets.match(sta):
        sta =   '[' + sta + ']'
    elif not rgx_brackets.match(sta):
        return '' # invalid status

    if type(ver) != str:
        ver =   str(ver)
    if type(svn) != str:
        svn =   str(svn)

    return sta + ver + "." + svn + fix 


def ver_str2tup(ver):
    """
    Converts a "version" from str to tuple
    
    Args:
        ver (str): version to change to tuple
    
    Returns:
        tuple representation of version
    """
    ver = list(ver)
    ver.remove('.')
    return tuple(ver)


def check_validity(new, old):
    """
    Checks whether new version is valid or not
    
    Args:
        new (tuple): new version. can be str
        old (tuple): last version. can be str
          
    Returns:
        True if valid; otherwise, False
    """
    if type(new) == str:
        new = ver_str2tup(new)
    if type(old) == str:
        old = ver_str2tup(old)

    for n, o in zip(new, old):
        if n != o:
            return n > o
    return False


def usage(err=None):
    """
    Prints usage information, usually in invalid cases.

    Args:
        err (None, str): default None; if not, print the error alongside usage.

    Returns:
        False
    """
    print('Usage: add_changelog [status version subversion bugfix]')
    print('Current Version: ' + ver_tup2str(*current_sta))
    if not err:
        print('[status version subversion bugfix] are optional but must all be completed if one is filled in.')
        print('[status]     - m (milestone), i (incremental), n (nightly/bugfix)')
        print('[version]    - the primary release number.       e.g., the \'1\' in \'1.0a\'')
        print('[subversion] - the secondary release number.     e.g., the \'0\' in \'1.0a\'')
        print('[bugfix]     - the bugfix version; can be empty. e.g., the \'a\' in \'1.0a\'')
        print('To enter an empty [bugfix], use two single quotes.')
        print('Example: add_changelog m 1 1 \'\'')
        print('\nChangelog Editor:')
        print('Use the following options and hit enter after each option you use.')
        print('[+-]i    # indents two spaces, forward (+) or back (-)')
        print('@m       # changes your line character to asterisk for acknowledging')
        print('$x       # quit, to save your changelog')
        print('...or just begin typing your message. (Max. ' + str(max_msg_len) + ' chars.)')
    else:
        print(err)
    #return False
    sys.exit(1)


def prepare_changelog():
    """
    Prints a changelog formatted for logging/history, from user input.

    Returns:
        a str containing the formatted changelog.
    """
    n_ind   =   0
    ind_OK  =   False
    msg     =   ""

    print('\nUse the following options and hit enter after each option you use.')
    print('[+-]i    # indents two spaces, forward (+) or back (-)')
    print('@m       # changes your line character to asterisk for acknowledging')
    print('$x       # quit, to save your changelog')
    print('...or just begin typing your message. (Max. ' + str(max_msg_len) + ' chars.)\n')

    while True:
        msg_len     =   len(msg)
        # section: invalid, went over
        if msg_len > max_msg_len:
            print('You have exceeded the safe character count. Please re-do your changelog.')

            # re-initialize
            n_ind   =   0
            ind_OK  =   False
            msg     =   ""
            
            continue

        raw =   input('Input- ' + str(n_ind) + ' indents; ' + str(msg_len) + '/' + str(max_msg_len) + ' max chars.:\n')

        # section: finish
        if rgx_finish.match(raw):
            return msg

        # section: indent
        elif rgx_indent.match(raw) and ind_OK:
            if rgx_plus.match(raw):
                n_ind   +=  1
            elif n_ind > 0:
                n_ind   -=  1
            else:
                # cannot unindent beyond 0 to negatives; this should not be possible
                print('You cannot indent more or less.') # current only error with bad input
            ind_OK  =   False # regardless of input, disable indentation

        # section: acknowledgement
        elif rgx_mention.match(raw):
            msg +=  (indent * n_ind) # add necessary indentation
            msg +=  acknowledge + rgx_mention.sub('', raw) + "\n"
            ind_OK  =   True # reset indentation to True

        # section: invalid input in the case of valid symbols but invalid flags
        elif (rgx_indent.match(raw) and not ind_OK):
            # print('Warning: invalid input.') # general message
            print('You cannot indent more or less.') # current only error with bad input

        else:
            msg +=  (indent * n_ind)
            msg +=  section + raw + "\n"
            ind_OK  =   True 



# begin script section

changelogs  =   json2log()
current_ver =   get_current_version()
current_sta =   current_ver[0:4]
current     =   current_ver[1:4]

valid       =   False

# enter arg mode
if len(sys.argv) == 5:
    tentative   =   sys.argv[1:]
    if not check_validity(tentative, current):
        usage('Invalid Version')

# enter interactive mode
elif len(sys.argv) == 0:
    sys.stdout.write('Current Version: ' + current_sta)
    ver =   input('Enter new version: [1-' + current[0] + '] (e.g. 1 in 1.0a) ')
    svn =   input('Enter new subversion: (e.g. 0 in 1.0a) ')
    fix =   input('Enter new fix revision: [a-z] (optional) ')
    if not fix:
        fix =   ''
    sta =   input('Enter this version\'s status: [m, i, n] ')
    tentative   =   (sta, ver, svn, fix)
    if not check_validity(tentative, current):
        usage('Invalid Version')

# return general info
else:
    usage()


# begin changelog induction
try:
    tenta_log   =   prepare_changelog()
except:
    print('\nAborted.')
    sys.exit(1)

print('Here is your changelog.\n' + tenta_log)
raw =   input('If you are satisfied, please enter $x (quit) to confirm: ')

if not rgx_finish.match(raw):
    print('Aborted.')
    sys.exit(1)
else:
    # format date block/header
    log_date    =   datetime.now().strftime("%Y/%m/%d") # built on local time; do not use server time
    log_date    =   "```ini\n" + \
                    "[Version:] " + ver_tup2str(*tentative) + "\n" + \
                    "[Date:]    " + log_date + "\n" + \
                    "```"

    # format the string to a code block
    tenta_log   =   "```diff\n" + \
                    tenta_log + \
                    "```"

    # combine, and push to changelogs
    tenta_log   =   log_date + tenta_log
    if add_changelog(*tentative, tenta_log):
        print('Your new changelog has been saved.')
        sys.exit(0)
    else:
        print('Your changelog could not be saved. Please check permissions, and try again.')
        sys.exit(1)
