#vaivora_constants.command.boss
#requires: vaivora_constants.command.syntax
import vaivora_constants.command.syntax

command         =   vaivora_constants.command.syntax.code_block + "ini\n" + "[$boss] commands" + "\n" + \
                    ";================" + "\n" + \
                    vaivora_constants.command.syntax.heading + "\n"

N               =   "necessary"
O               =   "optional"
H               =   "help"

A               =   "type A"
B               =   "type B"
C               =   "type C"
D               =   "type D"

arg             =   dict()
arg[N]          =   dict()
arg[N][0]       =   "[prefix]"
arg[N][1]       =   dict()
arg[N][1][A]    =   "[boss|all]"
arg[N][1][B]    =   "[boss]"
arg[N][1][C]    =   "[all]"
arg[N][2]       =   dict()
arg[N][2][A]    =   "[died|anchored|warned]"
arg[N][2][B]    =   "[erase|list]"
arg[N][2][C]    =   "[synonyms|maps]"
arg[N][2][D]    =   "[world|field]"
arg[N][3]       =   "[time]"
arg[O]          =   dict()
arg[O][1]       =   "(chN)"
arg[O][2]       =   "(map)"
arg[H]          =   "[help]"

usage       =   arg[N][0] + " " + arg[N][1][B] + " " + arg[N][2][A] + " " + arg[N][3] + " " + arg[O][1] + " " + arg[O][2] + " " + "\n" + \
                arg[N][0] + " " + arg[N][1][A] + " " + arg[N][2][B] + " " + arg[O][2] + "\n" + \
                arg[N][0] + " " + arg[N][1][B] + " " + arg[N][2][C] + "\n" + \
                arg[N][0] + " " + arg[N][1][C] + " " + arg[N][2][D] + "\n" + \
                arg[N][0] + " " + arg[N][1][B] + " " + arg[H] + "\n"

command     +=  usage

arg_info    =   list()
arg_info.append(";================\n")
arg_info.append(arg[N][0] + "\n" + \
                "    [$boss] or [Vaivora, boss]\n")
arg_info.append(arg[N][1][B]  + "\n" + \
                "    Either part of, or full name- if spaced, enclose in double-quotes ([\"])\n" + \
                "    [all] for all bosses\n")
arg_info.append(arg[N][2][A]  + "\n" + \
                "    Valid for [boss] only, to indicate its status.\n" + \
                "    Do not use with [erase], [list], [synonyms], [maps], [world], or [field].\n")
arg_info.append(arg[N][2][B]  + "\n" + \
                "    Valid for both [boss] and [all] to [erase] or [list] entries.\n" + \
                "    Do not use with [died], [anchored], [warned], [synonyms], [maps], [world], or [field].\n")
arg_info.append(arg[N][2][C]  + "\n" + \
                "    Valid for [boss] only, to print aliases of bosses (short-hand) or maps that the boss may wander.\n" + \
                "    Do not use with [died], [anchored], [warned], [erase], [list], [world], or [field].\n")
arg_info.append(arg[N][2][D]  + "\n" + \
                "    Valid for [all] only, to print out either [world bosses] or [field bosses].\n" + \
                "    Do not use with [died], [anchored], [warned], [erase], [list], [synonyms], or [maps].\n")
arg_info.append(arg[N][3]     + " ; required for [died] and [anchored]\n" + \
                "    Remove spaces. 12 hour and 24 hour times acceptable, with valid delimiters \":\" and \".\". Use server time.\n")
arg_info.append(arg[O][2]     + " ; optional\n" + \
                "    Suitable only for field bosses.[*] If unlisted, this will be unassumed.\n")
arg_info.append(arg[O][1]     + " ; optional\n" + \
                "    Suitable only for world bosses.[*] If unlisted, CH[1] will be assumed.\n" + "\n")
arg_info.append("[*] ; Notes about world and field bosses:\n" + \
                "    ; Field bosses in channels other than 1 are considered 'world boss' variants.\n" + \
                "    ; and should not be recorded because they spawn unpredictably, because they're jackpot bosses.\n" + \
                "    ; Field bosses with jackpot buffs may also spawn in channel 1 but should not be recorded, either.\n")

command     +=  ''.join(arg_info)

examples    =   "\n" + vaivora_constants.command.syntax.example + \
                "[$boss cerb died 12:00pm 4f]        ; channel should be omitted for field bosses\n" + \
                "[Vaivora, boss crab died 14:00 ch2] ; map should be omitted for world bosses\n"

command     +=  examples

command     += "\n" + vaivora_constants.command.syntax.code_block


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
                  'Prison Manager Prison Cutter':   [ 'cutter', \
                                                      'prison cutter', \
                                                      'prison manager', \
                                                      'prison manager cutter' 
                                                    ], 
                  'Mirtis':                         [ 'mirtis' ], 
                  'Rexipher':                       [ 'rexipher', \
                                                      'rexi', \
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
                                                  'Syla Forest'
                                                ],
              'Demon Lord Zaura':               [ 'Arcus Forest', \
                                                  'Phamer Forest', \
                                                  'Ghibulinas Forest', \
                                                  'Mollogheo Forest'
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