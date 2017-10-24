import json
import sys
import os
import re
from datetime import date
from shlex import split
# important: do not refer to vaivora_modules; this is not used by vaivora directly
from disclaimer import disclaimer

# BGN CONST

json_file   =   "version.json"
changelogs  =   dict()

# BGN VERS
milestone   =   "[m]"
unstable    =   "[n]" # nightly
bugfix      =   "[i]" # incremental
# END VERS

categories  =   ["status", "version", "subversion", "bugfix"]

# BGN REGEX
rgx_brackets    =   re.compile(r'\[[imn]\]', re.IGNORECASE)
rgx_nobrackets  =   re.compile(r'[imn]', re.IGNORECASE)
rgx_letter      =   re.compile(r'[a-z]', re.IGNORECASE)
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
            sta (str): index 0 of tuple; the STATUS, i.e. [m], [n], [i]
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
    # Adds a changelog with version assigned. Pre-condition: sta, ver, svn, fix must be valid.
    # 
    # Args:
    #       sta (str): index 0 of tuple; the STATUS, i.e. [m], [n], [i]
    #       ver (str, int): index 1 of tuple; the VERSION, e.g. the '1' in 1.0a
    #       svn (str, int): index 2 of tuple; the SUBVERSION, e.g. the '0' in 1.0a
    #       fix (str): index 3 of tuple; the BUGFIX, e.g. the 'a' in 1.0a; may be empty string

    try: # see if dict is already formed; if not, create them as necessary
        changelogs[ver][svn][fix]
    except:
        try:
            changelogs[ver][svn]
        except:
            changelogs[ver][svn]    =   dict()
        changelogs[ver][svn][fix]   =   dict()

    changelogs[ver][svn][fix]['status']     =   sta
    changelogs[ver][svn][fix]['message']    =   message


def get_index(sta, ver, svn, fix):
    # Gets index of changelog requested
    #
    # Args:
    #       sta (str): index 0 of tuple; the STATUS, i.e. [m], [n], [i]
    #       ver (str, int): index 1 of tuple; the VERSION, e.g. the '1' in 1.0a
    #       svn (str, int): index 2 of tuple; the SUBVERSION, e.g. the '0' in 1.0a
    #       fix (str): index 3 of tuple; the BUGFIX, e.g. the 'a' in 1.0a; may be empty string
    #
    # Returns:
    #       index in int if found, 0-base; otherwise, -1
    for n, status, version, subver, hotfix in zip(range(len(version_n)), status_n, version_n, subver_n, hotfix_n):
        if sta == status and ver == version and svn == subver and fix == hotfix:
            return n
    return -1


# helper function to migrate from source to json
# def log2json():
#     # create if it does not exist
#     if not os.path.isfile(json_file):
#         open(json_file, 'w').close()

#     for i in range(len(version_n)):
#         hotfix  =   '0' if not hotfix_n[i] else hotfix_n[i]
#         # iterate
#         if not version_n[i] in changelogs.keys():
#             changelogs[version_n[i]]    =   dict()
#         if not subver_n[i] in changelogs[version_n[i]].keys():
#             changelogs[version_n[i]][subver_n[i]]   =   dict()
#         if not hotfix in changelogs[version_n[i]][subver_n[i]]:
#             changelogs[version_n[i]][subver_n[i]][hotfix]  =   dict()
#         if not 'status' in changelogs[version_n[i]][subver_n[i]][hotfix].keys():
#             changelogs[version_n[i]][subver_n[i]][hotfix]['status']     =   status_n[i]
#         if not 'changelog' in changelogs[version_n[i]][subver_n[i]][hotfix].keys():
#             changelogs[version_n[i]][subver_n[i]][hotfix]['changelog']  =   changelog[i]

#     with open(json_file, 'w') as jf:
#         json.dump(changelogs, jf)


def json2log():
    """
    Helper function to convert json to logs
                
    Returns:
        dict of json
    """
    with open(json_file, 'r') as f:
        return json.load(f)

def save2json():
    """
    Helper function to save logs to json

    Returns:
        True if successful; otherwise, False
    """
    if not changelogs: # empty
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
        sta (str): index 0 of tuple; the STATUS, i.e. [m], [n], [i]
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



changelogs  =   json2log()
current     =   get_current_version()[0:4]

print(current)

valid       =   False

# enter arg mode
if len(sys.argv) == 4:
    pass

# enter interactive mode
# elif len(sys.argv) == 0:
#     sys.stdout.write('Current version: ' + ver_tup2str(current[:-1]))
#     while not valid:
#         # check version
#         ver =   input('Enter new version: [1-x] ')
#         svn =   input('Enter new subversion: [0-x] ')
#         if svn < current[2] and ver == current[1]: # cases: 
#             sys.stdout.write('Invalid. Try again.')
#             continue
#         # check bugfix
#         fix =   input('Enter new fix revision: [a-z] ')
#         if fix < current[3] and svn == current[2] and ver == current[1]: # cases: 2.0a vs 2.0a, 1.0a vs 2.0a, 1.0a vs 1.0b
#             sys.stdout.write('Invalid. Try again.')
#             continue
