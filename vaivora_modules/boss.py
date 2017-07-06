# import additional constants
from datetime import datetime, timedelta
import re
from importlib import import_module as im
import vaivora_constants
for mod in vaivora_constants.modules:
    im(mod)
import vaivora_modules
for mod in vaivora_modules.modules:
    im(mod)

# BGN CONST

module_name     =   "boss"

command         =   []

arg_prefix      =   "[prefix]"
arg_prefix_alt  =   "\"$\", \"Vaivora, \""
arg_module      =   "[module]"
arg_cmd         =   module_name
arg_defcmd      =   "$" + module_name

# options for argument 1
arg_n_1         =   "[target]"
arg_n_1_alt     =   "[boss], all"
arg_n_1_A       =   arg_n_1 + ":(" + arg_n_1_alt + ")"
arg_n_1_B       =   arg_n_1 + ":[boss]" 
arg_n_1_C       =   arg_n_1 + ":all"

# options for argument 2
arg_n_2_A       =   "[status]" # "[died|anchored|warned]"
arg_n_2_A_alt   =   "\"died\", \"anchored\", \"warned\""
arg_n_2_B       =   "[entry]" # "[erase|list]"
arg_n_2_B_alt   =   "\"list\", \"erase\""
arg_n_2_C       =   "[query]" # "[synonyms|maps]"
arg_n_2_C_alt   =   "\"synonyms\", \"maps\""
arg_n_2_D       =   "[type]" # "[world, field]"
arg_n_2_D_alt   =   "\"world\", \"field\""

# options for argument 3
arg_n_3         =   "[time]"

# optional arguments
arg_opt_1       =   "[channel]"
arg_opt_2       =   "[map]"

# auxiliary arguments
arg_help        =   "help"
arg_arg         =   "Argument"
#                   $boss
arg_pre_cmd     =   arg_prefix + arg_cmd


cmd_fragment    =   "```diff\n" + "- " + "[" + arg_defcmd + "] commands" + " -" + "\n" + \
                    "+ Usage" + "```"
command.append(cmd_fragment)

usage           =  "```ini\n"
#                   $boss               [target: boss]      [status command]    [time]              [channel]           [map]
usage           +=  arg_pre_cmd + " " + arg_n_1_B + " " +   arg_n_2_A + " " +   arg_n_3 + " " +     arg_opt_1 + " " +   arg_opt_2 + "\n"
#                   $boss               [target: any]       [entry command]     [map]
usage           +=  arg_pre_cmd + " " + arg_n_1_A + " " +   arg_n_2_B + " " +   arg_opt_2 + "\n"
#                   $boss               [target: boss]      [query command]
usage           +=  arg_pre_cmd + " " + arg_n_1_B + " " +   arg_n_2_C + "\n"
#                   $boss               [target: all]       [type command]
usage           +=  arg_pre_cmd + " " + arg_n_1_C + " " +   arg_n_2_D + "\n"
#                   $boss               help
usage           +=  arg_pre_cmd + " " + arg_help + "\n"
usage           +=  "```"

cmd_fragment    =  usage
command.append(cmd_fragment)

# examples
cmd_fragment    =   "```diff\n" + "+ Examples\n" + "```"
command.append(cmd_fragment)

examples        =   "[$boss cerb died 12:00pm 4f]        ; channel should be omitted for field bosses\n" + \
                    "[Vaivora, boss crab died 14:00 ch2] ; map should be omitted for world bosses\n"

cmd_fragment    =  "```ini\n" + examples
cmd_fragment    += "```"
command.append(cmd_fragment)

# arguments
cmd_fragment    =   "```diff\n" + "+ Arguments \n" + "```"
command.append(cmd_fragment)

# immutable
arg_info        =   list()
arg_info.append("```ini\n")
arg_info.append("Prefix=\"" +   arg_prefix +    "\": " + arg_prefix_alt + "\n" + \
                "; default: [$] or [Vaivora, ]\n" + \
                "This server may have others. Run [$settings get prefix] to check.\n")
arg_info.append("\n---\n\n")
arg_info.append("Module=\"" +   arg_module +    "\": '" + arg_cmd + "'\n" + \
                "; required\n"
                "(always) [" + arg_cmd + "]; goes after prefix. e.g. [$" + arg_cmd + "], [Vaivora, " + arg_cmd + "]\n")
arg_info.append("\n---\n\n")

# target
arg_info.append("Argument=\"" + arg_n_1 +       "\": " + arg_n_1_alt + "\n" + \
                "Opt=\"[boss]\":\n" + \
                "    Either part of, or full name. If spaced, enclose in double-quotes (\").\n" + \
                "Opt=\"all\":\n" + \
                "    For 'all' bosses.\n" + \
                "Some commands only take specific options, so check first.\n")
arg_info.append("\n---\n\n")

# status commands
arg_info.append("Argument=\"" + arg_n_2_A +     "\": " + arg_n_2_A_alt + "\n" + \
                "Opt=\"died\":\n" + \
                "    The boss died or despawned (if field boss).\n" + \
                "Opt=\"anchored\":\n" + \
                "    The world boss was anchored. You or someone else has stayed in the map, leading to spawn.\n" + \
                "Opt=\"warned\":\n" + \
                "    The field boss was warned to spawn, i.e. 'The field boss will appear in awhle.'\n" + \
                "Valid for [target]:[boss] only, to indicate its status.\n" + \
                "Do not use with [entry], [query], or [type] commands.\n")
