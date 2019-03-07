import re

MODULE_NAME = 'boss'
COMMAND = '$' + MODULE_NAME

HELP = []
HELP.append(
"""
```
Usage:
    $boss <target> <status> <time> [<channel>] [<map>]
    $boss <target> (<entry> [<channel>] | <query> | <type>)
    $boss help

Examples:
    $boss cerb died 12:00pm mok
        Means: "Violent Cerberus" died in "Mokusul Chamber" at 12:00PM server time.
        Omit channels for field bosses.

    $boss crab died 14:00 ch2
        Means: "Earth Canceril" died in "Royal Mausoleum Constructors' Chapel" at 2:00PM server time.
        You may omit channel for world bosses.

    $boss all erase
        Means: Erase all records unconditionally.

    $boss nuaele list
        Means: List records with "[Demon Lords: Nuaele, Zaura, Blut]".

    $boss rexipher erase
        Means: Erase records with "[Demon Lords: Mirtis, Rexipher, Helgasercle, Marnox]".

    $boss crab maps
        Means: Show maps where "Earth Canceril" may spawn.

    $boss crab alias
        Means: Show aliases for "Earth Canceril", of which "crab" is an alias
```
""")

HELP.append(
"""
```
Options:
    <target>
        This can be either "all" or part of the single boss's name. e.g. "cerb" for "Violent Cerberus"
        "all" will always target all valid bosses for the command. The name (or part of it) will only target that boss.
        Some commands do not work with both. Make sure to check which command can accept what <target>.

    <status>
        This <subcommand> refers to specific conditions related to a boss's spawning.
        Options:
            "died": to refer a known kill
            "anchored": to refer a process known as anchoring for world bosses
        <target> cannot be "all".

    <entry>
        This <subcommand> allows you to manipulate existing records.
        Options:
            "list": to list <target> records
            "erase": to erase <target> records
        <target> can be any valid response.

    <query>
        This <subcommand> supplies info related to a boss.
        Options:
            "maps": to show where <target> may spawn
            "alias": to list possible short-hand aliases, e.g. "ml" for "Noisy Mineloader", to use in <target>
        <target> cannot be "all".

    <type>
        This <subcommand> returns a list of bosses assigned to a type.
        Options:
            "world": bosses that can spawn across all channels in a particular map; they each have a gimmick to spawn
            "event": bosses/events that can be recorded; usually time gimmick-related
            "field": bosses that spawn only in CH 1; they spawn without a separate mechanism/gimmick
            "demon": Demon Lords, which also count as field bosses; they have longer spawn times and the server announces everywhere prior to a spawn
        <target> must be "all".
```
""")

HELP.append(
"""
```
Options (continued):
    <time>
        This refers only to server time. Remember to report in a format like "10:00".
        12/24H formats OK; AM/PM can be omitted but the time will be treated as 24H.
        <target> cannot be "all". Only valid for <status>.

    [<channel>]
        (optional) This is the channel in which the boss was recorded.
        Remember to report in a format like "ch1".
        Omit for all bosses except world bosses. Field boss (including Demon Lords) spawn only in CH 1.
        <target> cannot be "all". Only valid for <status> & <entry>.

    [<map>]
        (optional) This is the map in which the boss was recorded.
        You may use part of the map's name. If necessary, enclose the map's name with quotations.
        Omit for world bosses and situations in which you do not know the last map.
        <target> cannot be "all". Only valid for <status>.

    help
        Prints this page.
```
""")

HELP = 'help'

KW_WORLD = 'world'
KW_EVENT = 'event'
KW_FIELD = 'field'
KW_DEMON = 'Demon Lord'

# sorted by level
BOSS_W_ABOMINATION = 'Abomination'
BOSS_W_TEMPLESHOOTER = 'Earth Templeshooter'
BOSS_W_CANCERIL = 'Earth Canceril'
BOSS_W_ARCHON = 'Earth Archon'
BOSS_W_NECROVENTER = 'Necroventer'
BOSS_W_KUBAS = 'Kubas Event'
BOSS_W_MARIONETTE = 'Marionette'
BOSS_W_DULLAHAN = 'Dullahan Event'

