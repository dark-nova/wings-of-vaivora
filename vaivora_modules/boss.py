from datetime import datetime, timedelta
import re
import math
from importlib import import_module as im
import vaivora_modules
for mod in vaivora_modules.modules:
    im(mod)
from vaivora_modules.settings import channel_boss as channel_boss
from constants.boss import en_us as lang

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

# Do not adjust 
cmd_fragment    =   ("```diff\n" + "- " + 
                     "[" + arg_defcmd + "] commands" + " -" + "\n" + 
                     "+ Usage" + "```")
command.append(cmd_fragment)

usage           =   "```ini\n"
# Do not adjust /
#                   $boss               [target: boss]      [status command]    [time]              [channel]           [map]
usage           +=  arg_pre_cmd + " " + arg_n_1_B + " " +   arg_n_2_A + " " +   arg_n_3 + " " +     arg_opt_1 + " " +   arg_opt_2 + "\n"
#                   $boss               [target: any]       [entry command]     [map]
usage           +=  arg_pre_cmd + " " + arg_n_1_A + " " +   arg_n_2_B + " " +   arg_opt_2 + "\n"
#                   $boss               [target: boss]      [query command]
usage           +=  arg_pre_cmd + " " + arg_n_1_B + " " +   arg_n_2_C + "\n"
#                   $boss               [target: all]       [type command]
usage           +=  arg_pre_cmd + " " + arg_n_1_C + " " +   arg_n_2_D + "\n"
# Do not adjust 
#                   $module             help
usage           +=  arg_pre_cmd + " " + arg_help + "\n"
usage           +=  "```"

cmd_fragment    =   usage
command.append(cmd_fragment)

acknowledge     =   "Thank you! Your command has been acknowledged and recorded.\n"
msg_help        =   "Please run `" + arg_defcmd + " help` for syntax.\n"
# Do not adjust /

# examples
cmd_fragment    =   "```diff\n" + "+ Examples\n" + "```"
command.append(cmd_fragment)

examples        =   ("[$boss cerb died 12:00pm 4f]\n; channel should be omitted for field bosses\n" + 
                     "[Vaivora, boss crab died 14:00 ch2]\n; map should be omitted for world bosses\n")

cmd_fragment    =   "```ini\n" + examples
cmd_fragment    +=  "```"
command.append(cmd_fragment)

# arguments
cmd_fragment    =   "```diff\n" + "+ Arguments \n" + "```"
command.append(cmd_fragment)

# immutable
arg_info        =   list()
arg_info.append("```ini\n")
arg_info.append("Prefix=\"" +   arg_prefix +    "\": " + arg_prefix_alt + "\n" + 
                "; default: [$] or [Vaivora, ]\n" + 
                "This server may have others. Run [$settings get prefix] to check.\n")
arg_info.append("\n---\n\n")
arg_info.append("Module=\"" +   arg_module +    "\": '" + arg_cmd + "'\n" + 
                "; required\n" + 
                "(always) [" + arg_cmd + "]; goes after prefix. e.g. [$" + arg_cmd + "], [Vaivora, " + arg_cmd + "]\n")
arg_info.append("\n---\n\n")

# target
arg_info.append("Argument=\"" + arg_n_1 +       "\": " + arg_n_1_alt + "\n" + 
                "Opt=\"[boss]\":\n" + 
                "    Either part of, or full name. If spaced, enclose in double-quotes (\").\n" + 
                "Opt=\"all\":\n" + 
                "    For 'all' bosses.\n" + 
                "Some commands only take specific options, so check first.\n")
arg_info.append("\n---\n\n")

# status commands
arg_info.append("Argument=\"" + arg_n_2_A +     "\": " + arg_n_2_A_alt + "\n" + 
                "Opt=\"died\":\n" + 
                "    The boss died or despawned (if field boss).\n" + 
                "Opt=\"anchored\":\n" + 
                "    The world boss was anchored. You or someone else has stayed in the map, leading to spawn.\n" + 
                "Opt=\"warned\":\n" + 
                "    The field boss was warned to spawn, i.e. 'The field boss will appear in awhle.'\n" + 
                "Valid for [target]:[boss] only, to indicate its status.\n" + 
                "Do not use with [entry], [query], or [type] commands.\n")
arg_info.append("\n---\n\n")
arg_info.append("```")


cmd_fragment    =   ''.join(arg_info)
command.append(cmd_fragment)

arg_info        =   list()
arg_info.append("```ini\n")


# entry commands
arg_info.append("Argument=\"" + arg_n_2_B +     "\": " + arg_n_2_B_alt + "\n" + 
                "Opt=\"list\":\n" + 
                "    Lists the entries for the boss you have chosen. If 'all', all records will be printed.\n" + 
                "Opt=\"erase\":\n" + 
                "    Erases the entries matching the boss or 'all'. Optional parameter [map] restricts which records to erase.\n" + 
                "Valid for both [target]:[boss] and [target]:'all' to 'list' or 'erase' entries.\n" + 
                "Do not use with [status], [query], or [type] commands.\n")
arg_info.append("\n---\n\n")

# query commands
arg_info.append("Argument=\"" + arg_n_2_C +     "\": " + arg_n_2_C_alt + "\n" + 
                "Opt=\"synonyms\":\n" + 
                "    Synonyms for the boss to use, for shorthand for [status] and [entry] commands.\n" + 
                "    e.g. 'spider' used in place of 'Blasphemous Deathweaver'\n" + 
                "Opt=\"maps\":\n" + 
                "    Maps for the boss you choose.\n" + 
                "Valid for [target]:[boss] only.\n" + 
                "Do not use with [status], [entry], or [type] commands.\n")
arg_info.append("\n---\n\n")
arg_info.append("```")

cmd_fragment    =   ''.join(arg_info)
command.append(cmd_fragment)

arg_info        =   list()
arg_info.append("```ini\n")

# type commands
arg_info.append("Argument=\"" + arg_n_2_D +     "\": " + arg_n_2_D_alt + "\n" + 
                "Opt=\"world\":\n" + 
                "    Bosses that spawn on specific mechanics and do not wander maps. They can spawn in all channels.\n" + 
                "    Debuffs have no effect on them, and they do not give the 'Field Boss Cube Unobtainable' debuff.\n" + 
                "    Cubes drop loosely on the ground and must be claimed.\n" + 
                "Opt=\"field\":\n" + 
                "    Bosses that spawn in a series of maps, only on Channel 1 in regular periods.\n" + 
                "    Cubes automatically go into inventory of parties of highest damage contributors.\n" + 
                "Valid for [target]:\"all\" only.\n" + 
                "Do not use with [status], [entry], or [type] commands.\n")