arg_info.append("\n---\n\n")
arg_info.append("```")

cmd_fragment    =   ''.join(arg_info)
command.append(cmd_fragment)

arg_info        =   list()
arg_info.append("```ini\n")

# entry commands
arg_info.append("Argument=\"" + arg_n_2_B +     "\": " + arg_n_2_B_alt + "\n" + \
                "Opt=\"list\":\n" + \
                "    Lists the entries for the boss you have chosen. If 'all', all records will be printed.\n" + \
                "Opt=\"erase\":\n" + \
                "    Erases the entries matching the boss or 'all'. Optional parameter [map] restricts which records to erase.\n" + \
                "Valid for both [target]:[boss] and [target]:'all' to 'list' or 'erase' entries.\n" + \
                "Do not use with [status], [query], or [type] commands.\n")
arg_info.append("\n---\n\n")

# query commands
arg_info.append("Argument=\"" + arg_n_2_C +     "\": " + arg_n_2_C_alt + "\n" + \
                "Opt=\"synonyms\":\n" + \
                "    Synonyms for the boss to use, for shorthand for [status] and [entry] commands.\n" + \
                "    e.g. 'spider' used in place of 'Blasphemous Deathweaver'\n" + \
                "Opt=\"maps\":\n" + \
                "    Maps for the boss you choose.\n" + \
                "Valid for [target]:[boss] only.\n" + \
                "Do not use with [status], [entry], or [type] commands.\n")
arg_info.append("\n---\n\n")
arg_info.append("```")

cmd_fragment    =   ''.join(arg_info)
command.append(cmd_fragment)

arg_info        =   list()
arg_info.append("```ini\n")

# type commands
arg_info.append("Argument=\"" + arg_n_2_D +     "\": " + arg_n_2_D_alt + "\n" + \
                "Opt=\"world\":\n" + \
                "    Bosses that spawn on specific mechanics and do not wander maps. They can spawn in all channels.\n" + \
                "    Debuffs have no effect on them, and they do not give the 'Field Boss Cube Unobtainable' debuff.\n" + \
                "    Cubes drop loosely on the ground and must be claimed.\n" + \
                "Opt=\"field\":\n" + \
                "    Bosses that spawn in a series of maps, only on Channel 1 in regular periods.\n" + \
                "    If you do not have the 'Field Boss Cube Unobtainable' debuff, upon killing, you obtain it.\n" + \
                "    The debuff lasts 8 hours roughly and you do not need to be online for it to tick down.\n" + \
                "    The debuff prevents you from contributing to other field bosses (no damage contribution),\n" + \
                "    so you cannot provide for your party even if your partymates do not have the debuff.\n" + \
                "    Cubes automatically go into inventory of parties of highest damage contributors.\n" + \
                "Valid for [target]:\"all\" only.\n" + \
                "Do not use with [status], [entry], or [type] commands.\n")
arg_info.append("\n---\n\n")
arg_info.append("```")

cmd_fragment    =   ''.join(arg_info)
command.append(cmd_fragment)

arg_info        =   list()
arg_info.append("```ini\n")

# time
arg_info.append("Argument=\"" + arg_n_3   + "\"\n" + \
                "eg=\"9:00p\"\n" + \
                "eg=\"21:00\"\n" + \
                "    Both these times are equivalent. Make sure to record 'AM' or 'PM' if you're using 12 hour format.\n" + \
                "Required for [status] commands.\n" + \
                "Remove spaces. 12 hour and 24 hour times acceptable, with valid delimiters \":\" and \".\". Use server time.\n")
arg_info.append("\n---\n\n")

# channel
arg_info.append("Argument=\"" + arg_opt_1 + "\"\n" + \
                "eg=\"ch1\"\n" + \
                "eg=\"1\"\n" + \
                "   Both these channels are equivalent. You may drop the 'CH'.\n" + \
                "; optional\n" + \
                "Suitable only for world bosses.[*] If unlisted, CH[1] will be assumed.\n")
arg_info.append("\n---\n\n")

# map
arg_info.append("Argument=\"" + arg_opt_2 + "\"\n" + \
                "eg=\"vid\"\n" + \
                "    Corresponds to 'Videntis Shrine', a map where 'Starving Ellaganos' spawns.\n"
                "; optional\n" + \
                "Suitable only for field bosses.[*] If unlisted, this will be unassumed.\n")
arg_info.append("\n---\n\n")

arg_info.append("[*] ; Notes about world and field bosses:\n" + \
                "    ; Field bosses in channels other than 1 are considered 'world boss' variants,\n" + \
                "    ; and should not be recorded because they spawn unpredictably, because they're jackpot bosses.\n" + \
                "    ; Field bosses with jackpot buffs may also spawn in channel 1 but should not be recorded, either.\n" + \
                "    ; You should record the channel for world bosses because\n" + \
                "    ; they can spawn in any of the channels in their respective maps.\n")
