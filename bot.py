import discord
import sqlite3
import shlex
import re
import os
from datetime import datetime, timedelta

# basic declarations and initializations
client    = discord.Client()
EASTERN   = timedelta(hours=3)
WESTERN   = timedelta(hours=-3)
FOURHWAIT = timedelta(hours=4)
ANCHHWAIT = timedelta(hours=3)

# variables to use
output    = list()

# constants
#   regex
numbers   = re.compile(r'[0-9]+')
letters   = re.compile(r'[a-z -]+')
pmflag    = re.compile(r' ?[Pp][Mm]?')
amflag    = re.compile(r' ?[Aa][Mm]?')
uletters  = re.compile(r'[^A-Za-z0-9 "-]')
timefmt   = re.compile(r'[0-2]?[0-9]:[0-5][0-9]([AaPp][Mm]?)?')
quotes    = re.compile(r'"')
bstatus   = re.compile(r'([Dd]ied|[Aa]nchored)')
bstanch   = re.compile(r'([Aa]nchored)')
chanlre   = re.compile(r'(ch)?[1-4]')
floors    = re.compile(r'[bf]?[0-9][bf]?$')
gfloors   = re.compile(r'.+(b?)(f?)([0-9])(b?)(f?)$')
gflarre   = re.compile(r'\g<1>\g<4>\g<3>\g<2>\g<5>')
pfboss    = re.compile(r'([Vv]a?i(v|b)ora, |\$)boss')
bossall   = re.compile(r'all')
bosslist  = re.compile(r'li?st?')
#   error(**) related constants
#     error(**) constants for "command" argument
cmd_boss  = "Command: Boss"
#     error(**) constants for "reason" argument
rsn_broad = "Reason: Broad"
rsn_argct = "Reason: Argument Count"
rsn_unknn = "Reason: Unknown Boss"
rsn_syntx = "Reason: Malformed Syntax"
rsn_quote = "Reason: Mismatched Quotes"
rsn_bdmap = "Reason: Bad Map"
rsn_bdtme = "Reason: Bad Time"
rsn_fdbos = "Reason: Field Boss Channel"

# database formats
time_prototype = ('year','month','day','hour','minute')
boss_prototype = ('name','channel','map') + time_prototype
remi_prototype = ('user','comment') + time_prototype
talt_prototype = ('user','previous','current','valid') + time_prototype
perm_prototype = ('user','role')

# and the database formats' types
time_prototype_types = ('real',)*5
boss_prototype_types = ('text',) + ('real',)*2 + time_prototype_types
remi_prototype_types = ('text',)*2 + time_prototype_types
talt_prototype_types = ('text',) + ('real',)*3 + time_prototype_types
perm_prototype_types = ('text',)*2

# zip, create, concatenate into tuple
boss_tuple = tuple('{} {}'.format(*t) for t in 
                   zip(boss_prototype,boss_prototype_types))
remi_tuple = tuple('{} {}'.format(*t) for t in 
                   zip(remi_prototype,remi_prototype_types))
talt_tuple = tuple('{} {}'.format(*t) for t in 
                   zip(talt_prototype,talt_prototype_types))
perm_tuple = tuple('{} {}'.format(*t) for t in
                   zip(perm_prototype,perm_prototype_types))

async def create_discord_db(discord_db):
    conn = sqlite3.connect(discord_db)
    c = conn.cursor()

    # delete table if necessary since it may be invalid
    c.execute('drop table if exists boss')
    # create boss table
    c.execute('create table boss(?)',boss_tuple)
    c.commit()

    # create reminders table
    #### TODO
    #c.execute('create table reminders(?)',remi_tuple)
    #c.commit()

    # create talt tracking table
    #### TODO
    #c.execute('create table talt(?)',talt_tuple)
    #c.commit()

    # create permissions hierarchy
    #### TODO
    #c.execute('create table permissions(?)',perm_tuple)
    #c.commit()

    # close the database after creating
    c.close()
    return

# @func:  
async def validate_discord_db(discord_db):
    if not os.path.isfile(discord_db):
        await create_discord_db(discord_db)
        return False # not initialized
    else:
        conn = sqlite3.connect(discord_db)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        # check boss table
        c.execute('select * from boss')
        r = c.fetchone()
        # check if boss table matches format
        if not tuple(r.keys()) is boss_prototype:
            c.close() # close first
            await create_discord_db(discord_db)
            return False # invalid db; deleted and recreated
        #### TODO: Validate other tables when implemented
        return True

async def check_boss_db(discord_server,boss_name):
    discord_db = discord_server + ".db"
    if not os.path.isfile(discord_db):
        await create_discord_db(discord_db)
    else:
        await valid = validate_discord_db(discord_db)

    if valid:
        conn = sqlite3.connect(discord_db)
        c = conn.cursor()
        c.executemany("select * from boss where name=? and channel=? and map=?",(boss,channel,boss_map))

        # return a list of records
        return c.fetchall()

    return None

