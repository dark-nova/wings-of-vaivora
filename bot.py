import discord
import sqlite3
import shlex
import re
import os
from datetime import datetime

# basic declarations and initializations
client = discord.Client()

# variables to use
output  = list()

# constants
#   regex
numbers   = re.compile('[0-9]+')
quotes    = re.compile('"')
channel   = 'ch?[1-4]'
#   error(**) related constants
#     error(**) constants for "command" argument
cmd_boss  = "Command: Boss"
#     error(**) constants for "reason" argument
rsn_broad = "Reason: Broad"
rsn_unknn = "Reason: Unknown"
rsn_syntx = "Reason: Malformed Syntax"
rsn_quote = "Reason: Mismatched Quotes"

# database formats
time_prototype = ('year','month','day','hour','minute')
boss_prototype = ('name','channel','map') + time_prototype
remi_prototype = ('user','comment') + time_prototype
talt_prototype = ('user','previous','current','valid') + time_prototype

# and the database formats' types
time_prototype_types = ('real',)*5
boss_prototype_types = ('text',) + ('real',)*2 + time_prototype_types
remi_prototype_types = ('text',)*2 + time_prototype_types
talt_prototype_types = ('text',) + ('real',)*3 + time_prototype_types

# zip, create, concatenate into tuple
boss_tuple = tuple('{} {}'.format(*t) for t in 
                   zip(boss_prototype,boss_prototype_types))
remi_tuple = tuple('{} {}'.format(*t) for t in 
                   zip(remi_prototype,remi_prototype_types))
talt_tuple = tuple('{} {}'.format(*t) for t in 
                   zip(talt_prototype,talt_prototype_types))

async def create_discord_db(discord_db):
  conn = sqlite3.connect(discord_db)
  c = conn.cursor()
  # create boss table
  c.execute('create table boss(?)',boss_tuple)
  c.commit()
  # create reminders table; TODO (?)
  c.execute('create table reminders(?)',remi_tuple)
  c.commit()
  # close the database after creating
  c.close()
  return

async def validate_discord_db(discord_db):
  conn = sqlite3.connect(discord_db)
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  # 
  c.execute('select * from boss')
  r = c.fetchone()

async def check_boss_db(discord_server,boss_name,channel,boss_map,time):
  discord_db = discord_server + ".db"
  if not os.path.isfile(discord_db):
    await create_discord_db(discord_db)
  else:
    await valid = validate_discord_db(discord_db)

  if valid:
    conn = sqlite3.connect(discord_db)
    c = conn.cursor()
    c.executemany("select * from boss where name=? and channel=? and map=?",(boss,channel,boss_map))



  return valid 

## begin: obsolete code
# async def check_db(db):
#     try:
#         c.execute("select * from ?",db)
#         output.append(c.fetchall())
#     except:
#         print('Error: ' + db + ' database not found. Building new database...')
#         c.execute("create table ?(name text,channel real,day text,time text,
#                    map text,status text",db)
#         c.commit()
#         output.append(["None. Start getting some timers!"])
#         print("Built " + db + " database!")


# async def on_ready():
#     await client.login('MjEzMDQxNzI3Nzk4MjQ3NDI1.Co0qOA.yqoI7ggaX9aleWxUyPEHEIiLji0')
#     print("Logging in...")
#     print("Attaching database...")
#     await check_db('boss')
#     # check_db('dilgele')
#     print('Successsfully logged in as: ' + client.user.name + '#' + 
#           client.user.id + '. Ready!')
#     while True:
#         update(output[0])
#         #await asyncio.sleep(60)
#     pass



# async def update(db):
#     print("Current timers:")
#     boss_db.sort(key=lambda entry: (entry[2],entry[3]))
#     #dilg_db = output[1]
#     #dilg_db.sort(key=lambda entry: (entry[2],entry[3]))
#     print("Bosses:")
#     for boss in boss_db:
#         _year  = boss[2][0:4]
#         _month = boss[2][4:6]
#         _day   = boss[2][6:8]
#         _hour  = boss[3][0:2]
#         _mins  = boss[3][3:5]
#         diff = (datetime(_year,_month,_day,_hour,_mins)-datetime.now()).seconds
#         if diff < 0:
#             c.executemany('delete from boss where name=?,day=?,time=?',
#                           boss[0],boss[2],boss[3])
#             continue
#         _hours = diff//3600
#         _minsT = diff//60
#         _mins_ = _minsT-_hours*3600
#         print(boss[0] + " at " + boss[1] + " " + boss[4] + ", in " + 
#               _hours + " hour(s), " + _mins + " min(s). [" + 
#               _year + "/" + _month + "/" + _day + " "  + boss[3] + "]")
#     return