arg_info.append("\n---\n\n")
arg_info.append("```")

cmd_fragment    =   ''.join(arg_info)
command.append(cmd_fragment)

arg_info        =   list()
arg_info.append("```ini\n")

# time
arg_info.append("Argument=\"" + arg_n_3   + "\"\n" + 
                "eg=\"9:00p\"\n" + 
                "eg=\"21:00\"\n" + 
                "    Both these times are equivalent. Make sure to record 'AM' or 'PM' if you're using 12 hour format.\n" + 
                "Required for [status] commands.\n" + 
                "Remove spaces. 12 hour and 24 hour times acceptable, with valid delimiters \":\" and \".\". Use server time.\n")
arg_info.append("\n---\n\n")

# channel
arg_info.append("Argument=\"" + arg_opt_1 + "\"\n" + 
                "eg=\"ch1\"\n" + 
                "eg=\"1\"\n" + 
                "   Both these channels are equivalent. You may drop the 'CH'.\n" + 
                "; optional\n" + 
                "Suitable only for world bosses.[*] If unlisted, CH[1] will be assumed.\n")
arg_info.append("\n---\n\n")

# map
arg_info.append("Argument=\"" + arg_opt_2 + "\"\n" + 
                "eg=\"inner 8\"\n" + 
                "    Corresponds to 'Inner Wall District 8', a map where the original set of Demon Lords spawns.\n"
                "; optional\n" + 
                "Suitable only for Demon Lord field bosses.[*] If unlisted, this will be unassumed.\n")
arg_info.append("\n---\n\n")

# Jackpot bosses do not spawn anymore
# arg_info.append("[*] ; Notes about world and field bosses:\n" + 
#                 "    ; Field bosses in channels other than 1 are considered 'world boss' variants,\n" + 
#                 "    ; and should not be recorded because they spawn unpredictably, because they're jackpot bosses.\n" + 
#                 "    ; Field bosses with jackpot buffs may also spawn in channel 1 but should not be recorded, either.\n" + 
#                 "    ; You should record the channel for world bosses because\n" + 
#                 "    ; they can spawn in any of the channels in their respective maps.\n")
# arg_info.append("\n---\n\n")

# help
arg_info.append("Argument=\"" + arg_help + "\"\n" + 
                "Prints this series of messages.\n")
arg_info.append("```")

cmd_fragment    =   ''.join(arg_info)
command.append(cmd_fragment)

arg_min         =   2
arg_max         =   5

# hours!
pacific2server  =   3
server2pacific  =   -3
# minutes!
time_died       =   130
time_died_330   =   390
# hours!
time_died_wb    =   4
time_died_wb_ab =   2
time_anchored   =   3
time_anch_abom  =   1
# minutes!
time_warned     =   10
# hours!
time_rel_2h     =   -2
time_rel_16h    =   12

status_died     =   "died"
status_warned   =   "was warned to spawn"
status_anchored =   "was anchored"


# BGN REGEX

prefix      =   re.compile(r'(va?i(v|b)ora, |\$)boss', re.IGNORECASE)
rgx_help    =   re.compile(r'help', re.IGNORECASE)
rgx_tg_all  =   re.compile(r'all', re.IGNORECASE)
rgx_status  =   re.compile(r'(di|kill|anchor|warn)(ed)?', re.IGNORECASE)
rgx_st_died =   re.compile(r'(di|kill)(ed)?', re.IGNORECASE)
rgx_st_warn =   re.compile(r'(was )?warn(ed)?', re.IGNORECASE)
rgx_st_anch =   re.compile(r'anchor(ed)?', re.IGNORECASE)
rgx_entry   =   re.compile(r'(li?st?|erase|del(ete)?|cl(ea)?r)', re.IGNORECASE)
#rgx_list    =   re.compile(r'li?st?', re.IGNORECASE)
rgx_erase   =   re.compile(r'(erase|del(ete)?|cl(ea)?r)', re.IGNORECASE)
rgx_query   =   re.compile(r'(syn(onyms|s)?|alias(es)?|maps?)', re.IGNORECASE)
rgx_q_syn   =   re.compile(r'(syn(onyms|s)?|alias(es)?)', re.IGNORECASE)
#rgx_maps    =   re.compile(r'maps?', re.IGNORECASE)
rgx_type    =   re.compile(r'((wor|fie)ld|demon)', re.IGNORECASE)
#rgx_type_w  = re.compile(r'world', re.IGNORECASE)
rgx_type_f  =   re.compile(r'field', re.IGNORECASE)
rgx_time    =   re.compile(r'[0-2]?[0-9][:.]?[0-5][0-9] ?([ap]m?)*', re.IGNORECASE)
rgx_time_12 =   re.compile(r'^12.*', re.IGNORECASE)
rgx_time_ap =   re.compile(r'[ap]m?', re.IGNORECASE)
rgx_time_pm =   re.compile(r'pm?', re.IGNORECASE)
rgx_time_dl =   re.compile(r'[:.]')
rgx_time_3d =   re.compile(r'[0-9]{3,4}')
rgx_channel =   re.compile(r'(ch?)*.?([1-4])$', re.IGNORECASE)
rgx_letters =   re.compile(r"[a-z -']+", re.IGNORECASE)
rgx_invalid =   re.compile(r"""[^a-z1-589 ']""", re.IGNORECASE)


rgx_floors  =   re.compile(r'[^1-589bdf]*(?P<basement_pre>b)?(?P<floor_pre>f)?(?P<district_pre>d)? ?(?P<floornumber>[1-589]) ?(?P<basement_post>b)?(?P<floor_post>f)?(?P<district_post>d)?$', re.IGNORECASE)
#floors_fmt  =   re.compile(r'[^1-5bdf]*(?P<basement>b)? ?(?P<floornumber>[1-5]) ?(?P<floor>f)?$', re.IGNORECASE)

rgx_loc_dw  =   re.compile(r'(ashaq|c(rystal)? ?m(ines?)?) ?', re.IGNORECASE)
rgx_loc_dwc =   re.compile(r'c(rystal)? ?m(ines?)? ?', re.IGNORECASE)
rgx_loc_dwa =   re.compile(r'ashaq[a-z ]*', re.IGNORECASE)
rgx_loc_h   =   re.compile(r'd(emon)? ?p(ris(on?))? ?', re.IGNORECASE)
rgx_loc_hno =   re.compile(r'(d ?(ist(rict)?)?)?[125]', re.IGNORECASE)
rgx_loc_haz =   re.compile(r'(d ?(ist(rict)?)?)?', re.IGNORECASE)
rgx_loc_iwd =   re.compile(r'inner', re.IGNORECASE)