async def update_boss_db(discord_server,boss_dict):
    discord_db = discord_server + ".db"


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
                                'Tenet Church 1F'],
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
# @func:    on_message(Discord.message)
# @arg:
#     message: Discord.message; includes message among sender (Discord.user) and server (Discord.server)
# @return:
#     None
async def on_message(message):
    # 'boss' channel processing
    if "timer" in message.channel or "boss" in message.channel:
        # 'boss' channel command: $boss
        #     arg order:
        #         1. [0] req boss name
        #         2. [1] req status (killed, anchored)
        #         3. [2] req time
        #         4. [3] opt channel
        #         5. [4] opt map
        if message.content.startswith('$boss ') or 
           message.content.startswith('Vaivora, boss '):
            command_server  = message.server
            command_message = message.content
            command_message = uletters.sub('',command_message)  # sanitize
            command_message = command_message.lower()           # standardize
            command_message = pfboss.sub('',command_message)    # strip leading command/arg
            message_args    = dict() # keys(): name, channel, map, time, 
            boss_channel    = 1
            maps_idx        = -1

            # if odd amount of quotes, drop
            if len(re.findall('"',command_message)) % 2:
                err_code = await error(message.author,message.channel,rsn_quote)
                return err_code

            # command: list of arguments
            command = shlex.split(command_message)

            # begin checking validity
            #     arg validity
            #         count: [3,5]
            if len(command) < 3 or len(command) > 5:
                err_code = await error(message.author,message.channel,rsn_argct,len(command))
                return err_code

            #         boss: letters
            #         status: anchored, died
            #         time: format
            if not (letters.match(command[0]) and bstatus.match(command[1]) and timefmt.match(command[2])):
                err_code = await error(message.author,message.channel,rsn_syntx)
                return err_code

            #     boss validity
            #         all list
            if bossall.match(command[0]) and bosslist.match(command[1]):
                bossrec = await check_boss_db(command_server,[bosses]) # possible return

            elif bossall.match(command[0]):
                err_code = await error(message.author,message.channel,rsn_syntx)
                return err_code
            
            boss_idx = await check_boss(command[0])
            if boss_idx < 0  or boss_idx >= len(boss):
                err_code = await error(message.author,message.channel,rsn_unknn,command[0])
                return err_code

            #         boss list
            if bosslist.match(command[1]):
                bossrec = await get_boss_db(command_server,[bosses[boss_idx],]) # possible return


            #     (opt) channel: reject if field boss & ch > 1 or if ch > 4
            #     (opt) map: validity
            ##### TODO: Make channel limit specific per boss
            if len(command) > 3:
                #     channel is set
                #     keep track of arg position in case we have 5
                argpos = 3
                if chanlre.match(command[argpos]):
                    boss_channel = int(letters.sub('',command[argpos]))
                    argpos += 1
                
                #     specifically not an elif - sequential handling of args
                #     cases:
                #         4 args: 4th arg is channel
                #         4 args: 4th arg is map
                #         5 args: 4th and 5th arg are channel and map respectively
                if not chanlre.match(command[argpos]) or len(command) == 5:
                    maps_idx = await check_maps(command[argpos],command[1])
                    if maps_idx < 0 or maps_idx >= len(bosslo[boss]):
                        err_code = await error(message.author,message.channel,rsn_bdmap,command[1])
                        return err_code

            #         check if boss is a field boss, and discard if boss channel is not 1
            if bosses[boss_idx] in bossfl and boss_channel != 1:
                err_code = await error(message.author,message.channel,rsn_fdbos,boss_channel,bosses[boss_idx])

            # everything looks good if the string passes through
            # begin compiling record in dict form 'message_args'
            message_args['name'] = bosses[boss_idx]
            message_args['channel'] = boss_channel
            if maps_idx >= 0:
                message_args['map'] = bosslo[message_args['name']][maps_idx]
            else:
                message_args['map'] = 'N/A'

            # process time
            #     antemeridian
            if amflag.search(command[2]):
                btime = amflag.sub('',command[2]).split(':')
                bhour = int(btime[0]) % 12
            #     postmeridian
            elif pmflag.search(command[2]):
                btime = pmflag.sub('',command[2]).split(':')
                bhour = (int(btime[0]) % 12) + 12
            #     24h time
            else:
                btime = command[2].split(':')
                bhour = int(btime[0])
            #     handle bad input
            if bhour > 24:
                err_code = await error(message.author,message.channel,rsn_bdtme,command[2])
                return err_code
            bminu = int(btime[1])

            approx_server_time = datetime.today() + EASTERN
            btday = approx_server_time.day
            btmon = approx_server_time.month
            byear = approx_server_time.year
            # late recorded time; correct with -1 day
            mdate = datetime.datetime(byear,btmon,btday,hour=bhour,minute=bminu)
            if (mdate-approx_server_time).days < 0:
                btday -= 1

            wait_time = ANCHHWAIT if bstanch.match(command[1]) else FOURHWAIT
            bhour = int(bhour + wait_time - 3) # bhour in Pacific/local

            # add them to dict
            message_args['hour'] = bhour
            message_args['mins'] = bminu
            message_args['day']       = btday
            message_args['month']     = btmon
            message_args['year']      = byear
            message_args['status']    = command[1] # anchored or died

            bossrec = await update_boss_db(command_server,message_args)
                
    else:
        return

