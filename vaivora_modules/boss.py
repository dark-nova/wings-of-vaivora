# import additional constants
from datetime import datetime, timedelta
from importlib import import_module as im
import vaivora_constants
for mod in vaivora_constants.modules:
    im(mod)

# BGN CONST

module_name     =   "boss"

command         =   []

cmd_frag        =   "```ini\n" + "[$boss] commands" + "\n" + \
                    ";================" + "\n" + \
                    vaivora_constants.command.syntax.heading + "\n"

# N               =   "necessary"
# O               =   "optional"
# H               =   "help"

# A               =   "type A"
# B               =   "type B"
# C               =   "type C"
# D               =   "type D"

arg             =   dict()
arg[N]          =   dict()
arg[N][0]       =   "[prefix]"
arg[N][1]       =   "[boss]"
arg[N][2]       =   dict()
arg[N][2][A]    =   "[boss|all]"
arg[N][2][B]    =   "[boss]"
arg[N][2][C]    =   "[all]"
arg[N][3]       =   dict()
arg[N][3][A]    =   "[died|anchored|warned]"
arg[N][3][B]    =   "[erase|list]"
arg[N][3][C]    =   "[synonyms|maps]"
arg[N][3][D]    =   "[world|field]"
arg[N][4]       =   "[time]"
arg[O]          =   dict()
arg[O][1]       =   "(chN)"
arg[O][2]       =   "(map)"
arg[H]          =   "[help]"

usage           =   arg[N][0] + " " + arg[N][1] + " " + arg[N][2][B] + " " + arg[N][3][A] + " " + arg[N][4] + " " + arg[O][1] + " " + arg[O][2] + " " + "\n" + \
                    arg[N][0] + " " + arg[N][1] + " " + arg[N][2][A] + " " + arg[N][3][B] + " " + arg[O][2] + "\n" + \
                    arg[N][0] + " " + arg[N][1] + " " + arg[N][2][B] + " " + arg[N][3][C] + "\n" + \
                    arg[N][0] + " " + arg[N][1] + " " + arg[N][2][C] + " " + arg[N][3][D] + "\n" + \
                    arg[N][0] + " " + arg[N][1] + " " + arg[N][2][B] + " " + arg[H] + "\n"
usage           +=  vaivora_constants.command.syntax.code_block

cmd_frag        +=  usage
command.append(cmd_frag)

arg_info        =   list()
arg_info.append(vaivora_constants.command.syntax.code_block + "ini\n")
arg_info.append(";================\n")
arg_info.append(arg[N][0] + "\n" + \
                "    (default) [$] or [Vaivora, ]; this server may have others. Run [$settings get prefix] to check.\n")
arg_info.append(arg[N][1] + "\n" + \
                "    (always) [" + modname + "]; goes after prefix. e.g. [$" + modname + "], [Vaivora, " + modname + "]\n")
arg_info.append(arg[N][2][B]  + "\n" + \
                "    Either part of, or full name- if spaced, enclose in double-quotes ([\"])\n" + \
                "    [all] for all bosses\n")
arg_info.append(arg[N][3][A]  + "\n" + \
                "    Valid for [boss] only, to indicate its status.\n" + \
                "    Do not use with [erase], [list], [synonyms], [maps], [world], or [field].\n")
arg_info.append(arg[N][3][B]  + "\n" + \
                "    Valid for both [boss] and [all] to [erase] or [list] entries.\n" + \
                "    Do not use with [died], [anchored], [warned], [synonyms], [maps], [world], or [field].\n")
arg_info.append(arg[N][3][C]  + "\n" + \
                "    Valid for [boss] only, to print aliases of bosses (short-hand) or maps that the boss may wander.\n" + \
                "    Do not use with [died], [anchored], [warned], [erase], [list], [world], or [field].\n")
arg_info.append(arg[N][3][D]  + "\n" + \
                "    Valid for [all] only, to print out either [world bosses] or [field bosses].\n" + \
                "    Do not use with [died], [anchored], [warned], [erase], [list], [synonyms], or [maps].\n")