# sorted alphabetically
EVENT_ALEMETH_FLOWER = 'Alemeth Yellow-Eyed Flower Petal'
EVENT_LEGWYN_STONE = 'Legwyn Giant Star Stone'

# sorted by level
BOSS_F_CHAPPARITION = 'Bleak Chapparition'
BOSS_F_GLACKUMAN = 'Rugged Glackuman'
BOSS_F_SUCCUBUS = 'Alluring Succubus'
BOSS_F_VELNIAMONKEY = 'Hungry Velnia Monkey'
BOSS_F_DEATHWEAVER = 'Blasphemous Deathweaver'
BOSS_F_MINELOADER = 'Noisy Mineloader'
BOSS_F_FIRELORD = 'Burning Fire Lord'
BOSS_F_FERRETMARAUDER = 'Forest Keeper Ferret Marauder'
BOSS_F_ELLAGANOS = 'Starving Ellaganos'
BOSS_F_CERBERUS = 'Violent Cerberus'
BOSS_F_HARPEIA = 'Wrathful Harpeia'
BOSS_F_PRISONCUTTER = 'Prison Manager Prison Cutter'
BOSS_F_MOLICH = 'Frantic Molich'

# sorted by "age"
DEMON_LORDS_A = '[Demon Lords: Mirtis, Rexipher, Helgasercle, Marnox]'
DEMON_LORDS_B = '[Demon Lords: Nuaele, Zaura, Blut]'

BOSSES = dict()

BOSSES[KW_WORLD] = [BOSS_W_ABOMINATION,
                    BOSS_W_TEMPLESHOOTER,
                    BOSS_W_CANCERIL,
                    BOSS_W_ARCHON,
                    BOSS_W_NECROVENTER,
                    BOSS_W_KUBAS,
                    BOSS_W_MARIONETTE,
                    BOSS_W_DULLAHAN]

BOSSES[KW_EVENT] = [EVENT_ALEMETH_FLOWER,
                    EVENT_LEGWYN_STONE]

BOSSES[KW_FIELD] = [BOSS_F_CHAPPARITION,
                    BOSS_F_GLACKUMAN,
                    BOSS_F_SUCCUBUS,
                    BOSS_F_VELNIAMONKEY,
                    BOSS_F_DEATHWEAVER,
                    BOSS_F_MINELOADER,
                    BOSS_F_FIRELORD,
                    BOSS_F_FERRETMARAUDER,
                    BOSS_F_ELLAGANOS,
                    BOSS_F_CERBERUS,
                    BOSS_F_HARPEIA,
                    BOSS_F_PRISONCUTTER,
                    BOSS_F_MOLICH]

BOSSES[KW_DEMON] = [DEMON_LORDS_A,
                    DEMON_LORDS_B]

ALL_BOSSES = BOSSES[KW_WORLD] + BOSSES[KW_FIELD] + BOSSES[KW_DEMON]

# bosses that spawn in...
# ...two hours
BOSS_SPAWN_02H = [BOSS_W_ABOMINATION, BOSS_W_DULLAHAN]
# ...seven hours, 30 minutes
BOSS_SPAWN_330 = BOSSES[KW_DEMON]

BOSSES_EVENTS = [BOSS_W_KUBAS, BOSS_W_DULLAHAN] + BOSSES[KW_EVENT]