# @func:  check_boss(str): begin code for checking boss validity
# @arg:
#     boss: str; boss name from raw input
# @return:
#     boss index in list, or -1 if not found
async def check_boss(boss):
    if boss in bosses:
        return bosses.index(boss)
    else:
        # for b in bosses:
        #     if b in boss:
        #         return bosses.index(b)
        for b, syns in bossyn.items():
            if boss in syns or b in boss:
                return bosses.index(b)
    return -1
# end of check_boss

# @func:  check_maps(str): begin code for checking map validity
# @arg:
#     maps: str; map name from raw input
#     boss: str; the corresponding boss
# @return:
#     map index in list, or -1 if not found
async def check_maps(maps,boss):
    if floors.match(maps):
        # rearrange letters, and remove map name
        mapnum = gfloors.sub(gflarre,maps)
        mmatch = mapnum.search(maps)
        if not mmatch:
            return -1
        return bosslo[boss].index(mmatch)
    else:
        for m in bosslo[boss]:
            if m in maps:
                return bosslo[boss].index(m)
    return -1

# begin constants for strings for error messages
#   command - usage
cmd_usage     = "Usage:\n"
#   command - [us]age - [c]ode [bl]oc[k]
cmd_us_cblk   = "```\n"
#   command - [us]age - [a]rguments [bl]oc[k]
cmd_us_ablk   = "`"
#   command - [us]age - [c]ode [arg]uments
cmd_us_carg   = "Arguments:\n"
debug_message = " Debug message. Something went wrong.\n"

#   begin $boss specific constants
#       command - [us]age - [b]oss [arg]ument (1)
cmd_us_barg_1 = "BossName|\"Boss Name\""
#       command - prefix - [b]oss
cmd_prefix_b  = ("$boss","Vaivora, boss")
#       command - usage - [b]oss
cmd_usage_b   = ["***'Bosses' commands***"]
cmd_usage_b.append(cmd_usage)
#   end of $boss specific constants
# end of constants for strings for error messages

# begin $boss usage string, in cmd_usage_b : list
#     command - usage - [b]oss - [n]th command -- reuse after every append
#         boss arg [n] - cmd_usage_b[n]
#             n=1
cmd_usage_b_n = (cmd_us_barg_1 + " died|anchored time [chN] [Map|\"Map\"]\n",)
cmd_usage_b.append('\n'.join([(' '.join(t) for t in zip(cmd_prefix_b,cmd_usage_b_n*2))]))
#             n=2
cmd_usage_b_n = (cmd_us_barg_1 + "BossName|\"boss name\" verified|erase [chN]\n",)
cmd_usage_b.append('\n'.join([(' '.join(t) for t in zip(cmd_prefix_b,cmd_usage_b_n*2))]))
#             n=3
cmd_usage_b_n = (cmd_us_barg_1 + "BossName|\"boss name\" list [chN]\n",)
cmd_usage_b.append('\n'.join([(' '.join(t) for t in zip(cmd_prefix_b,cmd_usage_b_n*2))]))
#             n=4
cmd_usage_b_n = (cmd_us_barg_1 + "all list",)
cmd_usage_b.append('\n'.join([(' '.join(t) for t in zip(cmd_prefix_b,cmd_usage_b_n*2))]))
#     command - usage - [b]oss - [a]rgument descriptors
#             n=5
cmd_usage_b_a = "`-` Boss Name or `all` **(required)**\n" +
                "`  -` Either part of, or full name; if spaced, enclose in double-quotes (\")\n" +
                "`  -` all when used with list will display all valid entries.\n" +
                "`-` time **(required for** `died` **and** `anchored` **)**" +
                "`-` Map *(optional)*\n" +
                "`  -` Handy for field bosses only. World bosses don't move across maps. This is optional and if unlisted will be unassumed.\n" +
                "Do note that Jackpot Bosses (clover buff) are 'world boss' variants of field bosses, " + 
                "and should not be recorded because they have unpredictable spawns.\n"