arg_info.append(arg[N][4]     + "\n" + \
                "; required for [died] and [anchored]\n" + \
                "    Remove spaces. 12 hour and 24 hour times acceptable, with valid delimiters \":\" and \".\". Use server time.\n")
arg_info.append(arg[O][2]     + "\n" + \
                "; optional\n" + \
                "    Suitable only for field bosses.[*] If unlisted, this will be unassumed.\n")
arg_info.append(arg[O][1]     + "\n" + \
                "; optional\n" + \
                "    Suitable only for world bosses.[*] If unlisted, CH[1] will be assumed.\n" + "\n")
arg_info.append("[*] ; Notes about world and field bosses:\n" + \
                "    ; Field bosses in channels other than 1 are considered 'world boss' variants.\n" + \
                "    ; and should not be recorded because they spawn unpredictably, because they're jackpot bosses.\n" + \
                "    ; Field bosses with jackpot buffs may also spawn in channel 1 but should not be recorded, either.\n")
arg_info.append(vaivora_constants.command.syntax.code_block)

cmd_frag        =  ''.join(arg_info)
command.append(cmd_frag)

examples        =   vaivora_constants.command.syntax.example + \
                    "[$boss cerb died 12:00pm 4f]        ; channel should be omitted for field bosses\n" + \
                    "[Vaivora, boss crab died 14:00 ch2] ; map should be omitted for world bosses\n"

cmd_frag        =  vaivora_constants.command.syntax.code_block + "ini\n" + examples
cmd_frag        += vaivora_constants.command.syntax.code_block
command.append(cmd_frag)

arg_min     = 3
arg_max     = 5

arg_del_min = 2
arg_del_max = 3

acknowledge = "Thank you! Your command has been acknowledged and recorded.\n"


# begin boss related variables

# 'bosses'
#   list of boss names in full
bosses  =   [ 'Blasphemous Deathweaver', \
              'Bleak Chapparition', \
              'Hungry Velnia Monkey', \
              'Abomination', \
              'Earth Templeshooter', \
              'Earth Canceril', \
              'Earth Archon', \
              'Violent Cerberus', \
              'Necroventer', \
              'Forest Keeper Ferret Marauder', \
              'Kubas Event', \
              'Noisy Mineloader', \
              'Burning Fire Lord', \
              'Wrathful Harpeia', \
              'Glackuman', \
              'Marionette', \
              'Dullahan Event', \
              'Starving Ellaganos', \
              'Prison Manager Prison Cutter', \
              'Mirtis', \
              'Rexipher', \
              'Helgasercle', \
              'Demon Lord Marnox', \
              'Demon Lord Nuaele', \
              'Demon Lord Zaura', \
              'Demon Lord Blut', \
              'Legwyn Crystal Event' 
            ]

bosses_field    =   bosses[0:3] + \
                    [bosses[7], bosses[9],] + \
                    bosses[11:14] + \
                    bosses[17:-1]

bosses_world    =   [ b for b in bosses if b not in bosses_field ]

# bosses that 'alt'ernate
bosses_alt      =   [ 'Mirtis', \
                      'Rexipher', \
                      'Helgasercle', \
                      'Demon Lord Marnox'
                    ]

boss_spawn_02h  =   [ 'Abomination', \
                      'Dullahan Event'
                    ]

boss_spawn_16h  =   [ 'Demon Lord Nuaele', \
                      'Demon Lord Zaura', \
                      'Demon Lord Blut'
                    ]

bosses_events   =   [ 'Kubas Event', \
                      'Dullahan Event', \
                      'Legwyn Crystal Event'
                    ]