# use for literal comparisons only
BOSS_SYNONYMS = {BOSS_W_ABOMINATION: ['abom'],

                 BOSS_W_TEMPLESHOOTER: ['temple shooter',
                                        'ts',
                                        'ets',
                                        'templeshooter'],

                 BOSS_W_CANCERIL: ['canceril',
                                   'ec',
                                   'crab'],

                 BOSS_W_ARCHON: ['archon'],

                 BOSS_W_NECROVENTER: ['nv',
                                      'necro'],

                 BOSS_W_KUBAS: ['kubas'],

                 BOSS_W_MARIONETTE: ['marionette',
                                     'mario',
                                     'luigi'],

                 BOSS_W_DULLAHAN: ['dull',
                                   'dulla',
                                   'dullachan'],

                 EVENT_ALEMETH_FLOWER: ['flower'],

                 EVENT_LEGWYN_STONE: ['legwyn',
                                      'crystal'],

                 BOSS_F_CHAPPARITION: ['chap',
                                       'chapparition'],

                 BOSS_F_GLACKUMAN: ['glackuman',
                                    'glack'],

                 BOSS_F_SUCCUBUS: ['succubus',
                                   'succ'],

                 BOSS_F_VELNIAMONKEY: ['velnia monkey',
                                       'monkey',
                                       'velnia',
                                       'velniamonkey'],

                 BOSS_F_DEATHWEAVER: ['deathweaver',
                                      'dw',
                                      'spider'],

                 BOSS_F_MINELOADER: ['ml',
                                     'mineloader'],

                 BOSS_F_FIRELORD: ['fire lord',
                                   'fl',
                                   'firelord'],

                 BOSS_F_FERRETMARAUDER: ['ferret marauder'
                                         'ferret',
                                         'marauder'],

                 BOSS_F_ELLAGANOS: ['ellaganos',
                                    'ella'],

                 BOSS_F_CERBERUS: ['cerberus',
                                   'dog',
                                   'cerb',
                                   'doge'],

                 BOSS_F_HARPEIA: ['harpeia',
                                  'harp',
                                  'harpy',
                                  'harpie'],

                 BOSS_F_PRISONCUTTER: ['prison cutter',
                                       'prison',
                                       'cutter',
                                       'pcutter'],

                 BOSS_F_MOLICH: ['molich',
                                 'molick',
                                 'mo\'lick'],

                 DEMON_LORDS_A: ['mirtis'
                                 'rexipher',
                                 'helgasercle',
                                 'marnox',
                                 'rex',
                                 'goth',
                                 'rexifer',
                                 'racksifur',
                                 'sexipher',
                                 'helga',
                                 'footballhead',
                                 'marn'],

                 DEMON_LORDS_B: ['nuaele',
                                 'zaura',
                                 'blut',
                                 'nuwhale',
                                 'butt'],
                }

BOSS_MAPS = {BOSS_W_ABOMINATION: ['Guards\' Graveyard'],

             BOSS_W_TEMPLESHOOTER: ['Royal Mausoleum Workers\' Lodge'],

             BOSS_W_CANCERIL: ['Royal Mausoleum Constructors\' Chapel'],

             BOSS_W_ARCHON: ['Royal Mausoleum Storage'],

             BOSS_W_NECROVENTER: ['Residence of the Fallen Legwyn Family'],

             BOSS_W_KUBAS: ['Crystal Mine Lot 2 - 2F'],

             BOSS_W_MARIONETTE: ['Roxona Reconstruction Agency East Building'],

             BOSS_W_DULLAHAN: ['Roxona Reconstruction Agency West Building'],

             EVENT_ALEMETH_FLOWER: ['Alemeth Forest'],

             EVENT_LEGWYN_STONE: ['Residence of the Fallen Legwyn Family'],

             BOSS_F_CHAPPARITION: ['Novaha Institute'],

             BOSS_F_GLACKUMAN: ['King\'s Plateau'],

             BOSS_F_SUCCUBUS: ['Feretory Hills'],

             BOSS_F_VELNIAMONKEY: ['Tenants\' Farm'],

             BOSS_F_DEATHWEAVER: ['Demon Prison District 4'],

             BOSS_F_MINELOADER: ['Pilgrim Path'],

             BOSS_F_FIRELORD: ['Mage Tower 5F'],

             BOSS_F_FERRETMARAUDER: ['Uskis Arable Land'],

             BOSS_F_ELLAGANOS: ['Verkti Square'],

             BOSS_F_CERBERUS: ['Mokusul Chamber'],

             BOSS_F_HARPEIA: ['Nahash Forest'],

             BOSS_F_PRISONCUTTER: ['Investigation Room'],

             BOSS_F_MOLICH: ['Tevhrin Stalactite Cave Section 4'],

             DEMON_LORDS_A: ['City Wall District 8',
                             'Inner Wall District 8',
                             'Inner Wall District 9',
                             'Jeromel Park',
                             'Jonael Memorial',
                             'Outer Wall District 9'],

             DEMON_LORDS_B: ['Emmet Forest',
                             'Pystis Forest',
                             'Syla Forest',
                             'Mishekan Forest'],
            }