# # @return: True if succeeded, False otherwise
# async def db_process_boss(user,channel,arg_list):
#     await c.executemany("select * from boss where name=? and channel=? and map=?",
#                   (arg_list[0],arg_list[1],arg_list[2]))
#     previous = c.fetchall() # retrieve boss record given name, channel, map
#     if previous: # previous record exists
#         response = await ask_delete_boss(user,channel,previous)
#     if not response:
#         await client.send_message(channel,
#                                   "@" + user + " " + 
#                                   "Command aborted.\n")
#         return False
#     # else:
#     await c.executemany("delete from boss where name=? and channel=? and map=?",
#                   (arg_list[0],arg_list[1],arg_list[2]))
#     c.executemany("insert into boss values (?,?,?,?)",
#                   (arg_list[0],arg_list[1],arg_list[2],
#                    str(datetime.date()) + " " + str(arg_list[3])))
#     return True

# # confirm deletion for db_process_boss(*)
# async def ask_delete_boss(user,channel,previous):
#     await client.send_message(channel,
#                               "@" + user + " " + 
#                               "A record for this boss already exists: ```" + 
#                               ' '.join(previous) + "```\n" + 
#                               "Do you want to delete this entry? [YN]")
#     response = await client.wait_for_message(timeout=10,author=user)
#     return re.match("^[Yy]",response)

# # timeA and timeB must be of datatype datetime
# async def compare_time(timeA,timeB):
#     try:
#         return (timeA-timeB).seconds
#     except:
#         return 0
## end: obsolete code

# begin boss related variables

# 'bosses'
#   list of boss names in full
bosses = ['Blasphemous Deathweaver',
          'Bleak Chapparition',
          'Hungry Velnia Monkey',
          'Abomination',
          'Earth Templeshooter',
          'Earth Canceril',
          'Earth Archon',
          'Violent Cerberus',
          'Necroventer',
          'Forest Keeper Ferret Marauder',
          'Kubas Event',
          'Noisy Mineloader',
          'Burning Fire Lord',
          'Wrathful Harpeia',
          'Glackuman',
          'Marionette',
          'Dullahan Event',
          'Starving Ellaganos',
          'Prison Manager Prison Cutter',
          'Mirtis',
          'Rexipher',
          'Helgasercle',
          'Demon Lord Marnox',
          'Demon Lord Nuaele',
          'Demon Lord Zaura',
          'Demon Lord Blut']
#   field bosses
bossfl = bosses[0:2] + list(bosses[7]) + list(bosses[11]) + list(bosses[13]) + list(bosses[25])
#   world bosses
bosswo = [b for b in bosses if b not in bossfl]

# 'boss synonyms'
# - keys: boss names (var `bosses`)
# - values: list of synonyms of boss names
bossyn = {'Blasphemous Deathweaver':['dw','spider','deathweaver'],
          'Bleak Chapparition':['chap','chapparition'],
          'Hungry Velnia Monkey':['monkey','velnia','velniamonkey',
            'velnia monkey'],
          'Abomination':['abom','abomination'],
          'Earth Templeshooter':['temple shooter','TS','ETS','templeshooter'],
          'Earth Canceril':['canceril','crab','ec'],
          'Earth Archon':['archon'],
          'Violent Cerberus':['cerb','dog','doge','cerberus'],
          'Necroventer':['nv','necro','necroventer'],
          'Forest Keeper Ferret Marauder':['ferret','marauder'],
          'Kubas Event':['kubas'],
          'Noisy Mineloader':['ml','mineloader'],
          'Burning Fire Lord':['firelord','fl','fire lord'],
          'Wrathful Harpeia':['harp','harpy','harpie','harpeia'],
          'Glackuman':['glack','glackuman'],
          'Marionette':['mario','marionette'],
          'Dullahan Event':['dull','dulla','dullachan'],
          'Starving Ellaganos':['ella','ellaganos'],
          'Prison Manager Prison Cutter':['cutter','prison cutter',
            'prison manager','prison manager cutter'],
          'Mirtis':['mirtis'],
          'Rexipher':['rexipher','rexi','rexifer'],
          'Helgasercle':['helga','helgasercle'],
          'Demon Lord Marnox':['marnox','marn'],
          'Demon Lord Nuaele':['nuaele'],
          'Demon Lord Zaura':['zaura'],
          'Demon Lord Blut':['blut']}