boss_synonyms = { 'Blasphemous Deathweaver':        [ 'dw', \
                                                      'spider', \
                                                      'deathweaver'
                                                    ],
                  'Bleak Chapparition':             [ 'chap', \
                                                      'chapparition' 
                                                    ], 
                  'Hungry Velnia Monkey':           [ 'monkey', \
                                                      'velnia', \
                                                      'velniamonkey', \
                                                      'velnia monkey' 
                                                    ], 
                  'Abomination':                    [ 'abom', \
                                                      'abomination' 
                                                    ], 
                  'Earth Templeshooter':            [ 'temple shooter', \
                                                      'TS', \
                                                      'ETS', \
                                                      'templeshooter' 
                                                    ], 
                  'Earth Canceril':                 [ 'canceril', \
                                                      'crab', \
                                                      'ec' 
                                                    ], 
                  'Earth Archon':                   [ 'archon' ], 
                  'Violent Cerberus':               [ 'cerb', \
                                                      'dog', \
                                                      'doge', \
                                                      'cerberus' 
                                                    ], 
                  'Necroventer':              
                                                    [ 'nv', \
                                                      'necro', \
                                                      'necroventer' 
                                                    ], 
                  'Forest Keeper Ferret Marauder':  [ 'ferret', \
                                                      'marauder'
                                                    ], 
                  'Kubas Event':                    [ 'kubas' ], 
                  'Noisy Mineloader':               [ 'ml', \
                                                      'mineloader' 
                                                    ], 
                  'Burning Fire Lord':              [ 'firelord', \
                                                      'fl', \
                                                      'fire lord' 
                                                    ], 
                  'Wrathful Harpeia':               [ 'harp',\
                                                      'harpy', \
                                                      'harpie', \
                                                      'harpeia' 
                                                    ], 
                  'Glackuman':                      [ 'glack', \
                                                      'glackuman' 
                                                    ], 
                  'Marionette':                     [ 'mario', \
                                                      'marionette' 
                                                    ], 
                  'Dullahan Event':                 [ 'dull', \
                                                      'dulla', \
                                                      'dullachan' 
                                                    ], 
                  'Starving Ellaganos':             [ 'ella', \
                                                      'ellaganos' 
                                                    ], 
                  'Prison Manager Prison Cutter':   [ 'pcutter'
                                                    ], 
                  'Mirtis':                         [ 'mirtis' ], 
                  'Rexipher':                       [ 'rex', \
                                                      'rexifer', \
                                                      'racksifur', \
                                                      'sexipher', \
                                                      'goth'
                                                    ], 
                  'Helgasercle':                    [ 'helga', \
                                                      'helgasercle' 
                                                    ], 
                  'Demon Lord Marnox':              [ 'marnox',\
                                                      'marn' 
                                                    ], 
                  'Demon Lord Nuaele':              [ 'nuaele' ], 
                  'Demon Lord Zaura':               [ 'zaura' ], 
                  'Demon Lord Blut':                [ 'blut' ], 
                  'Legwyn Crystal Event':           [ 'legwyn', \
                                                      'crystal' 
                                                    ]
                }

# only boss synonyms
boss_syns = []
for l in list(boss_synonyms.values()):
    boss_syns.extend(l)