# Defined behavior for NEAREST_WARPS:
# Key: [Value1, Value2] where
#   Value1 is Nearest Warp Map (same if map has it)
#   Value2 is number of maps away or 0 if same
NEAREST_WARPS = {BOSS_W_ABOMINATION: ['**Guards\' Graveyard**', 0],

                 BOSS_W_TEMPLESHOOTER: ['**Royal Mausoleum Constructors\' Chapel**', 1],

                 BOSS_W_CANCERIL: ['**Royal Mausoleum Constructors\' Chapel**', 0],

                 BOSS_W_ARCHON: ['**Royal Mausoleum Constructors\' Chapel**', 1],

                 BOSS_W_NECROVENTER: ['**Residence of the Fallen Legwyn Family**', 0],

                 BOSS_W_KUBAS: ['**Crystal Mine 3F**', 2],

                 BOSS_W_MARIONETTE: ['**Roxona Reconstruction Agency East Building**', 0],

                 BOSS_W_DULLAHAN: ['**Roxona Reconstruction Agency East Building**', 1],

                 EVENT_ALEMETH_FLOWER: ['**Forest of Prayer**', 1],

                 EVENT_LEGWYN_STONE: ['**Residence of the Fallen Legwyn Family**', 0],

                 BOSS_F_CHAPPARITION: ['**Novaha Institute**', 0],

                 BOSS_F_GLACKUMAN: ['**King\'s Plateau**', 0],

                 BOSS_F_SUCCUBUS: ['**Mochia Forest**', 1],

                 BOSS_F_VELNIAMONKEY: ['**Tenants\' Farm**', 0],

                 BOSS_F_DEATHWEAVER: ['**Demon Prison District 2**', 2],

                 BOSS_F_MINELOADER: ['**Saalus Convent**', 1],

                 BOSS_F_FIRELORD: ['**Mage Tower 5F**', 0],

                 BOSS_F_FERRETMARAUDER: ['**Dina Bee Farm**', 1],

                 BOSS_F_ELLAGANOS: ['**Ruklys Street**', 1],

                 BOSS_F_CERBERUS: ['**Mokusul Chamber**', 0],

                 BOSS_F_HARPEIA: ['**Nahash Forest**', 0],

                 BOSS_F_PRISONCUTTER: ['**Workshop**', 1],

                 BOSS_F_MOLICH: ['**Tevhrin Stalactite Cave Section 5**', 1],

                 DEMON_LORDS_A: [('**Inner Wall District 8**', 0),
                                 ('**Lanko 26 Waters**', 1)],

                 DEMON_LORDS_B: [('**Izoliacjia Plateau**', 1),
                                 ('**Pystis Forest**', 0)],
                }

ACKNOWLEDGED = "Thank you! Your command has been acknowledged and recorded.\n"

MSG_HELP = "Please run `" + COMMAND + " help` for syntax."

# change these to your own emoji
EMOJI_LOC = '<:location:448912251806810112>'
EMOJI_WARP = '<:warp:542445189785190400>'
# change these to your own emoji

CMD_ARG_TARGET = '<target>'
CMD_ARG_STATUS = '<status>'
CMD_ARG_ENTRY = '<entry>'
CMD_ARG_QUERY = '<query>'
CMD_ARG_TYPE = '<type>'
CMD_ARG_SUBCMD = '<subcommand>'

CMD_ARG_TARGET_ALL = 'all'

CMD_ARG_STATUS_DIED = 'died'
CMD_ARG_STATUS_ANCHORED = 'anchored'

CMD_ARG_ENTRY_LIST = 'list'
CMD_ARG_ENTRY_ERASE = 'erase'

CMD_ARG_QUERY_MAPS = 'maps'
CMD_ARG_QUERY_MAPS_NOT = 'N/A'
CMD_ARG_QUERY_ALIAS = 'alias'

REGEX_STATUS_DIED = re.compile(r'(di|kill)(ed)?', re.IGNORECASE)
REGEX_STATUS_ANCHORED = re.compile(r'anch(or(ed)?)?', re.IGNORECASE)

REGEX_ENTRY_LIST = re.compile(r'(show|li?st?)', re.IGNORECASE)
REGEX_ENTRY_ERASE = re.compile(r'(erase|del(ete))?', re.IGNORECASE)