arg_info.append("\n---\n\n")

# help
arg_info.append("Argument=\"" + arg_help + "\"\n" + \
                "Prints this series of messages.\n")
arg_info.append("```")

cmd_fragment    =   ''.join(arg_info)
command.append(cmd_fragment)

arg_min         =   2
arg_max         =   5

acknowledge     =   "Thank you! Your command has been acknowledged and recorded.\n"
msg_help        =   "Please run `" + arg_defcmd + "` for syntax.\n"

pacific2server  =   3
server2pacific  =   -3
time_died       =   4
time_anchored   =   3
time_warned     =   2
time_rel_2h     =   -2
time_rel_16h    =   12

status_died     =   "died"
status_warned   =   "was warned to spawn"
status_anchored =   "was anchored"

# BGN REGEX

prefix      = re.compile(r'(va?i(v|b)ora, |\$)boss', re.IGNORECASE)
rgx_help    = re.compile(r'help', re.IGNORECASE)
rgx_tg_all  = re.compile(r'all', re.IGNORECASE)
rgx_status  = re.compile(r'(di|kill|anchor|warn)(ed)?', re.IGNORECASE)
rgx_st_died = re.compile(r'(di|kill)(ed)?', re.IGNORECASE)
rgx_st_warn = re.compile(r'warn(ed)?', re.IGNORECASE)
rgx_entry   = re.compile(r'(li?st?|erase|del(ete)?|cl(ea)?r)', re.IGNORECASE)
#rgx_list    = re.compile(r'li?st?', re.IGNORECASE)
rgx_erase   = re.compile(r'(erase|del(ete)?|cl(ea)?r)', re.IGNORECASE)
rgx_query   = re.compile(r'(syn(onyms|s)?|alias(es)?|maps?)', re.IGNORECASE)
rgx_q_syn   = re.compile(r'(syn(onyms|s)?|alias(es)?)', re.IGNORECASE)
#rgx_maps    = re.compile(r'maps?', re.IGNORECASE)
rgx_type    = re.compile(r'(wor|fie)ld', re.IGNORECASE)
#rgx_type_w  = re.compile(r'world', re.IGNORECASE)
rgx_type_f  = re.compile(r'field', re.IGNORECASE)
rgx_time    = re.compile(r'[0-2]?[0-9][:.]?[0-5][0-9] ?([ap]m?)*', re.IGNORECASE)
rgx_time_ap = re.compile(r'am?', re.IGNORECASE)
rgx_time_pm = re.compile(r'pm?', re.IGNORECASE)
rgx_time_dl = re.compile(r'[:.]')
rgx_channel = re.compile(r'(ch?)*.?([1-4])$', re.IGNORECASE)
rgx_letters = re.compile(r'[a-z -]+', re.IGNORECASE)


floors_chk  = re.compile(r'[bfd]?[0-9][bfd]?$', re.IGNORECASE)
rgx_floors  = re.compile(r'[^1-5bdf]*((?P<basement>b)|(?P<floor>f))? ?(?P<floornumber>[1-5]) ?((?P=basement)|(?P=floor))?$', re.IGNORECASE)
#floors_fmt  = re.compile(r'[^1-5bdf]*(?P<basement>b)? ?(?P<floornumber>[1-5]) ?(?P<floor>f)?$', re.IGNORECASE)
rgx_loc_az  = re.compile(r'[^1-5bdf]', re.IGNORECASE)

rgx_loc_dw  = re.compile(r'(ashaq|c(rystal)? ?m(ines?)?) ?', re.IGNORECASE)
rgx_loc_dwc = re.compile(r'c(rystal)? ?m(ines?)? ?', re.IGNORECASE)
rgx_loc_dwa = re.compile(r'ashaq[a-z ]*', re.IGNORECASE)
rgx_loc_h   = re.compile(r'd(emon)? ?p(ris(on?))? ?', re.IGNORECASE)
rgx_loc_hno = re.compile(r'(d ?(ist(rict)?)?)?[125]', re.IGNORECASE)
rgx_loc_haz = re.compile(r'(d ?(ist(rict)?)?)?', re.IGNORECASE)

# END REGEX

# BGN BOSS