# 'boss location'
# - keys: boss names (var `bosses`)
# - values: list of locations, full name
boss_locs = { 'Blasphemous Deathweaver':        [ 'Crystal Mine 2F', \
                                                  'Crystal Mine 3F', \
                                                  'Ashaq Underground Prison 1F', \
                                                  'Ashaq Underground Prison 2F', \
                                                  'Ashaq Underground Prison 3F'
                                                ],
              'Bleak Chapparition':             [ 'Tenet Church B1', \
                                                  'Tenet Church 1F' 
                                                ],
              'Hungry Velnia Monkey':           [ 'Novaha Assembly Hall', \
                                                  'Novaha Annex', \
                                                  'Novaha Institute'
                                                ],
              'Abomination':                    [ 'Guards\' Graveyard'],
              'Earth Templeshooter':            [ 'Royal Mausoleum Workers\' Lodge' ],
              'Earth Canceril':                 [ 'Royal Mausoleum Constructors\' Chapel' ],
              'Earth Archon':                   [ 'Royal Mausoleum Storage' ],
              'Violent Cerberus':               [ 'Royal Mausoleum 4F', \
                                                  'Royal Mausoleum 5F'
                                                ],
              'Necroventer':                    [ 'Residence of the Fallen Legwyn Family' ],
              'Forest Keeper Ferret Marauder':  [ 'Bellai Rainforest',
                                                  'Zeraha',
                                                  'Seir Rainforest'],
              'Kubas Event':                    [ 'Crystal Mine Lot 2 - 2F' ],
              'Noisy Mineloader':               [ 'Mage Tower 4F', \
                                                  'Mage Tower 5F'
                                                ],
              'Burning Fire Lord':              [ 'Main Chamber', \
                                                  'Sanctuary'
                                                ],
              'Wrathful Harpeia':               [ 'Demon Prison District 1', \
                                                  'Demon Prison District 2', \
                                                  'Demon Prison District 5'
                                                ],
              'Glackuman':                      [ '2nd Demon Prison' ],
              'Marionette':                     [ 'Roxona Reconstruction Agency East Building' ],
              'Dullahan Event':                 [ 'Roxona Reconstruction Agency West Building' ],
              'Starving Ellaganos':             [ 'Mokusul Chamber', \
                                                  'Videntis Shrine'],
              'Prison Manager Prison Cutter':   [ 'Drill Ground of Confliction', \
                                                  'Resident Quarter', \
                                                  'Storage Quarter', \
                                                  'Fortress Battlegrounds'
                                                ],
              'Mirtis':                         [ 'Kalejimas Visiting Room', \
                                                  'Storage', \
                                                  'Solitary Cells', \
                                                  'Workshop', \
                                                  'Investigation Room'
                                                ],
              'Helgasercle':                    [ 'Kalejimas Visiting Room', \
                                                  'Storage', \
                                                  'Solitary Cells', \
                                                  'Workshop', \
                                                  'Investigation Room'
                                                ],
              'Rexipher':                       [ 'Thaumas Trail', \
                                                  'Salvia Forest', \
                                                  'Sekta Forest', \
                                                  'Rasvoy Lake', \
                                                  'Ouaas Memorial'
                                                ],
              'Demon Lord Marnox':              [ 'Thaumas Trail', \
                                                  'Salvia Forest', \
                                                  'Sekta Forest', \
                                                  'Rasvoy Lake', \
                                                  'Ouaas Memorial'
                                                ],
              'Demon Lord Nuaele':              [ 'Yudejan Forest', \
                                                  'Nobreer Forest', \
                                                  'Emmet Forest', \
                                                  'Pystis Forest', \
                                                  'Syla Forest', \
                                                  'Mishekan Forest'
                                                ],
              'Demon Lord Zaura':               [ 'Arcus Forest', \
                                                  'Phamer Forest', \
                                                  'Ghibulinas Forest', \
                                                  'Mollogheo Forest', \
                                                  'Alembique Cave'
                                                ],
              'Demon Lord Blut':                [ 'Tevhrin Stalactite Cave Section 1', \
                                                  'Tevhrin Stalactite Cave Section 2', \
                                                  'Tevhrin Stalactite Cave Section 3', \
                                                  'Tevhrin Stalactite Cave Section 4', \
                                                  'Tevhrin Stalactite Cave Section 5'
                                                ],
              'Legwyn Crystal Event':           [ 'Residence of the Fallen Legwyn Family' ]
     }

boss_loc_synonyms = [ 'crystal mine', 'ashaq', \
                      'tenet', \
                      'novaha', \
                      'guards', 'graveyard', \
                      'maus', 'mausoleum', \
                      'legwyn', \
                      'bellai', 'zeraha', 'seir', \
                      'mage tower', 'mt', \
                      'demon prison', 'dp', \
                      'main chamber', 'sanctuary', 'sanc', \
                      'roxona', \
                      'mokusul', 'videntis', \
                      'drill', 'quarter', 'battlegrounds', \
                      'kalejimas', 'storage', 'solitary', 'workshop', 'investigation', \
                      'thaumas', 'salvia', 'sekta', 'rasvoy', 'oasseu', \
                      'yudejan', 'nobreer', 'emmet', 'pystis', 'syla', \
                      'arcus', 'phamer', 'ghibulinas', 'mollogheo', \
                      'tevhrin'
                    ]

bosses_with_floors    =   [ 'Blasphemous Deathweaver', \
                            'Bleak Chapparition', \
                            'Violent Cerberus', \
                            'Noisy Mineloader', \
                            'Wrathful Harpeia', \
                            'Demon Lord Blut'
                          ]

