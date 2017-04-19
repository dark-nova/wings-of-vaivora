#vaivora_constants.regex.boss.command
import re

prefix      = re.compile(r'(va?i(v|b)ora, |\$)boss', re.IGNORECASE)
arg_all     = re.compile(r'all', re.IGNORECASE)
arg_list    = re.compile(r'li?st?', re.IGNORECASE)
arg_erase   = re.compile(r'(erase|del(ete)?|cl(ea)?r)', re.IGNORECASE)
arg_info    = re.compile(r'(syn(onyms|s)?|alias(es)?|maps?)', re.IGNORECASE)
arg_syns    = re.compile(r'(syn(onyms|s)?|alias(es)?)', re.IGNORECASE)
arg_maps    = re.compile(r'maps?', re.IGNORECASE)
arg_boss    = re.compile(r'(wor|fie)ld', re.IGNORECASE)
arg_boss_w  = re.compile(r'world', re.IGNORECASE)
arg_boss_f  = re.compile(r'field', re.IGNORECASE)