# END REGEX

# BGN BOSS

demon_lords_A   =   '[Demon Lords: Mirtis, Rexipher, Helgasercle, Marnox]'
demon_lords_B   =   '[Demon Lords: Nuaele, Zaura, Blut]'

# 'bosses'
#   list of boss names in full
bosses_field    =                                   [ 
                                                        'Bleak Chapparition', 
                                                        'Rugged Glackuman', 
                                                        'Alluring Succubus', 
                                                        'Hungry Velnia Monkey', 
                                                        'Blasphemous Deathweaver', 
                                                        'Noisy Mineloader', 
                                                        'Burning Fire Lord', 
                                                        'Forest Keeper Ferret Marauder', 
                                                        'Starving Ellaganos', 
                                                        'Violent Cerberus', 
                                                        'Wrathful Harpeia', 
                                                        'Prison Manager Prison Cutter', 
                                                        'Frantic Molich'
                                                    ]
bosses_demon    =                                   [
                                                        demon_lords_A, 
                                                        demon_lords_B 
                                                    ]
bosses_world    =                                   [
                                                        'Abomination', 
                                                        'Earth Templeshooter', 
                                                        'Earth Canceril', 
                                                        'Earth Archon', 
                                                        'Necroventer', 
                                                        'Kubas Event', 
                                                        'Marionette', 
                                                        'Dullahan Event', 
                                                        'Legwyn Crystal Event' 
                                                    ]


bosses          =                                   bosses_field + bosses_world + bosses_demon

# shortcut reference
bosses_list             =   dict()
bosses_list['world']    =   bosses_world
bosses_list['field']    =   bosses_field
bosses_list['demon']    =   bosses_demon

# bosses that 'alt'ernate
bosses_alt      =                                   [ 
                                                        'Mirtis', 
                                                        'Rexipher', 
                                                        'Helgasercle', 
                                                        'Demon Lord Marnox'
                                                    ]

# bosses that spawn in...
# ...two hours
boss_spawn_02h  =                                   [ 
                                                        'Abomination', 
                                                        'Dullahan Event'
                                                    ]
# ...seven hours, 30 minutes
boss_spawn_330  =                                   [
                                                        demon_lords_A, 
                                                        demon_lords_B
                                                    ]

# event based timers
bosses_events   =                                   [ 
                                                        'Kubas Event', 
                                                        'Dullahan Event', 
                                                        'Legwyn Crystal Event'
                                                    ]


boss_synonyms   =   {   
                        'Blasphemous Deathweaver':  
                                                    [ 
                                                        'dw', 
                                                        'spider', 
                                                        'deathweaver'
                                                    ],
                        'Bleak Chapparition':       
                                                    [ 
                                                        'chap', 
                                                        'chapparition' 
                                                    ], 
                        'Hungry Velnia Monkey':     
                                                    [ 
                                                        'monkey', 
                                                        'velnia', 
                                                        'velniamonkey', 
                                                        'velnia monkey' 
                                                    ], 
                        'Abomination':              
                                                    [   
                                                        'abom' 
                                                    ], 
                        'Earth Templeshooter':      
                                                    [ 
                                                        'temple shooter', 
                                                        'TS', 
                                                        'ETS', 
                                                        'templeshooter' 
                                                    ], 
                        'Earth Canceril':           
                                                    [ 
                                                        'canceril', 
                                                        'crab', 
                                                        'ec' 
                                                    ], 
                        'Earth Archon':             
                                                    [   
                                                        'archon' 
                                                    ], 
                        'Violent Cerberus':         
                                                    [ 
                                                        'cerb', 
                                                        'dog', 
                                                        'doge', 
                                                        'cerberus' 
                                                    ], 
                        'Necroventer':             
                                                    [ 
                                                        'nv', 
                                                        'necro'
                                                    ], 
                        'Forest Keeper Ferret Marauder':  
                                                    [ 
                                                        'ferret', 
                                                        'marauder'
                                                    ], 
                        'Kubas Event':              
                                                    [   
                                                        'kubas'
                                                    ], 
                        'Noisy Mineloader':         
                                                    [ 
                                                        'ml', 
                                                        'mineloader' 
                                                    ], 
                        'Burning Fire Lord':        [ 
                                                        'firelord', 
                                                        'fl', 
                                                        'fire lord' 
                                                    ], 
                        'Wrathful Harpeia': 
                                                    [ 
                                                        'harp',
                                                        'harpy', 
                                                        'harpie', 
                                                        'harpeia' 
                                                    ], 
                        'Rugged Glackuman':                
                                                    [ 
                                                        'glack', 
                                                        'glackuman' 
                                                    ], 
                        'Marionette':               
                                                    [ 
                                                        'mario', 
                                                        'marionette' 
                                                    ], 
                        'Dullahan Event':                 
                                                    [ 
                                                        'dull', 
                                                        'dulla', 
                                                        'dullachan' 
                                                    ], 
                        'Starving Ellaganos':       
                                                    [ 
                                                        'ella', 
                                                        'ellaganos' 
                                                    ], 
                        'Prison Manager Prison Cutter':   
                                                    [   
                                                        'pcutter'   
                                                    ], 
                        demon_lords_A:             
                                                    [   
                                                        'rex', 
                                                        'rexifer', 
                                                        'racksifur', 
                                                        'sexipher', 
                                                        'goth',
                                                        'helga',
                                                        'footballhead', 
                                                        'marnox',
                                                        'marn' 
                                                    ], 
                        demon_lords_B:                    
                                                    [   
                                                        'nuaele', 
                                                        'nuwhale', 
                                                        'zaura', 
                                                        'blut', 
                                                        'butt'
                                                    ], 
                        'Legwyn Crystal Event':           
                                                    [ 
                                                        'legwyn', 
                                                        'crystal' 
                                                    ],
                        'Alluring Succubus':        
                                                    [   
                                                        'succ'      
                                                    ],
                        'Frantic Molich':           
                                                    [   
                                                        'mo\'lick'    
                                                    ]
                }

# only boss synonyms
boss_syns   =   []
for l in list(boss_synonyms.values()):
    boss_syns.extend(l)

