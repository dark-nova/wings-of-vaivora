#vaivora_constants.regex.boss.status
import re

all_status  = re.compile(r'(died|anchor(ed)?|warn(ed|ing)?)', re.IGNORECASE)
anchored    = re.compile(r'(anchor(ed)?', re.IGNORECASE)
warning     = re.compile(r'(warn(ed|ing)?)', re.IGNORECASE)