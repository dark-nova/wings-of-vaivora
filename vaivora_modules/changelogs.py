#vaivora_modules.changelogs
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