# 'boss synonyms short'
# - list of synonyms of boss names
bossns = []
for l in list(bossyn.values()):
    bossns.extend(l)

# 'boss location'
# - keys: boss names (var `bosses`)
# - values: list of locations, full name
bosslo = {'Blasphemous Deathweaver':['Crystal Mine 1F',
                                     'Crystal Mine 2F',
                                     'Crystal Mine 3F',
                                     'Ashaq Underground Prison 1F',
                                     'Ashaq Underground Prison 2F',
                                     'Ashaq Underground Prison 3F'],
          'Bleak Chapparition':['Tenet Church B1',
                                'Tenet Church 1F',
                                'Tenet Church 2F'],
          'Hungry Velnia Monkey':['Novaha Assembly Hall',
                                  'Novaha Annex',
                                  'Novaha Institute'],
          'Abomination':['Guards\' Graveyard'],
          'Earth Templeshooter':['Royal Mausoleum Workers\' Lodge'],
          'Earth Canceril':['Royal Mausoleum Constructors\' Chapel'],
          'Earth Archon':['Royal Mausoleum Storage'],
          'Violent Cerberus':['Royal Mausoleum 4F',
                              'Royal Mausoleum 5F'],
          'Necroventer':['Residence of the Fallen Legwyn Family'],
          'Forest Keeper Ferret Marauder':['Bellai Rainforest',
                                           'Zeraha',
                                           'Seir Rainforest'],
          'Kubas Event':['Crystal Mine Lot 2 - 2F'],
          'Noisy Mineloader':['Mage Tower 4F','Mage Tower 5F'],
          'Burning Fire Lord':['Main Chamber','Sanctuary'],
          'Wrathful Harpeia':['Demon Prison District 1',
                              'Demon Prison District 2',
                              'Demon Prison District 5'],
          'Glackuman':['2nd Demon Prison'],
          'Marionette':['Roxona Reconstruction Agency East Building'],
          'Dullahan Event':['Roxona Reconstruction Agency West Building'],
          'Starving Ellaganos':['Mokusul Chamber',
                                'Videntis Shrine'],
          'Prison Manager Prison Cutter':['Drill Ground of Confliction',
                                          'Resident Quarter',
                                          'Storage Quarter',
                                          'Fortress Battlegrounds'],
          'Mirtis':['Kalejimas Visiting Room',
                    'Storage',
                    'Solitary Cells',
                    'Workshop',
                    'Investigation Room'],
          'Helgasercle':['Kalejimas Visiting Room',
                    'Storage',
                    'Solitary Cells',
                    'Workshop',
                    'Investigation Room'],
          'Rexipher':['Thaumas Trail',
                      'Salvia Forest',
                      'Sekta Forest',
                      'Rasvoy Lake',
                      'Oasseu Memorial'],
          'Demon Lord Marnox':['Thaumas Trail',
                      'Salvia Forest',
                      'Sekta Forest',
                      'Rasvoy Lake',
                      'Oasseu Memorial'],
          'Demon Lord Nuaele':['Yudejan Forest',
                               'Nobreer Forest',
                               'Emmet Forest',
                               'Pystis Forest',
                               'Syla Forest'],
          'Demon Lord Zaura':['Arcus Forest',
                              'Phamer Forest',
                              'Ghibulinas Forest',
                              'Mollogheo Forest'],
          'Demon Lord Blut':['Tevhrin Stalactite Cave Section 1',
                             'Tevhrin Stalactite Cave Section 2',
                             'Tevhrin Stalactite Cave Section 3',
                             'Tevhrin Stalactite Cave Section 4',
                             'Tevhrin Stalactite Cave Section 5']                          
         }

