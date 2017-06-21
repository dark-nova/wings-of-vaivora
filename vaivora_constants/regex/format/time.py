#vaivora_constants.regex.format.time
import re

full    = re.compile(r'[0-2]?[0-9][:.][0-5][0-9]([ap]m?)?', re.IGNORECASE)
am      = re.compile(r' ?am?', re.IGNORECASE)
pm      = re.compile(r' ?pm?', re.IGNORECASE)
delim   = re.compile(r'[:.]')