# 'boss location'
# - keys: boss names (var `bosses`)
# - values: list of locations, full name
boss_locs   =       { 
                        'Blasphemous Deathweaver':        
                                                    [ 
                                                        #'Demon Prison District 1', 
                                                        #'Demon Prison District 2', 
                                                        #'Demon Prison District 3', 
                                                        'Demon Prison District 4', 
                                                        #'Demon Prison District 5'
                                                    ],
                        'Bleak Chapparition':                 
                                                    [ 
                                                        #'Absenta Reservoir', 
                                                        #'Karolis Springs', 
                                                        #'Letas Stream', 
                                                        #'Novaha Annex', 
                                                        #'Novaha Assembly Hall', 
                                                        'Novaha Institute', 
                                                        #'Pelke Shrine Ruins' 
                                                    ],
                        'Hungry Velnia Monkey':               
                                                    [ 
                                                        #'Aqueduct Bridge Area', 
                                                        #'Baron Allerno', 
                                                        #'Myrkiti Farm', 
                                                        'Tenants\' Farm'
                                                    ],
                        'Abomination':                        
                                                    [   
                                                        'Guards\' Graveyard'
                                                    ],
                        'Earth Templeshooter':      
                                                    [
                                                        'Royal Mausoleum Workers\' Lodge'
                                                    ],
                        'Earth Canceril':           
                                                    [
                                                        'Royal Mausoleum Constructors\' Chapel'
                                                    ],
                        'Earth Archon':             
                                                    [   
                                                        'Royal Mausoleum Storage'
                                                    ],
                        'Violent Cerberus':         
                                                    [ 
                                                        'Mokusul Chamber', 
                                                        #'Underground Grave of Ritinis', 
                                                        #'Valius\' Eternal Resting Place', 
                                                        #'Videntis Shrine'
                                                    ],
                        'Necroventer':              
                                                    [   
                                                        'Residence of the Fallen Legwyn Family'
                                                    ],
                        'Forest Keeper Ferret Marauder':   
                                                    [ 
                                                        #'Dina Bee Farm', 
                                                        #'Spring Light Woods', 
                                                        'Uskis Arable Land', 
                                                        #'Vilna Forest'
                                                    ],
                        'Kubas Event':                        
                                                    [   
                                                        'Crystal Mine Lot 2 - 2F' 
                                                    ],
                        'Noisy Mineloader':                   
                                                    [ 
                                                        #'Altar Way', 
                                                        #'Apsimesti Crossroads', 
                                                        #'Forest of Prayer', 
                                                        'Pilgrim Path', 
                                                        #'Starving Demon\'s Way'
                                                    ],
                        'Burning Fire Lord':                  
                                                    [ 
                                                        #'Mage Tower 1F', 
                                                        #'Mage Tower 2F', 
                                                        #'Mage Tower 3F', 
                                                        #'Mage Tower 4F', 
                                                        'Mage Tower 5F'
                                                    ],
                        'Wrathful Harpeia':                   
                                                    [ 
                                                        #'Alemeth Forest', 
                                                        #'Barha Forest', 
                                                        #'Elgos Abbey Main Building', 
                                                        #'Elgos Monastery Annex', 
                                                        'Nahash Forest', 
                                                        #'Vera Coast'
                                                    ],
                        'Rugged Glackuman':                          
                                                    [   
                                                        #'Akmens Ridge',
                                                        #'Gateway of the Great King', 
                                                        'King\'s Plateau', 
                                                        #'Overlong Bridge Valley', 
                                                        #'Ramstis Ridge', 
                                                        #'Rukas Plateau', 
                                                        #'Tiltas Valley', 
                                                        #'Zachariel Crossroads'
                                                    ],
                        'Marionette':                         
                                                    [   
                                                        'Roxona Reconstruction Agency East Building' 
                                                    ],
                        'Dullahan Event':                     
                                                    [   
                                                        'Roxona Reconstruction Agency West Building'
                                                    ],
                        'Starving Ellaganos':                 
                                                    [ 
                                                        #'Downtown', 
                                                        #'Inner Enceinte District', 
                                                        #'Roxona Market', 
                                                        #'Ruklys Street', 
                                                        'Verkti Square'
                                                    ],
                        'Prison Manager Prison Cutter':       
                                                    [ 
                                                        #'Solitary Cells', 
                                                        #'Workshop', 
                                                        'Investigation Room'
                                                    ],
                        demon_lords_A:              
                                                    [ 
                                                        'City Wall District 8', 
                                                        'Inner Wall District 8', 
                                                        'Inner Wall District 9', 
                                                        'Jeromel Park', 
                                                        'Jonael Memorial', 
                                                        'Outer Wall District 9'
                                                    ],
                        demon_lords_B:                        
                                                    [ 
                                                        'Emmet Forest', 
                                                        'Pystis Forest', 
                                                        'Syla Forest', 
                                                        'Mishekan Forest'
                                                    ],
                        'Legwyn Crystal Event':     
                                                    [   
                                                        'Residence of the Fallen Legwyn Family'
                                                    ],
                        'Alluring Succubus':        
                                                    [   
                                                        #'Mochia Forest', 
                                                        'Feretory Hills', 
                                                        #'Sutatis Trade Route'
                                                    ],
                        'Frantic Molich':                     
                                                    [
                                                        #'Tevhrin Stalactite Cave Section 1', 
                                                        #'Tevhrin Stalactite Cave Section 2', 
                                                        #'Tevhrin Stalactite Cave Section 3', 
                                                        'Tevhrin Stalactite Cave Section 4', 
                                                        #'Tevhrin Stalactite Cave Section 5'
                                                    ]

            }



# # bosses that spawn in maps with floors or numbered maps
# bosses_with_floors      =                           [   
#                                                         'Blasphemous Deathweaver', 
#                                                         'Burning Fire Lord', 
#                                                         'Frantic Molich'
#                                                     ] # obsoleted

bosses_with_floors      =                           [   
                                                        demon_lords_A
                                                    ]




# END BOSS

# END CONST

def help():
    """
    :func:`help` returns help for this module.

    Returns:
        a list of detailed help messages
    """
    return lang.HELP


def what_status(entry):
    """
    :func:`what_status` checks what "status" the input may be.
    "Statuses" are defined to be "died" and "anchored".

    Args:
        entry (str): the string to check for "status"

    Returns:
        str: the correct "status" if successful
        None: if unsuccessful
    """
    if lang.REGEX_STATUS_DIED.match(entry):
        return lang.CMD_ARG_STATUS_DIED
    elif lang.REGEX_STATUS_ANCHORED.match(entry):
        return lang.CMD_ARG_STATUS_ANCHORED
    elif lang.REGEX_STATUS_WARNED.match(entry):
        return lang.CMD_ARG_STATUS_WARNED
    else:
        return None


