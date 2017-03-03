import re
from datetime import datetime, timedelta

# constants
#   constant dictionary
class TOS_CONSTANTS:
    def __init__(self):
        pass

    def con():
        def boss():
            def arg():
                def count():
                    min = 3
                    max = 5
        def files():
            def logger():
                name    = "wings.logger"
                file    = name + ".log"
            debug       = logger.name + "debug.log"
            valid_db    = "wings-valid_db"
            norepeat    = "wings-norepeat"
            welcomed    = "wings-welcomed"
        def time():
            def offset():
                eastern = timedelta(hours=3)
                pacific = timedelta(hours=-3)
                boss02s = timedelta(hours=-2)
                boss04s = timedelta(hours=-4)
                boss16s = timedelta(hours=-16)
            def wait():
                _4hr    = timedelta(hours=4)
                anchor  = timedelta(hours=3)
            def seconds():
                in_day  = 24 * 60 * 60
        def words():
            def message():
                reason  = "Reason: "
                welcome = "Thank you for inviting me to your server! " + \
                            "I am a representative bot for the Wings of Vaivora, here to help you record your journey.\n" + \
                            "\nHere are some useful commands: \n\n" + \
                            '\n'.join(cmd_usage['name']) + \
                            '\n'*2 + \
                            "(To be implemented) Talt, Reminders, and Permissions. Check back soon!\n"
                            # '\n'.join(cmd_usage['talt']) # + \
                            # '\n'.join(cmd_usage['remi']) # + \
                            # '\n'.join(cmd_usage['perm'])
        def error():
            broad   = -1
            wrong   = -2
            syntax  = -127


    #   regular constants
    con = dict()

    #   regex dictionary
    rx = dict()
    rx['format.numbers']        = re.compile(r'^[0-9]{1}$')
    rx['format.letters']        = re.compile(r'[a-z -]+', re.IGNORECASE)
    rx['format.time.pm']        = re.compile(r' ?[Pp][Mm]?', re.IGNORECASE)
    rx['format.time.am']        = re.compile(r' ?[Aa][Mm]?', re.IGNORECASE)
    rx['format.time.delim']     = re.compile(r'[:.]', re.IGNORECASE)
    rx['format.letters.inv']    = re.compile(r'[^A-Za-z0-9 .:$",-]', re.IGNORECASE)
    rx['format.time']           = re.compile(r'[0-2]?[0-9][:.][0-5][0-9]([AaPp][Mm]?)?', re.IGNORECASE)
    rx['format.quotes']         = re.compile(r'"', re.IGNORECASE)
    rx['boss.status']           = re.compile(r'([Dd]ied|[Aa]nchored|[Ww]arn(ed)?)', re.IGNORECASE)
    rx['boss.status.anchor']    = re.compile(r'([Aa]nchored)', re.IGNORECASE)
    rx['boss.status.warning']   = re.compile(r'([Ww]arn(ed)?)', re.IGNORECASE)
    rx['boss.channel']          = re.compile(r'[Cc]([Hh])?[1-4]$', re.IGNORECASE)
    rx['boss.floors']           = re.compile(r'[bfd]?[0-9][bfd]?$', re.IGNORECASE)
    rx['boss.floors.format']    = re.compile(r'.*(?P<basement>b?)(?P<floor>f?)(?P<district>([Dd] ?(ist(rict)?)?)?) ?(?P<floornumber>[0-9]) ?(?P=basement)?(?P=floor)?(?P=district)?$', re.IGNORECASE)
    # rx['boss.floors.arrange']   = re.compile(r'\g<floor>\g<floornumber>\g<basement>', re.IGNORECASE) # cannot precompile
    rx['vaivora.boss']          = re.compile(r'([Vv]a?i(v|b)ora, |\$)boss', re.IGNORECASE)
    rx['boss.arg.all']          = re.compile(r'all', re.IGNORECASE)
    rx['boss.arg.list']         = re.compile(r'li?st?', re.IGNORECASE)
    rx['boss.arg.erase']        = re.compile(r'(erase|del(ete)?)', re.IGNORECASE)
    rx['boss.dw.ambi']          = re.compile(r'([Aa]shaq|[Cc](rystal)? ?[Mm](ine)?)', re.IGNORECASE)
    rx['boss.dw.loc.cm']        = re.compile(r'[Cc](rystal)? ?[Mm](ine)?', re.IGNORECASE)
    rx['boss.dw.loc.ashaq']     = re.compile(r'[Aa]shaq[A-Za-z ]*', re.IGNORECASE)
    rx['boss.hp.loc.dp']        = re.compile(r'[Dd](emon)? ?[Pp](ris(on?))? ?', re.IGNORECASE)
    rx['boss.hp.loc.dp.dist']   = re.compile(r'([Dd] ?(istrict)?)?[125]', re.IGNORECASE)
    rx['boss.hp.loc.dp.dist.n'] = re.compile(r'([Dd] ?(ist(rict)?)?)?', re.IGNORECASE)
    rx['str.ext.db']            = re.compile(r'\.db$', re.IGNORECASE)
    rx['str.fnm.db']            = re.compile(r'[0-9]{18,}')

    #   error(**) related constants
    #     error(**) constants for "command" argument
    cmd                         = dict()
    cmd['name']                 = "Command: Boss"
    # cmd['talt']                 = "Command: Talt Tracker" ####TODO
    # cmd['reminders']            = "Command: Reminders"    ####TODO
    #     error(**) constants for "reason" argument

    reason = dict()
    reason['baddb'] = con['STR.REASON'] + "Bad Database"
    reason['unkwn'] = con['STR.REASON'] + "Unknown"
    reason['broad'] = con['STR.REASON'] + "Broad Command"
    reason['argct'] = con['STR.REASON'] + "Argument Count"
    reason['noanc'] = con['STR.REASON'] + "Cannot Anchor"
    reason['unknb'] = con['STR.REASON'] + "Unknown Boss"
    reason['syntx'] = con['STR.REASON'] + "Malformed Syntax"
    reason['quote'] = con['STR.REASON'] + "Mismatched Quotes"
    reason['bdmap'] = con['STR.REASON'] + "Bad Map"
    reason['bdtme'] = con['STR.REASON'] + "Bad Time"
    reason['fdbos'] = con['STR.REASON'] + "Field Boss Channel"


    def get_constant(con_category, con_subcategory, con_specifier=None):