# 'boss location synonyms'
# - list of synonyms of boss locations
# -- grouping similar locations by line
bossls = ['crystal mine','ashaq',
          'tenet',
          'novaha',
          'guards','graveyard',
          'maus','mausoleum',
          'legwyn',
          'bellai','zeraha','seir',
          'mage tower','mt',
          'demon prison','dp',
          'main chamber','sanctuary','sanc',
          'roxona',
          'mokusul','videntis',
          'drill','quarter','battlegrounds',
          'kalejimas','storage','solitary','workshop','investigation',
          'thaumas','salvia','sekta','rasvoy','oasseu',
          'yudejan','nobreer','emmet','pystis','syla',
          'arcus','phamer','ghibulinas','mollogheo',
          'tevhrin']
# probably won't be using this, in hindsight.

# end of boss related variables

# begin code for message processing
async def on_message(message):
    # 'boss' channel processing
    if "timer" in message.channel or "boss" in message.channel:
        # 'boss' channel command: $boss
        #   arg order:
        #     1. [0] boss name
        #     2. [1] status (killed, anchored)
        #     3. [2] time
        #     4. [3] channel
        #     5. [4] map
        if message.content.startswith('$boss ') or 
           message.content.startswith('Vaivora, boss '):
            command_message = message.content
            message_args    = list()
            message_arg_str = str()

            # if odd amount of quotes, drop
            if len(re.findall('"',command_message)) % 2:
                err_code = await error(message.author,message.channel,'quote')
                return err_code

            # command: list of arguments
            command = shlex.split(command_message)
            # begin checking validity
            boss_valid = await check_boss(command[0])
            if not boss_valid > 0:
                err_code = await error(message.author,message.channel,rsn_unknn,command[0])
                return err_code

                concat   = str()
                word = re.sub('[^A-Za-z0-9-"]','',word) # sanitize
                word = word.lower()                     # standardize

                # section 0: concatenation
                if count == 1 or count == 3 and '"' in word:
                    complete = not complete
                    concat += word.replace('"','')
                    continue

                elif count == 1 or count == 3 and not complete:
                    concat += word
                    continue

                elif count == 1 or count == 3 and complete:
                    word = concat # redo loop with new word
                    continue
                # end of section 0

                # section 1: boss
                elif count == 1 and word == "boss":
                    continue

                elif count == 1 and word in bosses: # matched completely
                    bossrec.append(word)
                    bossname = word
                    count += 1
                    continue

                elif count == 1 and word in bossns: # matched synonym
                    for boss in bossyn.keys():
                        if word in bossyn[boss]:
                            bossname = boss
                            bossrec.append(boss) # append boss name
                            count += 1
                            continue
                    await error(message.author,message.channel,'boss',word) # no match; send error message, and...
                    return
                # end of section 1

                # section 2: channel
                elif count == 2 and channel.match(word):
                    message.append(re.sub('ch?','',word))
                    count += 1
                    continue
                # end of section 2

                # section 3: map
                elif count == 3 and word in bosslo[bossname]: # matched completely
                    bossrec.append(word)
                    count += 1
                    continue

                # section 3.a: map with floors
                elif count == 3 and bossname in bossfl: # no number? then...
                    if re.match('[0-9]f?',word):
                        mapnum = re.sub('[^0-9]f?','',word)
                        mapnam = word.split(mapnum)[0]
                    else: # boss spawns in maps with floors but floor not found
                        await error(message.author,message.channel,rsn_broad,cmd_boss,bossname) # too broad
                        return

                    if not mapnum > 0: # error on floor number
                        await error(message.author,message.channel,rsn_broad,cmd_boss,bossname) # too broad
                        return
                    elif bossname == bosses[0]: # blasphemous deathweaver
                        if not re.match('ashaq',mapnam) and not re.match('c(rystal ?)?m'):
                            await error(message.author,message.channel,'broad',bossname) # ashaq or cm not listed
                            return
                        elif mapnum > 3: # invalid floor
                            await error(message.author,message.channel,'badmap',mapnum)
                            return 
                        elif re.match('ashaq',mapnam): # ashaq
                            bossrec.append(bosslo[bossname][2+mapnum])
                            count += 1
                            continue
                        else: # crystal mine
                            bossrec.append(bosslo[bossname][mapnum-1])
                            count += 1
                            continue
                    elif bossname == bosses[1]: # bleak chapparition
                        if re.match('b',mapnam):
                            bossrec.append(bosslo[bossname][0]) # b1
                            count += 1
                            continue
                        elif re.match('1',mapnam):
                            bossrec.append(bosslo[bossname][1]) # 1f
                            count += 1
                            continue
                        else:
                            bossrec.append(bosslo[bossname][2]) # 2f
                            count += 1
                            continue
                    elif bossname == bosses[7] or bossname == bosses[11]: # violent cerberus and noisy mineloader
                        if mapnum > 5 or mapnum < 4: # incorrect range
                            await error(message.author,message.channel,'badmap',mapnum)
                            return
                        else:
                            bossrec.append(bosslo[bossname][mapnum-4])
                            count += 1
                            continue
                    # elif bossname == bosses[13]: # wrathful harpeia
                    elif not mapnum in [1,2,5]: # wrong districts
                        await error(message.author,message.channel,'badmap',mapnum)
                            return
                        else:
                            bossrec.append(bosslo[bossname][sqrt(mapnum-1)])
                            count += 1
                            continue

                # section 3.b: other maps
                elif count == 3:
                    for loc in bosslo[bossname]:
                        if word in loc:                               
                            bossrec.append(loc)
                            count += 1 
                            continue
                    await error(message.author,message.channel,'nomap',word)
                    return
                # end of section 3

                # section 4: time
                elif count == 4:
                    if re.match("am?",word):
                        word = re.sub("am?",'',word)
                        mins = int(word.split(':')[1])
                        hour = int(word.split(':')[0])
                    elif re.match("pm?",word):
                        word = re.sub("pm?",'',word)
                        mins = int(word.split(':')[1])
                        hour = int(word.split(':')[0])+12
                        word = str(hour) + ":" + str(mins)                               
                    elif not re.match(":",word):
                        await error(message.author,message.channel,'badtime',word)
                        return
                    elif hour > 23 or hour < 0 or mins > 59 or mins < 0:
                        await error(message.author,message.channel,'badtime',word)
                        return

                    bossrec.append(word)
                    count += 1
                # end of section 4

                # section 5: complete and assemble
                else:
                    await db_process_boss(message.author,message.channel,bossrec)
                # end of section 5
                # end of for-loop _message

            # check if not properly terminated
            if not complete:
                await error(message.author,message.channel,'quote')
                return

        # 'boss' channel command: $list
        elif message.content.startswith('$list '):
            pass

                
    else:
        return