def what_entry(entry):
    """
    :func:`what_entry` checks what "entry" the input may be.
    "Entries" are defined to be "maps" and "alias".

    Args:
        entry (str): the string to check for "query"

    Returns:
        str: the correct "entry" if successful
        None: if unsuccessful
    """    
    if lang.REGEX_ENTRY_LIST.match(entry):
        return lang.CMD_ARG_ENTRY_LIST
    elif lang.REGEX_ENTRY_ERASE.match(erase):
        return lang.CMD_ARG_ENTRY_ERASE
    else:
        return None


def what_query(entry):
    """
    :func:`what_query` checks what "query" the input may be.
    "Queries" are defined to be "maps" and "alias".

    Args:
        entry (str): the string to check for "query"

    Returns:
        str: the correct "query" if successful
        None: if unsuccessful
    """
    if lang.REGEX_QUERY_MAPS.match(entry):
        return lang.CMD_ARG_QUERY_MAPS
    elif lang.REGEX_QUERY_ALIAS.match(entry):
        return lang.CMD_ARG_QUERY_ALIAS
    else:
        return None


def what_type(entry):
    """
    :func:`what_type` checks what "type" the input may be.
    "Types" are defined to be "world", "event", "field", and "demon".

    Args:
        entry (str): the string to check for "type"

    Returns:
        str: the correct "type" if successful
        None: if unsuccessful
    """
    if entry == lang.KW_WORLD or entry == lang.KW_EVENT or entry == lang.KW_FIELD:
        return entry
    elif re.search(entry, lang.KW_DEMON.lower(), re.IGNORECASE):
        return lang.KW_DEMON
    else:
        return None


def check_boss(entry):
    """
    :func:`check_boss` checks whether an input string is a valid boss.

    Args:
        entry (str): the string to check for valid boss

    Returns:
        int: the boss index if valid and matching just one; otherwise, -1
    """
    match = None
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


def check_maps(boss, maps):
    """
    :func:`check_maps` checks whether a string refers to a valid map.

    Args:
        boss (str): the valid boss to check
        maps (str): the string to check for valid map

    Returns:
        int: the map index if valid and matching just one; otherwise, -1
    """
    map_idx     =   -1
    map_floor   =   0
    map_match   =   None

    # currently a specific case with floors: Inner Wall District [8-9]
    if boss in bosses_with_floors and rgx_loc_iwd.search(maps):
        map_match   = rgx_floors.search(maps)
        if not map_match:
            return -1
    
    if map_match: # and boss in bosses_with_floors
        map_floor   =   map_match.group('floornumber')
        # extract target map string
        target_map  =   re.sub(map_floor, '', maps)

    # default case; includes bosses in bosses_with_floors but unnumbered map
    else:
        target_map  =   maps

    for boss_map in boss_locs[boss]:
        if re.search(target_map, boss_map, re.IGNORECASE):
            if map_floor and not re.search(map_floor, boss_map, re.IGNORECASE):
                continue
            # multiple matched; invalid
            if map_idx != -1:
                return -1
            map_idx =   boss_locs[boss].index(boss_map)

    return map_idx


def get_syns(boss):
    """
    :func:`get_syns` gets the synonyms of a valid boss.

    Args:
        boss (str): the string to get the boss's synonyms

    Returns:
        str: a formatted markdown message with synonyms
    """
    return ("**" + boss + "** can be called using the following aliases: ```python\n" + 
            "#   " + '\n#   '.join(boss_synonyms[boss]) + "```\n")


def get_maps(boss):
    """
    :func:`get_maps` gets the maps of a valid boss.

    Args:
        boss (str): the valid boss to get maps

    Returns:
        str: a formatted markdown message with maps for a boss
    """
    return ("**" + boss + "** can be found in the following maps: ```python\n" + 
            "#   " + '\n#   '.join(boss_locs[boss]) + "```\n")


def get_bosses(boss_type):
    """
    :func:`get_bosses` gets the bosses of a certain boss type.

    Args:
        boss_type (str): the type of the boss

    Returns:
        str: a formatted markdown message with bosses of the specified type
    """
    return ("The following bosses are considered \"" + boss_type + "\" bosses: ```python\n" + 
            "#   " + '\n#   '.join(bosses_list[boss_type]) + "```")


def validate_channel(ch):
    """
    :func:`validate_channel` validates a channel string.

    Args:
        ch (str): the channel as string input by user

    Returns:
        int: the channel parsed, or 1 (default) if `ch` could not be parsed or was incorrect
    """
    if rgx_channel.match(ch):
        return int(rgx_letters.sub('', ch))
    else:
        return 1


def process_command(server_id, msg_channel, arg_list):
    """
    :func:`process_command` processes a boss command input by the user.

    Args:
        server_id (str): the id of the server of the originating message
        msg_channel (str): the id of the channel of the originating message (belonging to server of `server_id`)
        arg_list (list): the list of arguments supplied for the command, all str

    Returns:
        str: an appropriate message for success or fail of command
    """
    if not vaivora_modules.settings.Settings(server_id).is_ch_type(msg_channel, channel_boss):
        return [""] # silently deny

    # $boss help
    if rgx_help.match(arg_list[0]):
        return command
    arg_len     = len(arg_list)

    # error: not enough arguments
    if arg_len < arg_min or arg_len > arg_max:
        return ["You supplied " + str(arg_len) + " arguments; commands must have at least " + 
                str(arg_min) + " or at most " + str(arg_max) + " arguments.\n" + msg_help]

    # $boss all ...
    if rgx_tg_all.match(arg_list[0]):
        cmd_boss    =   bosses

    # $boss [boss] ...
    else:
        boss_idx  = check_boss(arg_list[0])
        if boss_idx == -1:
            return arg_list[0].split(' ')[0]
            # return arg_list[0] + " is invalid for `$boss`. This is a list of bosses you may use:```python\n#   " + 
            #        '\n#   '.join(bosses) + "```\n" + msg_help
        cmd_boss    =   [bosses[boss_idx], ]

    # error: invalid argument 2
    if (not rgx_status.match(arg_list[1]) and 
        not rgx_entry.match(arg_list[1]) and 
        not rgx_query.match(arg_list[1]) and 
        not rgx_type.match(arg_list[1])):
        return ["\"" + arg_list[1] + "\" is invalid for `$boss`, argument position 2.\n" + msg_help]

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
        try:
            return [process_cmd_status(server_id, msg_channel, cmd_boss[0], arg_list[1], arg_list[2], arg_list[3:])]
        except:
            return ["You supplied " + str(arg_len) + " arguments; commands must have at least " + 
                    str(arg_min) + " or at most " + str(arg_max) + " arguments.\n" + msg_help]
    # $boss [boss]|all [entry] ...
    elif rgx_entry.match(arg_list[1]) and len(arg_list) == 2:
        return process_cmd_entry(server_id, msg_channel, cmd_boss, arg_list[1])
    elif rgx_entry.match(arg_list[1]):
        return process_cmd_entry(server_id, msg_channel, cmd_boss, arg_list[1], arg_list[2:])
    # $boss [boss] [query]
    elif rgx_query.match(arg_list[1]):
        return [process_cmd_query(cmd_boss[0], arg_list[1])]
    # $boss all [type]
    elif rgx_type.match(arg_list[1]):
        return [process_cmd_type(arg_list[1])]
    else:
        return arg_list[1] + " is invalid for `$boss`, argument position 2.\n" + msg_help


