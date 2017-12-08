#vaivora_modules.changelogs
import json
import re

### BGN CONST

mode_sub    =   "subscribe"
mode_unsub  =   "un" + mode_sub

### BGN REGEX

cmd_csub    =   re.compile(r'(un)?sub(scribe)?', re.IGNORECASE)
cmd_un      =   re.compile(r'^un', re.IGNORECASE)
empty_line  =   re.compile(r'^[ ]*\n*$', re.IGNORECASE)

### END REGEX

### END CONST

def get_specific_version(n):
    # Args:
    #     n (int): the index of the changelog to retrieve
    
    # iterate through changelogs dict. assign index based on age

    pass

pass # do things later