# begin code for checking boss validity
async def check_boss(boss):
    if boss in bosses:
        return bosses.index(boss)
    else:
        for b in bosses:
            if b in boss:
                return bosses.index(b)
    return -1
# end code for checking boss validity

# begin strings for errors
# command - usage
cmd_usage     = "Usage:\n"
# command - [us]age - [c]ode [bl]oc[k]
cmd_us_cblk   = "```\n"
# command - [us]age - [a]rguments [bl]oc[k]
cmd_us_ablk   = "`"
# command - [us]age - [c]ode [arg]uments
cmd_us_carg   = "Arguments:\n"
# command - [us]age - [b]oss [arg]ument (1)
cmd_us_barg_1 = "BossName|\"Boss Name\""
# command - prefix - [b]oss
cmd_prefix_b  = ("$boss","Vaivora, boss")
# command - usage - [b]oss
cmd_usage_b   = ["***'Bosses' commands***"]

# command - usage - [b]oss - [n]th command -- reuse after every append
#   boss arg [n] - cmd_usage_b[n]
#     n=1
cmd_usage_b_n = (cmd_us_barg_1 + " died|anchored time [chN] [Map|\"Map\"]\n",)
cmd_usage_b.append('\n'.join([(' '.join(t) for t in zip(cmd_prefix_b,cmd_usage_b_n*2))]))
#     n=2
cmd_usage_b_n = (cmd_us_barg_1 + "BossName|\"boss name\" verified|erase [chN]\n",)
cmd_usage_b.append('\n'.join([(' '.join(t) for t in zip(cmd_prefix_b,cmd_usage_b_n*2))]))
#     n=3
cmd_usage_b_n = (cmd_us_barg_1 + "BossName|\"boss name\" list [chN]\n",)
cmd_usage_b.append('\n'.join([(' '.join(t) for t in zip(cmd_prefix_b,cmd_usage_b_n*2))]))
#     n=4
cmd_usage_b_n = (cmd_us_barg_1 + "all list",)
cmd_usage_b.append('\n'.join([(' '.join(t) for t in zip(cmd_prefix_b,cmd_usage_b_n*2))]))
#   command - usage - [b]oss - [a]rgument descriptors
#     n=5
cmd_usage_b_a = "`-` Boss Name or `all` **(required)**\n" +
                "`  -` Either part of, or full name; if spaced, enclose in double-quotes (\")\n" +
                "`  -` all when used with list will display all valid entries.\n" +
                "`-` time **(required for** `died` **and** `anchored` **)**" +
                "`-` Map *(optional)*\n" +
                "`  -` Handy for field bosses only. World bosses don't move across maps. This is optional and if unlisted will be unassumed.\n" +
                "Do note that Jackpot Bosses (clover buff) are 'world boss' variants of field bosses, " + 
                "and should not be recorded because they have unpredictable spawns.\n"