def process_cmd_status(server_id, msg_channel, tg_boss, status, time, opt_list):
    """
    :func:`process_cmd_status` processes a specific boss command: status related to recording.

    Args:
        server_id (str): the id of the server of the originating message
        msg_channel (str): the id of the channel of the originating message (belonging to server of `server_id`)
        boss (str): the boss in question
        status (str): the boss's status, or the status command
        time (str): time represented for the associated event
        opt_list (list): a list containing optional parameters; may be null

    Returns:
        str: an appropriate message for success or fail of command, e.g. boss data recorded
    """
    offset      =   0
    target      =   dict()

    # target - boss
    target['boss']          =   tg_boss # cmd_boss[0] # reassign to 'target boss'
    target['text_channel']  =   msg_channel
    target['channel']       =   -1

    if len(opt_list) > 0:
        opts                =   process_cmd_opt(opt_list, tg_boss)
        target['map'], target['channel']    = opts
    # 3 or fewer arguments
    elif target['boss'] in bosses_demon:
        target['map']       =   "N/A"
        target['channel']   =   1
    else:
        target['map']       =   boss_locs[target['boss']][0]
        target['channel']   =   1


    # $boss [boss] died ...
    if (rgx_st_died.match(status) and not target['boss'] in boss_spawn_330 and 
        not target['boss'] in boss_spawn_02h and not target['boss'] in bosses_world):
        time_offset         =   timedelta(minutes=time_died)
        target['status']    =   status_died
    elif rgx_st_died.match(status) and target['boss'] == "Abomination":
        time_offset         =   timedelta(hours=time_died_wb_ab)
        target['status']    =   status_died
    elif rgx_st_died.match(status) and target['boss'] in bosses_world:
        time_offset         =   timedelta(hours=time_died_wb)
        target['status']    =   status_died
    elif rgx_st_died.match(status) and target['boss'] in boss_spawn_330:
        time_offset         =   timedelta(minutes=time_died_330)
        target['status']    =   status_died
    elif rgx_st_died.match(status):
        time_offset         =   timedelta(hours=2)
        target['status']    =   status_died
    # $boss [boss] warned ...
    elif rgx_st_warn.match(status):
        if target['boss'] in bosses_world:
            return (target['boss'] + " is invalid for `$boss`: `time`: `" + status + "`. " + 
                    "Only field bosses have warnings.\n" + msg_help)
        time_offset         =   timedelta(minutes=time_warned)
        target['status']    =   status_warned
    # $boss [boss] anchored ...
    elif rgx_st_anch.match(status) and tg_boss == "Abomination":
        time_offset         =   timedelta(hours=time_anch_abom)
        target['status']    =   status_anchored
    else:
        if not target['boss'] in bosses_world:
            return (target['boss'] + " is invalid for `$boss`: `time`: `" + status + "`. " + 
                    "Only world bosses can be anchored.\n" + msg_help)
        time_offset         =   timedelta(hours=time_anchored)
        target['status']    =   status_anchored

    # error: invalid time
    if not rgx_time.match(time) and not rgx_time_3d.match(time):
        return (time + " is not a valid time for `$boss`: `time`: `" + status + "`. " + 
                "Use either 12 hour (with AM/PM) or 24 hour time.\n" + msg_help)

    # $boss [boss] died [time?]
    # $boss [boss] died [time:am/pm]
    if rgx_time_ap.search(time):
        # $boss [boss] died [time:pm]
        if rgx_time_pm.search(time):
            offset  = 12
        elif rgx_time_12.match(time):
            offset  = -12
        arg_time    = rgx_time_ap.sub('', time)
    else:
        arg_time    = time

    delim   = rgx_time_dl.search(arg_time)
    record  = dict()
    # $boss [boss] died [time:delimiter]
    if delim:
        hours, minutes  =   [int(t) for t in arg_time.split(delim.group(0))]
        temp_hour       =   hours + offset
    # $boss [boss] died [time:no delimiter]
    else:
        minutes         =   int(arg_time[::-1][0:2][::-1])
        hours           =   int(re.sub(str(minutes), '', arg_time))
        temp_hour       =   hours + offset

    if hours == 12 and offset == 12:
        temp_hour   =   hours

    # error: invalid hours
    if temp_hour > 24 or hours < 0:
        return (time + " is not a valid time for `$boss` : `time` : `" + status + "`. " + 
                "Use either 12 hour (with AM/PM) or 24 hour time.\n" + msg_help)

    # $boss [boss] died [time] ...
    server_date = datetime.now() + timedelta(hours=pacific2server)

    if temp_hour > int(server_date.hour):
        server_date += timedelta(days=-1) # adjust to one day before, e.g. record on 23:59, July 31st but recorded on August 1st

    # dates handled like above example, e.g. record on 23:59, December 31st but recorded on New Years Day
    record['year']  =   int(server_date.year) 
    record['month'] =   int(server_date.month)
    record['day']   =   int(server_date.day)
    record['hour']  =   temp_hour
    record['mins']  =   minutes

    # reconstruct boss kill time
    record_date     =   datetime(*record.values())
    record_date     +=  time_offset # value generated by arguments [died, warned, anchored]

    # if target['boss'] in boss_spawn_02h:
    #     record_date +=  timedelta(hours=time_rel_2h) # 2 hour spawn
    # elif target['boss'] in boss_spawn_330:
    #     record_date +=  timedelta(minutes=time_died_330) # 7h20m spawn

    # reassign to target data
    target['year']  =   int(record_date.year)
    target['month'] =   int(record_date.month)
    target['day']   =   int(record_date.day)
    target['hour']  =   int(record_date.hour)
    target['mins']  =   int(record_date.minute)

    status = vaivora_modules.db.Database(server_id).update_db_boss(target)

    if status:
        return (acknowledge + "```python\n" + 
                "\"" + target['boss'] + "\" " + 
                target['status'] + " at " + 
                ("0" if temp_hour < 10 else "") + 
                str(temp_hour) + ":" + 
                ("0" if minutes < 10 else "") + 
                str(minutes) + 
                ", in ch." + str(target['channel']) + ": " + 
                (("\"" + target['map'] + "\"") if target['map'] != "N/A" else "") + "```\n")
    else:
        return "Your command could not be processed. It appears this record overlaps too closely with another.\n" + msg_help


