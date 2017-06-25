#vaivora_constants.fun
import re

ohoho       = re.compile(r'\#(oh)+', re.IGNORECASE)
meme        = re.compile(r'vaivora[, ]*pl(ea)?[sz]e?', re.IGNORECASE)
stab        = re.compile(r'[^spw]?(kill|edg[ey]|maim|stab|🗡|⚔).*', re.IGNORECASE)
stab2       = re.compile(r'.*[^s]?kill.*', re.IGNORECASE)
stab3       = re.compile(r'.*[^lw]?edg[ey].*', re.IGNORECASE)
stab4       = re.compile(r'.*stab[^l]*', re.IGNORECASE)
stab5       = re.compile(r'.*maim.*', re.IGNORECASE)