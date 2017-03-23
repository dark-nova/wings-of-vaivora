#vaivora_constants.regex.boss.location
import re

floors_chk  = re.compile(r'[bfd]?[0-9][bfd]?$', re.IGNORECASE)
floors_fmt  = re.compile(r'.*(?P<basement>b?)(?P<floor>f?)(?P<district>(d ?(ist(rict)?)?)?) ?(?P<floornumber>[0-9]) ?(?P=basement)?(?P=floor)?(?P=district)?$', re.IGNORECASE)
channel     = re.compile(r'ch?[1-4]$', re.IGNORECASE)

DW          = "Blasphemous Deathweaver"
HA          = "Wrathful Harpeia"

A           = "All"
CM          = "Crystal Mine"
AS          = "Ashaq Underground Prison"
DP          = "Demon Prison District"
DN          = "Demon Prison District, no numbers"

loc         = dict()
loc[DW]     = dict()
loc[DW][A]  = re.compile(r'(ashaq|c(rystal)? ?m(ine)?)', re.IGNORECASE)
loc[DW][CM] = re.compile(r'c(rystal)? ?m(ine)?', re.IGNORECASE)
loc[DW][AS] = re.compile(r'ashaq[a-z ]*', re.IGNORECASE)
loc[HA]     = dict()
loc[HA][A]  = re.compile(r'd(emon)? ?p(ris(on?))? ?', re.IGNORECASE)
loc[HA][DP] = re.compile(r'(d ?(ist(rict)?)?)?[125]', re.IGNORECASE)
loc[HA][DN] = re.compile(r'(d ?(ist(rict)?)?)?', re.IGNORECASE)