cmd_usage_b.append(cmd_usage_b_a)

# General command errors
cmd_badsyntax = "Your command was malformed.\n"
cmd_ambiguous = "Your command was ambiguous.\n"

# Specific command errors
#   command - usage - [b]oss - [m]ap
cmd_usage_b_m = "Make sure to properly record the map.\n"


# @arg:
#     user:     Discord.user
#     channel:  server channel
#     etype:    [e]rror type
#     ecmd:     [e]rror (invoked by) command
#     msg:      (optional) message for better error clarity
# @return:
#     -1: too general
#     -2: 
#     -127:   malformed command; quote, badmap, nomap
async def error(user,channel,etype,ecmd,msg=''):
    # Get the user in mentionable string
    user_name = user.mention
    ret_msg   = list()

    if ecmd == cmd_boss:
        if etype == rsn_broad:
            ret_msg.append(user_name + " The following option `boss` (" + msg + 
                           ") for `$boss` has multiple matching spawn points.\n")
            ret_msg.append(cmd_us_cblk)
            ret_msg.append('\n'.join(bosslo[msg]))
            ret_msg.append(cmd_us_cblk)
            ecode = -1
            await client.send_message(channel, user_name + " " + 
                                      "The following option `boss` (" + msg + 
                                      ") for `$boss` has multiple matching spawn points:\n```" + 
                                      '\n'.join(bosslo[msg]) + "```\n" + 
                                      cmd_ambiguous + 
                                      cmd_usage_b)

        elif etype == rsn_unknn:
            await client.send_message(channel, user_name + " " + 
                                      "The following option `boss` (" + msg + 
                                      ") is invalid for `$boss`.\n" + 
                                      "This is a list of bosses you may use:\n" + 
                                      "```" + '\n'.join(bosses) + "```\n" + 
                                      cmd_usage_b)
            return -2
        else:
            ret_msg.append(user_name + " Debug message")
            ecode = -1
        # end of conditionals for cmd_boss

        # begin common return
        ret_msg.append()
        ret_msg.extend(cmd_usage_b)
        # end of common return
    elif etype == "quote":
        await client.send_message(channel, user_name + " " + 
                                  "Your command for `$boss` had misused quotes somewhere.\n" +
                                  cmd_usage_b)
        return -127

    elif etype == "badmap":
        await client.send_message(channel, user_name + " " + 
                                  "The following option `map` (" + msg + 
                                  ") (number) is invalid for `$boss`.\n" + 
                                  cmd_usage_b_m + 
                                  cmd_usage_b)
        return -127

    elif etype == "nomap":
        await client.send_message(channel,"@" + user + " " + 
                                  "The following option `map` (" + msg + 
                                  ") is invalid for `$boss`.\n" + 
                                  "The map was not found. " + 
                                  cmd_usage_b_m + 
                                  cmd_usage_b)
        return
    elif etype == "badtime":
        await client.send_message(channel,"@" + user + " " + 
                                  "The following option `time` (" + msg + 
                                  ") is invalid for `$boss`.\n" + 
                                  "Omit spaces; 12H or 24H time is valid." + 
                                  cmd_usage_b)