cmd_usage_b.append(cmd_usage_b_a)
# end of $boss usage string, in cmd_usage_b

# begin constants to use for error(**)
#     general command errors
cmd_badsyntax = "Your command was malformed.\n"
cmd_ambiguous = "Your command was ambiguous.\n"

#     specific command errors
#         command - usage - [b]oss - [m]ap
cmd_usage_b_b = "Make sure to properly spell the boss name.\n"
cmd_usage_b_m = "Make sure to properly record the map.\n"
# end of constants for error(**)

# @func:  error(**): begin code for error message printing to user
# @arg:
#     user:     Discord.user
#     channel:  server channel
#     etype:    [e]rror type
#     ecmd:     [e]rror (invoked by) command
#     msg:      (optional) message for better error clarity
# @return:
#     -1: the command was correctly formed but the argument is too broad
#     -2: the command was correctly formed but could not validate arguments
#     -127:   malformed command: quote mismatch, argument count
async def error(user,channel,etype,ecmd,msg='',xmsg=''):
    # Get the user in mentionable string
    user_name = user.mention
    ret_msg   = list()

    # boss command only
    if ecmd == cmd_boss:
        # broad
        if etype == rsn_broad:
            ret_msg.append(user_name + the_following_argument('boss') + msg + 
                           ") for `$boss` has multiple matching spawn points:\n")
            ret_msg.append(cmd_us_cblk)
            ret_msg.append('\n'.join(bosslo[msg]))
            ret_msg.append(cmd_us_cblk)
            ret_msg.append(cmd_ambiguous)
            ret_msg.append(cmd_usage_b_m)
            ecode = -1
        # unknown
        elif etype == rsn_unknn:
            ret_msg.append(user_name + the_following_argument('boss') + msg +
                           ") is invalid for `$boss`. This is a list of bosses you may use:\n")
            ret_msg.append(cmd_us_cblk)
            ret_msg.append('\n'.join(bosses))
            ret_msg.append(cmd_us_cblk)
            ret_msg.append(cmd_usage_b_b)
            ecode = -2
        elif etype == rsn_bdmap:
            ret_msg.append(user_name + the_following_argument('map') + msg +
                           ") (number) is invalid for `$boss`. This is a list of maps you may use:\n")
            ret_msg.append(cmd_us_cblk)
            try:
              ret_msg.append('\n'.join(bosslo[xmsg]))
            except:
              ret_msg.append(user_name + debug_message)
              ret_msg.append(cmd_badsyntax)
              ecode = -127
              await client.send_message(channel,'\n'.join(ret_msg))
              return ecode
            ret_msg.append(cmd_us_cblk)
            ret_msg.append(cmd_usage_b_m)
            ecode = -2
        elif etype == rsn_fdbos:
            ret_msg.append(user_name + the_following_argument('channel') + msg +
                           ") (number) is invalid for `$boss`. " + xmsg + " is a field boss, thus " +
                           "variants that spawn on channels other than 1 (or other maps) are considered world bosses " +
                           "with unpredictable spawns.\n")
            ecode = -2
        elif etype == rsn_bdtme:
            ret_msg.append(user_name + the_following_argument('time') + msg +
                           ") is invalid for `$boss`.\n")
            ret_msg.append("Omit spaces; record in 12H (with AM/PM) or 24H time.\n")
            ret_msg.append(cmd_badsyntax)
            ecode = -2
        elif etype == rsn_argct:
            ret_msg.append(user_name + " Your command for `$boss` had too few arguments.\n" +  
                           "Expected: 4 to 6; got: " + msg + ".\n")
            ret_msg.append(cmd_badsyntax)
            ecode = -127
        elif etype == rsn_quote:
            ret_msg.append(user_name + " Your command for `$boss` had misused quotes somewhere.\n")
            ret_msg.append(cmd_badsyntax)
            ecode = -127
        else:
            ret_msg.append(user_name + debug_message)
            ret_msg.append(cmd_badsyntax)
            ecode = -127
            await client.send_message(channel,'\n'.join(ret_msg))
            return ecode
        # end of conditionals for cmd_boss

        # begin common return
        ret_msg.extend(cmd_usage_b)
        await client.send_message(channel,'\n'.join(cmd_usage_b))
        return ecode
        # end of common return
    # todo: reminders, Talt tracking, permissions
    else:
        # todo
        ret_msg.append(user_name + debug_message)
        ret_msg.append(cmd_badsyntax)
        ecode = -127
        await client.send_message(channel,'\n'.join(ret_msg))
        return ecode 
# end of error

# @func:  the_following_argument(str): begin concatenated string
# @arg:
#     arg: str; e.g. boss, map, time
# @return:
#     str, containing message
def the_following_argument(arg):
    return " The following argument `" + arg + "` ("
# end of the_following_argument