# 'bosses'
#   list of boss names in full
bosses  =                                           [ 
                                                        'Blasphemous Deathweaver', \
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

bosses_field    =                                   bosses[0:3] + \
                                                    [bosses[7], bosses[9],] + \
                                                    bosses[11:14] + \
                                                    bosses[17:-1]

bosses_world    =                                   [ b for b in bosses if b not in bosses_field ]

# bosses that 'alt'ernate
bosses_alt      =                                   [ 'Mirtis', \
                                                      'Rexipher', \
                                                      'Helgasercle', \
                                                      'Demon Lord Marnox'
                                                    ]

# bosses that spawn in...
# ...two hours
boss_spawn_02h  =                                   [ 
                                                        'Abomination', \
                                                        'Dullahan Event'
                                                    ]
# ...sixteen hours
boss_spawn_16h  =                                   [
                                                        'Demon Lord Nuaele', \
                                                        'Demon Lord Zaura', \
                                                        'Demon Lord Blut'
                                                    ]

# event based timers
bosses_events   =                                   [ 
                                                        'Kubas Event', \
                                                        'Dullahan Event', \
                                                        'Legwyn Crystal Event'
                                                    ]


boss_synonyms = { 'Blasphemous Deathweaver':        [ 
                                                        'dw', \
                                                        'spider', \
                                                        'deathweaver'
                                                    ],
                  'Bleak Chapparition':             [ 
                                                        'chap', \
                                                        'chapparition' 
                                                    ], 
                  'Hungry Velnia Monkey':           [ 
                                                        'monkey', \
                                                        'velnia', \
                                                        'velniamonkey', \
                                                        'velnia monkey' 
                                                    ], 
                  'Abomination':                    [   'abom' ], 
                  'Earth Templeshooter':            [ 
                                                        'temple shooter', \
                                                        'TS', \
                                                        'ETS', \
                                                        'templeshooter' 
                                                    ], 
                  'Earth Canceril':                 [ 
                                                        'canceril', \
                                                        'crab', \
                                                        'ec' 
                                                    ], 
                  'Earth Archon':                   [   'archon' ], 
                  'Violent Cerberus':               [ 
                                                        'cerb', \
                                                        'dog', \
                                                        'doge', \
                                                        'cerberus' 
                                                    ], 
                  'Necroventer':              
                                                    [ 
                                                        'nv', \
                                                        'necro'
                                                    ], 
                  'Forest Keeper Ferret Marauder':  [ 
                                                        'ferret', \
                                                        'marauder'
                                                    ], 
                  'Kubas Event':                    [   'kubas' ], 
                  'Noisy Mineloader':               [ 
                                                        'ml', \
                                                        'mineloader' 
                                                    ], 
                  'Burning Fire Lord':              [ 
                                                        'firelord', \
                                                        'fl', \
                                                        'fire lord' 
                                                    ], 
                  'Wrathful Harpeia':               [ 
                                                        'harp',\
                                                        'harpy', \
                                                        'harpie', \
                                                        'harpeia' 
                                                    ], 
                  'Glackuman':                      [ 
                                                        'glack', \
                                                        'glackuman' 
                                                    ], 
                  'Marionette':                     [ 
                                                        'mario', \
                                                        'marionette' 
                                                    ], 
                  'Dullahan Event':                 [ 
                                                        'dull', \
                                                        'dulla', \
                                                        'dullachan' 
                                                    ], 
                  'Starving Ellaganos':             [ 
                                                        'ella', \
                                                        'ellaganos' 
                                                    ], 
                  'Prison Manager Prison Cutter':   [   'pcutter' ], 
                  'Mirtis':                         [   'mirtis' ], 
                  'Rexipher':                       [ 
                                                        'rex', \
                                                        'rexifer', \
                                                        'racksifur', \
                                                        'sexipher', \
                                                        'goth'
                                                    ], 
                  'Helgasercle':                    [   'helga' ], 
                  'Demon Lord Marnox':              [   
                                                        'marnox',\
                                                        'marn' 
                                                    ], 
                  'Demon Lord Nuaele':              [   'nuaele' ], 
                  'Demon Lord Zaura':               [   'zaura' ], 
                  'Demon Lord Blut':                [ 
                                                        'blut', \
                                                        'butt'
                                                    ], 
                  'Legwyn Crystal Event':           [ 
                                                        'legwyn', \
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
boss_locs = { 'Blasphemous Deathweaver':            [ 
                                                        'Crystal Mine 2F', \
                                                        'Crystal Mine 3F', \
                                                        'Ashaq Underground Prison 1F', \
                                                        'Ashaq Underground Prison 2F', \
                                                        'Ashaq Underground Prison 3F'
                                                    ],
              'Bleak Chapparition':                 [ 
                                                        'Tenet Church B1', \
                                                        'Tenet Church 1F' 
                                                    ],
              'Hungry Velnia Monkey':               [ 
                                                        'Novaha Assembly Hall', \
                                                        'Novaha Annex', \
                                                        'Novaha Institute'
                                                    ],
              'Abomination':                        [   'Guards\' Graveyard'],
              'Earth Templeshooter':                [   'Royal Mausoleum Workers\' Lodge' ],
              'Earth Canceril':                     [   'Royal Mausoleum Constructors\' Chapel' ],
              'Earth Archon':                       [   'Royal Mausoleum Storage' ],
              'Violent Cerberus':                   [ 
                                                        'Royal Mausoleum 4F', \
                                                        'Royal Mausoleum 5F'
                                                    ],
              'Necroventer':                        [   'Residence of the Fallen Legwyn Family' ],
              'Forest Keeper Ferret Marauder':      [ 
                                                        'Bellai Rainforest',
                                                        'Zeraha',
                                                        'Seir Rainforest'
                                                    ],
              'Kubas Event':                        [   'Crystal Mine Lot 2 - 2F' ],
              'Noisy Mineloader':                   [ 
                                                        'Mage Tower 4F', \
                                                        'Mage Tower 5F'
                                                    ],
              'Burning Fire Lord':                  [ 
                                                        'Main Chamber', \
                                                        'Sanctuary'
                                                    ],
              'Wrathful Harpeia':                   [ 
                                                        'Demon Prison District 1', \
                                                        'Demon Prison District 2', \
                                                        'Demon Prison District 5'
                                                    ],
              'Glackuman':                          [   '2nd Demon Prison' ],
              'Marionette':                         [   'Roxona Reconstruction Agency East Building' ],
              'Dullahan Event':                     [   'Roxona Reconstruction Agency West Building' ],
              'Starving Ellaganos':                 [ 
                                                        'Mokusul Chamber', \
                                                        'Videntis Shrine'
                                                    ],
              'Prison Manager Prison Cutter':       [ 
                                                        'Drill Ground of Confliction', \
                                                        'Resident Quarter', \
                                                        'Storage Quarter', \
                                                        'Fortress Battlegrounds'
                                                    ],
              'Mirtis':                             [ 
                                                        'Kalejimas Visiting Room', \
                                                        'Storage', \
                                                        'Solitary Cells', \
                                                        'Workshop', \
                                                        'Investigation Room'
                                                    ],
              'Helgasercle':                        [ 
                                                        'Kalejimas Visiting Room', \
                                                        'Storage', \
                                                        'Solitary Cells', \
                                                        'Workshop', \
                                                        'Investigation Room'
                                                    ],
              'Rexipher':                           [ 
                                                        'Thaumas Trail', \
                                                        'Salvia Forest', \
                                                        'Sekta Forest', \
                                                        'Rasvoy Lake', \
                                                        'Ouaas Memorial'
                                                    ],
              'Demon Lord Marnox':                  [ 
                                                        'Thaumas Trail', \
                                                        'Salvia Forest', \
                                                        'Sekta Forest', \
                                                        'Rasvoy Lake', \
                                                        'Ouaas Memorial'
                                                    ],
              'Demon Lord Nuaele':                  [ 
                                                        'Yudejan Forest', \
                                                        'Nobreer Forest', \
                                                        'Emmet Forest', \
                                                        'Pystis Forest', \
                                                        'Syla Forest', \
                                                        'Mishekan Forest'
                                                    ],
              'Demon Lord Zaura':                   [ 
                                                        'Arcus Forest', \
                                                        'Phamer Forest', \
                                                        'Ghibulinas Forest', \
                                                        'Mollogheo Forest', \
                                                        'Alembique Cave'
                                                    ],
              'Demon Lord Blut':                    [ 
                                                        'Tevhrin Stalactite Cave Section 1', \
                                                        'Tevhrin Stalactite Cave Section 2', \
                                                        'Tevhrin Stalactite Cave Section 3', \
                                                        'Tevhrin Stalactite Cave Section 4', \
                                                        'Tevhrin Stalactite Cave Section 5'
                                                    ],
              'Legwyn Crystal Event':               [   'Residence of the Fallen Legwyn Family' ]
     }

# synonyms for boss locations
boss_loc_synonyms =                                 [ 
                                                        'crystal mine', 'ashaq', \
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

# bosses that spawn in maps with floors or numbered maps
bosses_with_floors    =                             [   
                                                        'Blasphemous Deathweaver', \
                                                        'Bleak Chapparition', \
                                                        'Violent Cerberus', \
                                                        'Noisy Mineloader', \
                                                        'Wrathful Harpeia', \
                                                        'Demon Lord Blut'
                                                    ]

# END BOSS

# END CONST

# @func:    check_boss(str) : int
#     checks boss validity
# @arg:
#     boss : str
#         boss name from raw input
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
def check_maps(boss, maps):
    map_number  = ''
    map_idx     = -1
    
    if boss in bosses_with_floors:
        map_match   = rgx_floors.match(maps)
        map_floor   = map_match.group('floornumber')

    # Deathweaver map did not match
    if boss == "Blasphemous Deathweaver" and not rgx_loc_dw.search(maps):
        return map_idx
    elif boss == "Blasphemous Deathweaver" and rgx_loc_dwc.search(maps):
        tg_map  =   "Crystal Mine " + map_floor
    # process of elimination: Ashaq
    elif boss == "Blasphemous Deathweaver":
        tg_map  =   "Ashaq Underground Prison " + map_floor
    elif boss == "Bleak Chapparition":
        tg_map  =   map_match.group('basement') + map_floor + map_match.group(floor) # one of these must be true, and the other null
    else:
        tg_map  =   maps # default

    if boss in bosses_with_floors and not map_number:
        return map_idx
    
    for boss_map in boss_locs[boss]:
        if re.match(tg_map, boss_map, re.IGNORECASE):
            if map_idx != -1:
                return -1 # too many matches
            map_idx = boss_locs[boss].index(boss_map)

    return map_idx


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

# @func:    process_command(str, list) : list
# @arg:
#       server_id : str
#           id of the server of the originating message
#       msg_channel : str
#           id of the channel of the originating message
#       arg_list : list
#           list of arguments supplied for the command
# @return:
#       an appropriate message for success or fail of command
def process_command(server_id, msg_channel, arg_list):
    # $boss help
    if rgx_help.match(arg_list[0]):
        return command
    arg_len     = len(arg_list)

    # error: not enough arguments
    if arg_len < arg_min or arg_len > arg_max:
        return "You supplied " + arg_len + " arguments; commands must have at least " + \
               arg_min + " or at most " + arg_max + " arguments.\n" + msg_help

    # $boss all ...
    if rgx_tg_all.match(arg_list[0]):
        cmd_boss  = bosses

    # $boss [boss] ...
    else:
        boss_idx  = check_boss(arg_list[0])
        if boss_idx == -1:
            return arg_list[0] + " is invalid for `$boss`. This is a list of bosses you may use:```python\n#   " + \
                   '\n#   '.join(bosses) + "```\n" + msg_help
        cmd_boss  = [bosses[boss_idx], ]

    # error: invalid argument 2
    if not rgx_status.match(arg_list[1]) and \
       not rgx_entry.match(arg_list[1]) and \
       not rgx_query.match(arg_list[1]) and \
       not rgx_type.match(arg_list[1]):
        return arg_list[1] + " is invalid for `$boss`, argument position 2.\n" + msg_help

    # error: invalid [target] argument for argument 2
    # using 'all' with [status]
    if rgx_status.match(arg_list[1]) and len(cmd_boss) != 1:
        return [arg_list[1] + " is invalid for `$boss`:'all', argument position 2.\n" + msg_help]
    # using 'all' with [query]
    if rgx_query.match(arg_list[1]) and len(cmd_boss) != 1:
        return [arg_list[1] + " is invalid for `$boss`:'all' argument position 2.\n" + msg_help]
    # using [boss] with [type]
    if rgx_type.match(arg_list[1]) and len(cmd_boss) <= 1:
        return [arg_list[1] + " is invalid for `$boss`:`" + cmd_boss[0] + "`, argument position 2.\n" + msg_help]
    # no such errors with entry, since entry accepts both [boss] and 'all'

    # $boss [boss] [status] ...
    if rgx_status.match(arg_list[1]):
        return [process_cmd_status(server_id, msg_channel, cmd_boss[0], arg_list[1], arg_list[2], arg_list[3:])]
    # $boss [boss]|all [entry] ...
    elif rgx_entry.match(arg_list[1]) and len(arg_list) == 2:
        return [process_cmd_entry(server_id, msg_channel, cmd_boss, arg_list[1])]
    elif rgx_entry.match(arg_list[1]):
        return [process_cmd_entry(server_id, msg_channel, cmd_boss, arg_list[1], arg_list[2:])]
    # $boss [boss] [query]
    elif rgx_query.match(arg_list[1]):
        return [process_cmd_query(cmd_boss[0], arg_list[1])]
    # $boss all [type]
    else:
        return [process_cmd_type(arg_list[1])]


# @func:    process_cmd_status(str, str, str, str, str, list) : str
# @arg:
#       server_id : str
#           id of the server of the originating message
#       msg_channel : str
#           id of the channel of the originating message
#       boss : str
#           the boss in question
#       status : str
#           the boss's status, or the status command
#       time : str
#           time represented for the associated event
#       opt_list : list
#           list containing optional parameters. may be null.
# @return:
#       an appropriate message for success or fail of command
def process_cmd_status(server_id, msg_channel, tg_boss, status, time, opt_list):
    offset      =   0
    target      =   dict()

    # target - boss
    target['boss']      =   tg_boss # cmd_boss[0] # reassign to 'target boss'
    target['msg_chan']  =   msg_channel
    target['channel']   =   -1

    if len(opt_list) > 0:
        opts                =   process_cmd_opt(opt_list)
        target['map']       =   opts['map']
        target['channel']   =   opts['channel']
    # 3 or fewer arguments
    elif not target['boss'] in bosses_world:
        target['map']       =   "N/A"
        target['channel']   =   1
    else:
        target['map']       =   boss_locs[target['boss']][0]
        target['channel']   =   1


    # $boss [boss] died ...
    if rgx_st_died.match(status):
        time_offset         =   timedelta(hours=time_died)
        target['status']    =   status_died
    # $boss [boss] warned ...
    elif rgx_st_warn.match(status):
        if not target['boss'] in bosses_field:
            return target['boss'] + " is invalid for `$boss`:`time`:`" + status + "`. " + \
                   "Only field bosses have warnings.\n" + msg_help
        time_offset         =   timedelta(hours=time_warned)
        target['status']    =   status_warned
    # $boss [boss] anchored ...
    else:
        if not target['boss'] in bosses_world:
            return target['boss'] + " is invalid for `$boss`:`time`:`" + status + "`. " + \
                   "Only world bosses can be anchored.\n" + msg_help
        time_offset         =   timedelta(hours=time_anchored)
        target['status']    =   status_anchored

    # error: invalid time
    if not rgx_time.match(time):
        return time + " is not a valid time for `$boss`:`time`:`" + status + "`. " + \
               "Use either 12 hour (with AM/PM) or 24 hour time.\n" + msg_help

    # $boss [boss] died [time?]
    # $boss [boss] died [time:am/pm]
    if rgx_time_ap.search(time):
        # $boss [boss] died [time:pm]
        if rgx_time_pm.search(time):
            offset  = 12
        arg_time    = rgx_time_ap.sub('', time)
    else:
        arg_time    = time

    delim   = rgx_time_dl.search(arg_time)
    # $boss [boss] died [time:delimiter]
    if delim:
        hours, minutes  =   [int(t) for t in arg_time.split(delim.group(0))]
        record['hour']  =   hours + offset
    # $boss [boss] died [time:no delimiter]
    else:
        minutes =   int(arg_time[::-1][0:2][::-1])
        hours   =   int(re.sub(str(minutes), '', arg_time))
        record['hour']  =   hours + offset

    # error: invalid hours
    if record['hour'] > 23 or hours < 0:
        return time + " is not a valid time for `$boss`:`time`:`" + status + "`. " + \
               "Use either 12 hour (with AM/PM) or 24 hour time.\n" + msg_help

    # $boss [boss] died [time] ...
    server_date = datetime.now() + timedelta(hours=pacific2server)

    record          =   dict()
    if record['hour'] > int(server_date.hour):
        server_date += timedelta(days=-1) # adjust to one day before, e.g. record on 23:59, July 31st but recorded on August 1st

    # dates handled like above example, e.g. record on 23:59, December 31st but recorded on New Years Day
    record['year']  =   int(server_date.year) 
    record['month'] =   int(server_date.month)
    record['day']   =   int(server_date.day)
    #record['hour']  =   hours
    record['mins']  =   minutes

    # reconstruct boss kill time
    record_date     =   datetime(*record.values())
    record_date     +=  time_offset # value generated by arguments [died, warned, anchored]

    if target['boss'] in boss_spawn_02h:
        record_date +=  timedelta(hours=time_rel_2h) # 2 hour spawn
    elif target['boss'] in boss_spawn_16h:
        record_date +=  timedelta(hours=time_rel_16h) # 16 hour spawn

    # reassign to target data
    target['year']  =   int(record_date.year)
    target['month'] =   int(record_date.month)
    target['day']   =   int(record_date.day)
    target['hour']  =   int(record_date.hour)
    target['mins']  =   int(record_date.minute)

    status = vaivora_modules.db.Database(server_id).update_db_boss(target)

    if status:
        return acknowledge + "```python\n" + \
               "\"" + target['boss'] + "\" " + \
               target['status'] + " at " + \
               ("0" if hours < 10 else "") + \
               str(hour) + ":" + \
               ("0" if minutes < 10 else "") + \
               str(minutes) + \
               ", in ch." + str(target['channel']) + ": " + \
               (("\"" + target['map'] + "\"") if target['map'] != "N?A" else "") + "```\n"
    else:
        return "Your command, `" + ' '.join(arg_list) + "`, could not be processed.\n" + msg_help


# @func:    process_cmd_status(str, str, str, str, str, list) : str
# @arg:
#       server_id : str
#           id of the server of the originating message
#       msg_channel : str
#           id of the channel of the originating message
#       bosses : list
#           the bosses/target in question
#       entry : str
#           the entry command
#       opt_list : list
#           (optional) (default: None)
#           Contains extra parameters 'map' and/or 'channel'
# @return:
#       an appropriate message for success or fail of command
def process_cmd_entry(server_id, msg_channel, tg_bosses, entry, opt_list=None):
    if rgx_erase.match(entry) and not opt_list and tg_bosses == bosses:
        vaivora_modules.db.Database(server_id).rm_entry_db_boss()
        return "Your queried records have successfully been erased.\n"

    # specific bosses to erase, but no options
    elif rgx_erase.match(entry) and not opt_list:
        vaivora_modules.db.Database(server_id).rm_entry_db_boss(tg_bosses)
        return "Your queried records have successfully been erased.\n"

    # implicit non-null opt_list, erase
    elif rgx_erase.match(entry):
        opts                =   process_cmd_opt(opt_list)

        # process opts
        # too many bosses but only one map
        if opts['map'] != "N/A" and len(tg_bosses) > 1:
            return "Your query:`map`, `" + entry + "`, could not be interpreted.\n" + \
                   "You listed a map but selected more than one boss.\n" + msg_help

        # map is not null but channel is
        elif opts['map'] != "N/A" and not opts['channel']:
            vaivora_modules.db.Database(server_id).rm_entry_db_boss(boss_list=tg_bosses, boss_map=opts['map'])
            return "Your queried records have successfully been erased.\n"

        # error: channel other than 1, and boss is field boss
        elif opts['channel'] != 1 and not tg_bosses[0] in bosses_world:
            return "Your query:`channel`, `" + opts['channel'] + "`, could not be interpreted.\n" + \
                   "Field bosses, like `" + tg_bosses[0] + "`, with regular spawn do not spawn in channels other than 1.\n" + msg_help

        # channel is not null but map is
        elif opts['channel'] and opts['map'] == "N/A":
            vaivora_modules.db.Database(server_id).rm_entry_db_boss(boss_list=tg_bosses, boss_ch=opts['channel'])
            return "Your queried records have successfully been erased.\n"

        # implicit catch-all: match with all conditions
        else:
            vaivora_modules.db.Database(server_id).rm_entry_db_boss(boss_list=tg_bosses, boss_ch=opts['channel'], boss_map=opts['map'])
            return "Your queried records have successfully been erased.\n"

    # implicit list
    else:
        valid_boss_records = list()
        valid_boss_records.append("Records:")
        valid_boss_records.append("```python\n")
        boss_records = vaivora_modules.db.Database(server_id).check_db_boss(bosses=tg_bosses) # possible return

        # empty
        if not boss_records: # empty
            return "No results found! Try a different boss.\n"

        for boss_record in boss_records:
            boss_name   =   boss_record[0]
            boss_chan   =   boss_record[1]
            boss_premap =   boss_record[2]
            boss_status =   boss_record[3]
            record_date =   [int(rec) for rec in boss_record[5:10]]
            record_date =   datetime(*record_date)
            # e.g.          "Blasphemous Deathweaver"  died          in ch.      1           and
            # e.g.          "Earth Canceril"           was anchored  in ch.      2           and
            # e.g.          "Demon Lord Marnox"        was warned to spawn in ch.1           and
            ret_message =   "\"" + boss_name + "\" " + boss_status + " in ch." + boss_chan + " and "
            time_diff   = datetime.now() + pacific2server - record_date

            # old records
            if int(time_diff.days) >= 0:
                ret_message +=  "should have respawned at "
                mins_left   =   int(time_diff.seconds)/60 + int(time_diff.days)*86400

            # anchored
            elif boss_status == status_anchored:
                ret_message +=  "will spawn as early as "
                mins_left   =   int((86400-int(time_diff.seconds))/60)

            # warned & died
            else:
                ret_message +=  "will respawn around "
                mins_left   =   int((86400-int(time_diff.seconds))/60)

            # absolute date and time for spawn
            # e.g.              2017/07/06 "14:47"
            ret_message     +=  record_date.strftime("%Y/%m/%d \"%H:%M\"")

            # open parenthesis for minutes
            ret_message +=  " ("
            abs_mins    =   abs(mins_left)

            # print day or days conditionally
            if int(time_diff.days) > 1:
                ret_message     +=  str(time_diff.days) + " days, " 
            elif int(time_diff.days) == 1:
                ret_message     +=  "1 day, "

            # print hour or hours conditionally
            if abs_mins > 119:
                ret_message     +=  str(abs_mins/60) + " hours, "
            elif abs_mins > 59:
                ret_message     +=  "1 hour, "

            # print minutes unconditionally
            # e.g.              0 minutes from now
            # e.g.              59 minutes ago
            ret_message     +=  str(abs_mins%60) + " minutes " + \
                                ("from now" if mins_left < 0 else "ago") + \
                                ") "

            # print extra anchored message conditionally
            if boss_status == status_anchored:
                ret_message     +=  "and as late as one hour later"

            ret_message     += ".\nLast known map: #   " + boss_premap

            valid_boss_records.append(ret_message)

        valid_boss_records.append("```\n")
        return '\n'.join(valid_boss_records)


# @func:    process_cmd_query(str, str, str, str) : str
# @arg:
#       boss : str
#           the boss in question
#       query: str
#           the query command, i.e. aliases or maps
# @return:
#       an appropriate message for success or fail of command
def process_cmd_query(tg_boss, query):
    # $boss [boss] syns
    if rgx_q_syn.match(query):
        return get_syns(tg_boss)
    # $boss [boss] maps
    else:
        return get_maps(tg_boss)


# @func:    process_cmd_query(str, str, str, str) : str
# @arg:
#       btype: str
#           the btype command, i.e. world or field
# @return:
#       an appropriate message for success or fail of command
def process_cmd_type(server_id, msg_channel, btype):
    # $boss all field
    if rgx_type_f.match(btype):
        return get_bosses_field()
    # $boss all world
    else:
        return get_bosses_world()


# @func:    process_cmd_opt(list) : dict
# @arg:
#       opt_list : list
#           any optional parameters, of 1 length or more
# @return:
#       dict containing k:v 'map' and 'channel', both str
def process_cmd_opt(opt_list):
    target  =   dict()
    for cmd_arg in opt_list:
        channel     =   rgx_channel.match(cmd_arg)
        if channel and channel.group(2) != '1' and not target['boss'] in bosses_world:
            return cmd_arg + " is invalid for `$boss`:`channel` because " + target['boss'] + " is a field boss.\n" + \
                   "Field bosses that spawn in channels other than 1 are always jackpot bosses, world boss forms of " + \
                   "the equivalent field boss.\n" + msg_help
        # target - channel
        elif channel and target['boss'] in bosses_world:
            target['channel']   =   int(channel.group(2)) # use channel provided by command
            target['map']       =   boss_locs[target['boss']][0]
        elif not channel and target['boss'] in bosses_field: # possibly map instead
            target['channel']   =   1
            if cmd_arg: # must be map if not null
                map_idx         =   check_maps(target['boss'], cmd_arg)
            # target - map 
            if cmd_arg and map_idx >= 0 and map_idx < len(boss_locs[target['boss']]):
                target['map']   =   boss_locs[target['boss']][map_idx]
            else:
                target['map']   =   "N/A"
    return target

def process_time(hours, minutes, offset):
    pass