# END CONST








# @func:    check_boss(str) : int
#   checks boss validity
# @arg:
#     boss: str; boss name from raw input
# @return:
#     boss index in list, or -1 if not found or more than 1 matching
def check_boss(entry):
    match = ''
    for boss in bosses:
        if entry in boss.lower():
            if not match:
                match = boss
            else:
                return -1
    if not match and entry in boss_syns:
        for b, syns in boss_synonyms.items():
            if entry in syns and not match:
                match = b
            elif entry in syns:
                return -1    
    if not match:
        return -1

    return bosses.index(match)

# @func:    check_maps(str, str) : int
#       begin code for checking map validity
# @arg:
#       maps: map name from raw input
#       boss: the corresponding boss, as guaranteed by variable
# @return:
#       map index in list, or -1 if not found or too many maps matched
def check_maps(maps, boss):
    map_number  = ''
    mapidx      = -1
    maps        = maps.lower()
    # Deathweaver map did not match
    if boss == "Blasphemous Deathweaver" and not vaivora_constants.regex.boss.location.DW_A.search(maps):
        return -1

    if boss in bosses_with_floors:
        # rearrange letters, and remove map name
        if boss == "Wrathful Harpeia" or boss == "Demon Lord Blut":
            map_number = vaivora_constants.regex.format.matching.letters.sub('', maps)
            map_number = vaivora_constants.regex.boss.location.floors_arr.sub(r'\g<floornumber>', map_number)
        elif not vaivora_constants.regex.boss.location.floors_fmt.match(maps):
            map_number = vaivora_constants.regex.boss.location.floors_ltr.sub('', maps)
            map_number = vaivora_constants.regex.boss.location.floors_arr.sub(r'\g<basement>\g<floornumber>\g<floor>', map_number)
        else:
            map_number = vaivora_constants.regex.boss.location.floors_ltr.sub('', maps)

    #vaivora_constants.regex.format.matching.letters.sub(map_number)

    if boss == "Blasphemous Deathweaver" and vaivora_constants.regex.boss.location.DW_CM.search(maps):
        maps = "Crystal Mine " + map_number
    elif boss == "Blasphemous Deathweaver":
        maps = "Ashaq Underground Prison " + map_number
    elif map_number:
        maps = map_number
    elif boss in bosses_with_floors and not map_number:
        return -1
    
    maps    = maps.lower()

    for m in boss_locs[boss]:
        if maps in m.lower():
            if mapidx != -1:
                return -1
            mapidx = boss_locs[boss].index(m)

    return mapidx


# @func:    get_syns(str) : str
# @arg:
#       boss: the name of the boss
# @return:
#       a str containing a list of synonyms for boss
def get_syns(boss):
    return boss + " can be called using the following aliases: ```python\n" + \
           "#   " + '\n#   '.join(boss_synonyms[boss]) + "```\n"

# @func:    get_maps(str) : str
# @arg:
#       boss: the name of the boss
# @return:
#       a str containing the list of maps for a boss
def get_maps(boss):
    return boss + " can be found in the following maps: ```python\n" + \
           "#   " + '\n#   '.join(boss_locs[boss]) + "```\n"

# @func:    get_bosses_world() : str
# @return:
#       a str containing the list of world bosses
def get_bosses_world():
    return "The following bosses are considered world bosses: ```python\n" + \
           "#   " + '\n#   '.join(bosses_world) + "```\n"

# @func:    get_bosses_field() : str
# @return:
#       a str containing the list of field bosses
def get_bosses_field():
    return "The following bosses are considered field bosses: ```python\n" + \
           "#   " + '\n#   '.join(bosses_field) + "```\n"

# @func:    validate_channel(str) : int
# @arg:
#       boss: the name of the boss
# @return:
#       the channel parsed, or 1 (default) if ch could not be parsed or incorrect
def validate_channel(ch):
    if vaivora_constants.regex.boss.location.channel.match(ch):
        return int(vaivora_constants.regex.format.matching.letters.sub('', ch))
    else:
        return 1
