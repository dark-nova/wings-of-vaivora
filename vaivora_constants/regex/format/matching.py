#vaivora_constants.regex.format.matching
import re

letters     = re.compile(r'[a-z -]+', re.IGNORECASE)
numbers     = re.compile(r'^[0-9]+$', re.IGNORECASE)
one_number  = re.compile(r'^[0-9]{1}$')
to_sanitize = re.compile(r'[^a-z0-9 .:$",-]', re.IGNORECASE)
quotes      = re.compile(r'"')