def process_cmd_entry(server_id, msg_channel, tg_bosses, entry, opt_list=None):
    """
    :func:`process_cmd_entry` processes a specific boss command: entry to retrieve records.

    Args:
        server_id (str): the id of the server of the originating message
        msg_channel (str): the id of the channel of the originating message (belonging to server of `server_id`)
        bosses (list): a list of bosses to check
        entry (str): the entry command (list, erase)
        opt_list (list): (default: None) a list containing optional parameters; may be null; 'map' or 'channel' may be provided

    Returns:
        str: an appropriate message for success or fail of command, e.g. confirmation or list of entries
    """
    # all bosses, no options
    if rgx_erase.match(entry) and not opt_list and tg_bosses == bosses:
        if vaivora_modules.db.Database(server_id).rm_entry_db_boss():
            return "All records have successfully been erased.\n"
        else:
            return "*(But **nothing** happend...)*\n"
    # specific bosses to erase, but no options
    elif rgx_erase.match(entry) and not opt_list:
        recs    =   vaivora_modules.db.Database(server_id).rm_entry_db_boss(tg_bosses)

    # implicit non-null opt_list, erase
    elif rgx_erase.match(entry) and len(tg_bosses) == 1:
        opts    =   process_cmd_opt(opt_list, tg_bosses[0])

        # process opts
        # too many bosses but only one map
        if opts[0] != "N/A" and len(tg_bosses) > 1:
            return ("Your query:`map`, `" + entry + "`, could not be interpreted.\n" + 
                    "You listed a map but selected more than one boss.\n" + msg_help)

        # map is not null but channel is
        elif opts[0] != "N/A" and not opts[1]:
            recs    =   vaivora_modules.db.Database(server_id).rm_entry_db_boss(bosses_list=tg_bosses, boss_map=opts[0])
            
        # error: channel other than 1, and boss is field boss
        elif opts[0] != 1 and not tg_bosses[0] in bosses_world:
            return ("Your query:`channel`, `" + opts[1] + "`, could not be interpreted.\n" + 
                    "Field bosses, like `" + tg_bosses[0] + "`, with regular spawn do not spawn in channels other than 1.\n" + msg_help)

        # channel is not null but map is
        elif opts[0] and opts[1] == "N/A":
            recs    =   vaivora_modules.db.Database(server_id).rm_entry_db_boss(bosses_list=tg_bosses, boss_ch=opts[1])
            
        # implicit catch-all: match with all conditions
        else:
            recs    =   vaivora_modules.db.Database(server_id).rm_entry_db_boss(bosses_list=tg_bosses, boss_ch=opts[1], boss_map=opts[0])
            
    elif rgx_erase.match(entry):
        if vaivora_modules.db.Database(server_id).rm_entry_db_boss():
            return "All records have successfully been erased.\n"
        else:
            return "*(But **nothing** happend...)*\n"

    if rgx_erase.match(entry) and recs:
        return "Your queried records (" + str(recs) + ") have successfully been erased.\n"
    elif rgx_erase.match(entry) and not recs:
        return "*(But nothing happened...)*\n"

    if not rgx_erase.match(entry):
        valid_boss_records = list()
        valid_boss_records.append("Records:")
        #valid_boss_records.append("```python\n")
        boss_records = vaivora_modules.db.Database(server_id).check_db_boss(bosses=tg_bosses) # possible return

        # empty
        if not boss_records: # empty
            return "No results found! Try a different boss.\n"

        for boss_record in boss_records:
            boss_name   =   boss_record[0]
            boss_chan   =   str(math.floor(boss_record[1]))
            boss_premap =   boss_record[2]
            boss_status =   boss_record[3]
            # year, month, day, hour, minutes
            record_date =   [int(rec) for rec in boss_record[5:10]]
            record_date =   datetime(*record_date)
            # e.g.          "Blasphemous Deathweaver"  died          in ch.      1           and
            # e.g.          "Earth Canceril"           was anchored  in ch.      2           and
            # e.g.          "Demon Lord Marnox"        was warned to spawn in ch.1           and
            ret_message =   "\"" + boss_name + "\" " + boss_status + " in ch." + boss_chan + " and "
            time_diff   = datetime.now() + timedelta(hours=pacific2server) - record_date

            if int(time_diff.days) >= 0 and boss_status != status_anchored:
                ret_message +=  "should have respawned at "
                mins_left   =   math.floor(time_diff.seconds/60) + int(time_diff.days)*86400

            # anchored
            elif boss_status == status_anchored and int(time_diff.days) < 0:
                ret_message +=  "will spawn as early as "
                mins_left   =   math.floor((86400-int(time_diff.seconds))/60)

            elif boss_status == status_anchored and int(time_diff.days) >= 0:
                ret_message +=  "could have spawned at "
                mins_left   =   math.floor(time_diff.seconds/60) + int(time_diff.days)*86400

            # died
            elif boss_status == status_died:
                ret_message +=  "will respawn around "
                mins_left   =   math.floor((86400-int(time_diff.seconds))/60)

            # warned
            else:
                ret_message +=  "will spawn at "
                mins_left   =   math.floor((86400-int(time_diff.seconds))/60)

            # absolute date and time for spawn
            # e.g.              2017/07/06 "14:47"
            ret_message     +=  record_date.strftime("%Y/%m/%d %H:%M")

            # open parenthesis for minutes
            ret_message +=  " ("
            if mins_left >= 0:
                abs_mins    =   abs(mins_left)
            else:
                abs_mins    =   abs(int(time_diff.days))*86400 + mins_left

            # print day or days conditionally
            if int(time_diff.days) > 1:
                ret_message     +=  str(time_diff.days) + " days, " 
            elif int(time_diff.days) == 1:
                ret_message     +=  "1 day, "

            # print hour or hours conditionally
            if abs_mins > 119:
                ret_message     +=  str(math.floor((abs_mins%86400)/60)) + " hours, "
            elif abs_mins > 59:
                ret_message     +=  "1 hour, "

            # print minutes unconditionally
            # e.g.              0 minutes from now
            # e.g.              59 minutes ago
            ret_message     +=  (str(math.floor(abs_mins%60)) + " minutes " + 
                                ("from now" if int(time_diff.days) < 0 else "ago") + 
                                ")")

            # print extra anchored message conditionally
            if boss_status == status_anchored:
                ret_message     +=  " and as late as one hour later"

            ret_message     += ".\nLast known map: #   " + boss_premap + "\n"

            valid_boss_records.append(ret_message)

        #valid_boss_records.append("```\n")
        return valid_boss_records #'\n'.join(valid_boss_records)


