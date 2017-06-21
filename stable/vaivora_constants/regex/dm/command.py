#vaivora_constants.regex.dm.command
import re

prefix      = re.compile(r'(va?i(v|b)ora, |\$)', re.IGNORECASE)
cmd_help    = re.compile(r'\$help', re.IGNORECASE)
cmd_unsub   = re.compile(r'uns(ub(scribe)*)?', re.IGNORECASE)
cmd_sub     = re.compile(r'sub(scribe)?', re.IGNORECASE)
cmd_boss    = re.compile(r'boss', re.IGNORECASE)
empty_line  = re.compile(r'^[ ]*\n*$', re.IGNORECASE)
