#vaivora_constants.regex.boss.command
import re

prefix      = re.compile(r'(va?i(v|b)ora, |\$)boss', re.IGNORECASE)
arg_all     = re.compile(r'all', re.IGNORECASE)
arg_list    = re.compile(r'li?st?', re.IGNORECASE)
arg_erase   = re.compile(r'(erase|del(ete)?|cl(ea)?r)', re.IGNORECASE)