REGEX_QUERY_MAPS = re.compile(r'maps?', re.IGNORECASE)
REGEX_QUERY_ALIAS = re.compile(r'(syn(onym)?s?|alias(es)?)', re.IGNORECASE)

REGEX_TYPE_WORLD = re.compile(r'w(orld)?', re.IGNORECASE)
REGEX_TYPE_FIELD = re.compile(r'f(ield)?', re.IGNORECASE)
REGEX_TYPE_DEMON = re.compile(r'd(emon)?', re.IGNORECASE)

REGEX_OPT_CHANNEL = re.compile(r'(ch?)*.?([1-4])$', re.IGNORECASE)

CMD_USAGE_STATUS = '$boss <target> <status> <time> [<channel>] [<map>]'

RECORD = '{} {} CH {}'
RECORD_KUBAS = '{} {}; Machine of Riddles CH {}'

SUCCESS_STATUS = '{}\n**{}**\n- {} at **{}**\n- {} {} CH {}'

SUCCESS_ENTRY_ERASE = 'our queried records ({}) have successfully been erased.\n'
SUCCESS_ENTRY_ERASE_ALL = 'All of y' + SUCCESS_ENTRY_ERASE
SUCCESS_ENTRY_ERASE = 'Y' + SUCCESS_ENTRY_ERASE

GET_MAPS = '**{}** can be found in the following maps:\n\n' + EMOJI_LOC + ' {}'
GET_BOSSES= 'The following bosses are considered \"**{}**\" bosses:\n\n- {}'

SAME_MAP = 'same map'

FAIL_BAD_DB = "The boss database was corrupt and subsequently rebuilt."
FAIL_STATUS = "Your command could not be processed. It appears this record overlaps too closely with another."
FAIL_STATUS_NO_ANCHOR = "This boss cannot be anchored."

FAIL_ENTRY_ERASE = '*(But **nothing** happened...)*\n'
FAIL_ENTRY_LIST = 'No results found! Try a different boss.\n'

FAIL_INVALID_2 = '{} {} is invalid for `{}`.'
FAIL_INVALID_3 = '{} {} is invalid for `{}` `{}`.'

FAIL_TEMPLATE = "{}\n{}"

TIME_SPAWN_MISSED = 'should have spawned at'
TIME_SPAWN_ONTIME = 'will spawn around'
TIME_SPAWN_EARLY = 'will spawn as early as'

NEAREST = '{}\n\n The nearest'
MAP = 'map'
MAPS = 'maps'
WITH = 'with'
STATUE = 'a Vakarine statue'
STATUES = 'Vakarine statues'
NEAREST_SINGLE = '{} {} {} {}:\n\n'.format(NEAREST, MAP, WITH, STATUE)
NEAREST_PLURAL = '{} {} {} {}:\n\n'.format(NEAREST, MAPS, WITH, STATUES)
MAPAWAY = '{}{}'
MAP_DIST = EMOJI_WARP + ' {} ({})' # map (dist)
MAP_AWAY = 'map away'
MAPS_AWAY = 'maps away'

# Change this according to time difference from your server.
TIME_H_LOCAL_TO_SERVER = 3
TIME_H_SERVER_TO_LOCAL = -3

### DO NOT CHANGE/TRANSLATE THIS SECTION BELOW ###

TIME_STATUS_FIELD = 130
TIME_STATUS_DEMON = 390
TIME_STATUS_WB = 240
TIME_STATUS_ABOM = 120

REGEX_TIME = re.compile(r'[0-2]?[0-9][:.]?[0-5][0-9] ?([ap]m?)*', re.IGNORECASE)
REGEX_TIME_NOON = re.compile(r'^12.*', re.IGNORECASE)
REGEX_TIME_AMPM = re.compile(r'[ap]m?', re.IGNORECASE)
REGEX_TIME_PM = re.compile(r'pm?', re.IGNORECASE)
REGEX_TIME_DELIM = re.compile(r'[:.]')
REGEX_TIME_DIGITS = re.compile(r'^[0-9]{3,4}$')
REGEX_TIME_MINUTES = re.compile(r'.*([0-9]{2})$')

TIME = '{}:{}'

### DO NOT CHANGE/TRANSLATE THIS SECTION ABOVE ###