def process_cmd_query(tg_boss, query):
    """
    :func:`process_cmd_query` processes a query relating to bosses.

    Args:
        tg_boss (str): the target boss
        query (str): the query (synonyms, maps)

    Returns:
        str: an appropriate message for success or fail of command, i.e. maps or aliases
    """
    # $boss [boss] syns
    if rgx_q_syn.match(query):
        return get_syns(tg_boss)
    # $boss [boss] maps
    else:
        return get_maps(tg_boss)


def process_cmd_type(boss_type):
    """
    :func:`process_cmd_type` prints out bosses for that boss type.

    Args:
        boss_type (str): the type of boss to query (world, field, demon)

    Returns:
        str: a formatted markdown message with bosses of the specified type, or empty string ("") if invalid type
    """
    if rgx_type.match(boss_type):
        return get_bosses(boss_type)
    else:
        return ""
        

def process_cmd_opt(opt_list, opt_boss):
    """
    :func:`process_cmd_opt` processes optional arguments.

    Args:
        opt_list (list): a list of optional arguments to process
        opt_boss (list): a list of bosses related to the options

    Returns:
        dict: a k:v of 'map' and 'channel', both str
    """
    target  =   dict()
    for cmd_arg in opt_list:
        cmd_arg     =   rgx_invalid.sub('', cmd_arg)
        channel     =   rgx_channel.match(cmd_arg)
        # target - channel
        if channel and opt_boss and opt_boss in bosses_with_floors: # all field bosses
            target['channel']   =   1
            target['map']       =   boss_locs[opt_boss][check_maps(opt_boss, cmd_arg)]
            return (target['map'], target['channel'])
        elif channel and opt_boss and opt_boss in bosses_world:
            target['channel']   =   int(channel.group(2)) # use channel provided by command
            target['map']       =   boss_locs[opt_boss][0]
            return (target['map'], target['channel'])
        elif opt_boss and opt_boss in bosses_demon: # possibly map instead
            target['channel']   =   1
            if cmd_arg: # must be map if not null
                map_idx         =   check_maps(opt_boss, cmd_arg)
            # target - map 
            if cmd_arg and map_idx >= 0 and map_idx < len(boss_locs[opt_boss]):
                target['map']   =   boss_locs[opt_boss][map_idx]
            else:
                target['map']   =   "N/A"
            return (target['map'], target['channel'])
    return ("N/A", 1)


def process_record(boss, status, time, boss_map, channel):
    """
    :func:`process_records` processes a record to print out

    Args:
        boss (str): the boss in question
        status (str): the status of the boss
        time (datetime): the `datetime` of the target set to its next approximate spawn
        boss_map (str): the map containing the last recorded spawn
        channel (float): the channel of the world boss if applicable; else, 1

    Returns:
        str: a formatted markdown message containing the records
    """
    # map does not rotate
    if boss not in bosses_demon or (rgx_st_warn.match(status) and boss_map != "N/A"):
        ret_message =   ", in the following map:\n" +"#   "
        ret_message +=  boss_map
    elif rgx_st_warn.match(status):
        ret_message =   ", in any of the following maps:\n" + "#   "
        boss_map    =   "\n#   ".join(boss_locs[boss])

    # unrecorded map
    elif boss_map == 'N/A':
        ret_message =   "."
        boss_map    =   ""

    # all others, i.e. bosses with more than two rotating fields
    else:
        ret_message =   ", in one of the following maps:\n" + "#   "
        ret_message +=  "\n#   ".join([m for m in boss_locs[boss] if m != boss_map])

    if boss == "Kubas Event":
        ret_message += "\n#   [Machine of Riddles], ch." + str(math.floor(float(channel)%2+1))

    ret_message     +=  "\n\n"
    rem_minutes     =   math.floor((time-(datetime.now()+timedelta(hours=pacific2server))).seconds/60)

    time_str        =   time.strftime("%Y/%m/%d %H:%M") + " (in " + str(rem_minutes) + " minutes)"
    when_spawn      =   "at " + time_str + ret_message

    # set time difference based on status and type of boss
    # takes the negative (additive complement) to get the original time
    # anchored
    if rgx_st_anch.search(status) and boss == "Abomination":
        time_diff   =   timedelta(hours=(-1*time_anch_abom))
        when_spawn  =   ("between " + (time-timedelta(hours=-1)).strftime("%Y/%m/%d %H:%M") + " " + 
                         "and " + time_str + ret_message)
    elif rgx_st_anch.search(status):
        time_diff   =   timedelta(hours=(-1*time_anchored))
        when_spawn  =   ("between " + (time-timedelta(hours=-1)).strftime("%Y/%m/%d %H:%M") + " " + 
                         "and " + time_str + ret_message)
    # warned; takes precedence over when the boss will spawn
    elif rgx_st_warn.search(status):
        time_diff   =   timedelta(minutes=(-1*time_warned))
    # two hour spawns; takes precedence over type of boss
    elif boss in boss_spawn_02h:
        time_diff   =   timedelta(minutes=(-1*(time_died)))
    # world bosses
    elif boss == "Abomination":
        time_diff   =   timedelta(hours=(-1*(time_died_wb_ab)))
    elif boss in bosses_world:
        time_diff   =   timedelta(hours=(-1*(time_died_wb)))
    # demon lords
    elif boss in boss_spawn_330:
        time_diff   =   timedelta(minutes=(-1*(time_died_330)))
    # all else; these are generally 4h
    else:
        time_diff   =   timedelta(minutes=(-1*time_died))

    # and add it back to get the reported time
    report_time     =   time+time_diff
    
    # e.g. "Blasphemous Deathweaver" died in ch.1 Crystal Mine 3F at 2017/07/06 18:30,
    #      and should spawn at 2017/07/06 22:30, in the following map:
    #      #   Crystal Mine 2F
    ret_message     =   ("\"" + boss + "\" " + status + " " + 
                         "in ch." + str(math.floor(float(channel))) + 
                         ((" \"" + boss_map + "\" ") if boss_map else " ") + 
                         "at " + report_time.strftime("%Y/%m/%d %H:%M") + ",\n" + 
                         "and should spawn " + when_spawn)

    return ret_message
    
