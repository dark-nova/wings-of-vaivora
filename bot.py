#!/usr/bin/env python
import discord
import logging
import sqlite3
import shlex
import asyncio
import re
import os
from datetime import datetime, timedelta
from operator import itemgetter

# import additional constants
from importlib import import_module as im
import vaivora_constants
for mod in vaivora_constants.modules:
    im(mod)
import vaivora_db

# basic declarations and initializations
client    = discord.Client()

# database formats
prototype = dict()
prototype['time'] = ('year', 'month', 'day', 'hour', 'minute')
prototype['boss'] = ('name', 'channel', 'map', 'status', 'text_channel') + prototype['time']
prototype['remi'] = ('user', 'comment') + prototype['time']
prototype['talt'] = ('user', 'previous', 'current', 'valid') + prototype['time']
prototype['perm'] = ('user', 'role')

# and the database formats' types
prototype['time.types'] = ('real',)*5
prototype['boss.types'] = ('text',) + ('real',) + ('text',)*3 + prototype['time.types']
prototype['remi.types'] = ('text',)*2 + prototype['time.types']
prototype['talt.types'] = ('text',) + ('real',)*3 + prototype['time.types']
prototype['perm.types'] = ('text',)*2

# zip, create, concatenate into tuple
boss_tuple = tuple('{} {}'.format(*t) for t in 
                   zip(prototype['boss'], prototype['boss.types']))
remi_tuple = tuple('{} {}'.format(*t) for t in 
                   zip(prototype['remi'], prototype['remi.types']))
talt_tuple = tuple('{} {}'.format(*t) for t in 
                   zip(prototype['talt'], prototype['talt.types']))
perm_tuple = tuple('{} {}'.format(*t) for t in
                   zip(prototype['perm'], prototype['perm.types']))

# snippet from discord.py docs
logger = logging.getLogger(vaivora_constants.values.filenames.logger)
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(vaivora_constants.values.filenames.log_file, encoding="utf-8")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# @func:      create_discord_db(Discord.server.str, func, *)
# @arg:
#   discord_server: the discord server's id
#   db_func:        a database function
#   xargs:          extra arguments
# @return:
#   Relevant data if successful, False otherwise
async def func_discord_db(discord_server, db_func, xargs=None):
    if vaivora_constants.regex.db.ext.search(discord_server):
        discord_db = discord_server
    elif vaivora_constants.regex.db.filename.search(discord_server):
        discord_db = discord_server + ".db"
    else:
        return False # invalid name
    conn = sqlite3.connect(discord_db)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    if not os.path.isfile(discord_db):
        await create_discord_db(c)
        return False # not initialized
    elif not callable(db_func):
        return False
    # implicit else
    if xargs and not db_func is rm_ent_boss_db:
        dbif  = await db_func(c, xargs)
    elif type(xargs) is str:
        dbif  = await db_func(c, bn=xargs)
    elif type(xargs) is tuple:
        dbif  = await db_func(c, bn=xargs[0], ch=xargs[1])
    elif type(xargs) is dict:
        dbif  = await db_func(c, bd=xargs)
    else:
        dbif  = await db_func(c)
    conn.commit()
    conn.close()
    return dbif

# @func:      create_discord_db(sqlite3.connect.cursor)
# @arg:
#   conn:           the sqlite3 connection
# @return:
#   None
async def create_discord_db(c):
    # delete tables if necessary since it may be invalid #### Maybe to ignore?
    c.execute('drop table if exists boss')
    c.execute('drop table if exists reminders')
    c.execute('drop table if exists talt')
    c.execute('drop table if exists permissions')

    # create boss table
    c.execute('create table boss({})'.format(','.join(boss_tuple)))

    # create reminders table
    c.execute('create table reminders({})'.format(','.join(remi_tuple)))

    # create talt tracking table
    c.execute('create table talt({})'.format(','.join(talt_tuple)))

    # create permissions hierarchy
    c.execute('create table permissions({})'.format(','.join(perm_tuple)))
    
    return

# @func:    validate_discord_db(sqlite3.connect.cursor)
# @arg:
#   c:              the sqlite3 connection cursor
# @return:
#   True if valid, False otherwise
async def validate_discord_db(c):
    # check boss table
    try:
        c.execute('select * from boss')
    except:
        await create_discord_db(c)
        return True
    r = c.fetchone()
    if not r:
        return True # it's empty. probably works.
    # check if boss table matches format
    if sorted(tuple(r.keys())) != sorted(vaivora_db.columns[vaivora_db.BOSS]):
        return False # invalid db
    #### TODO: Validate other tables when implemented, priority: medium
    return True

# @func:    check_boss_db(sqlite3.connect.cursor, list)
# @arg:
#   c:              the sqlite3 connection cursor
#   boss_list:      list containing bosses to check
# @return:
#   False if db is not prepared; otherwise, a list
async def check_boss_db(c, boss_list):
    db_record = list()
    for b in boss_list:
        c.execute("select * from boss where name=?", (b,))
        records = c.fetchall()
        for record in records:
            db_record.append(tuple(record))
    # return a list of records
    return db_record
# @func:    update_boss_db(sqlite3.connect.cursor, dict)
# @arg:
#   c:              the sqlite3 connection cursor
#   boss_dict:      message_args from on_message(*)
# @return:
#   True if successful, False otherwise
async def update_boss_db(c, boss_dict):
    # the following two bosses rotate per spawn
    if boss_dict['name'] == 'Mirtis' or boss_dict['name'] == 'Helgasercle':
        c.execute("select * from boss where name=?", ('Mirtis',))
        contents = c.fetchall()
        c.execute("select * from boss where name=?", ('Helgasercle',))
        contents += c.fetchall()
    elif boss_dict['name'] == 'Demon Lord Marnox' or boss_dict['name'] == 'Rexipher':
        c.execute("select * from boss where name=?", ('Demon Lord Marnox',))
        contents = c.fetchall()
        c.execute("select * from boss where name=?", ('Rexipher',))
        contents += c.fetchall()
    elif boss_dict['name'] == 'Blasphemous Deathweaver':
        c.execute("select * from boss where name=? and map=?", \
          (boss_dict['name'], boss_dict['map'],))
        contents = c.fetchall()
    else:
        c.execute("select * from boss where name=? and channel=?", (boss_dict['name'], boss_dict['channel'],))
        contents = c.fetchall()

    # invalid case: more than one entry for this combination
    #### TODO: keep most recent time? 
    if boss_dict['name'] != "Blasphemous Deathweaver" and len(contents) >= 1: #and boss_dict['name'] not in bos16s:
        await rm_ent_boss_db(c, boss_dict)
    elif boss_dict['name'] == "Blasphemous Deathweaver" and len(contents) >= 2:
        await rm_ent_boss_db(c, boss_dict)

    # if entry has newer data, discard previousit's 
    if contents and (int(contents[0][5]) < boss_dict['year'] or \
                     int(contents[0][6]) < boss_dict['month'] or \
                     int(contents[0][7]) < boss_dict['day'] or \
                     int(contents[0][8]) < boss_dict['hour'] - 3):
        await rm_ent_boss_db(c, boss_dict)

    #try: # boss database structure
    c.execute("insert into boss values (?,?,?,?,?,?,?,?,?,?)",
              (str(boss_dict['name']),
               int(boss_dict['channel']),
               str(boss_dict['map']),
               str(boss_dict['status']),
               str(boss_dict['srvchn']),
               int(boss_dict['year']),
               int(boss_dict['month']),
               int(boss_dict['day']),
               int(boss_dict['hour']),
               int(boss_dict['mins'])))
    # except:
    #     return False
    return True

# @func:    rm_ent_boss_db(sqlite3.connect.cursor, dict, int)
# @arg:
#   c:              the sqlite3 connection cursor
#   boss_dict:      message_args from on_message(*)
#   ch:             Default: None; the channel to remove
# @return:
#   True if successful, False otherwise
async def rm_ent_boss_db(c, bd=None, bn=None, ch=None, perm=True):
    #if perm: # temporary. going to implement permissions for this
     #   return True
    rm_map = None
    if bd:
        rm_name, rm_channel, rm_map = bd['name'], bd['channel'], bd['map']
    elif bn and ch:
        rm_name, rm_channel = bn, ch
    elif bn:
        rm_name = bn
        rm_channel = None
    else:
        return False
    try:
        if rm_channel:
            c.execute("delete from boss where name=? and channel=?", (rm_name, rm_channel,))
        elif rm_name == "Blasphemous Deathweaver" and rm_map:
            c.execute("delete from boss where name=? and map=?", (rm_name, rm_map))
        else:
            c.execute("delete from boss where name=?", (rm_name,))
    except:
        return False
    return True

# @func:    on_ready()
# @return:
#   None
@client.event
async def on_ready():
    #servers
    print("Logging in...")
    print('Successsfully logged in as: ' + client.user.name + '#' + \
          client.user.id + '. Ready!')

    valid_dbs = []

    try:
        s = open(vaivora_constants.values.filenames.welcomed, 'r')
    except:
        open(vaivora_constants.values.filenames.welcomed, 'a').close()
        s = open(vaivora_constants.values.filenames.welcomed, 'r')
    for server in client.servers:
        if not str(server.id) in s:
            await on_server_join(server)

    try:
        f = open(vaivora_constants.values.filenames.valid_db, 'a')
    except:
        open(vaivora_constants.values.filenames.valid_db, 'a').close()
        f = open(vaivora_constants.values.filenames.valid_db, 'w')

    with open(vaivora_constants.values.filenames.valid_db, 'r') as vdbs:
        valid_list = [ vdb.rstrip('\n') for vdb in vdbs ]
    with os.scandir() as items:
        for item in items:
            if item.is_file() and vaivora_constants.regex.db.filename.search(item.name) and vaivora_constants.regex.db.ext.search(item.name) and \
              not item.name in valid_list:
                if not await func_discord_db(item.name, validate_discord_db):
                    await func_discord_db(item.name, create_discord_db)
                f.write(item.name + "\n")
    f.close()

# @func:    on_server_available(discord.Server)
# @return:
#   True if ready, False otherwise
@client.event
async def on_server_join(server):
    if server.unavailable:
        return False
    srvnm = server.id # id now
    if not re.match(r'[0-9]{18,}', srvnm):
        return False
    srvnm   = str(srvnm)
    status  = await func_discord_db(srvnm, validate_discord_db)
    if not status:
        # create if db doesn't already exist
        await func_discord_db(srvnm, create_discord_db)
    # send welcome message
    try:
        g = open(vaivora_constants.values.filenames.valid_db, 'r')
    except:
        open(vaivora_constants.values.filenames.valid_db, 'a').close()
        g = open(vaivora_constants.values.filenames.valid_db, 'r')
    with open(vaivora_constants.values.filenames.valid_db, 'a') as f:
        n = str(srvnm) + ".db"
        if not n in '\n'.join(g):
            f.write(n + "\n")
    h = open(vaivora_constants.values.filenames.welcomed, 'r')
    with open(vaivora_constants.values.filenames.welcomed, 'a') as f:
        if not srvnm in '\n'.join(h):
            f.write(srvnm + "\n")
            await client.send_message(server.owner, vaivora_constants.values.words.message.welcome)
    return True

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
          'Demon Lord Blut',
          'Legwyn Crystal Event']
#   field bosses
bossfl = bosses[0:3] + [bosses[7], bosses[9],] + bosses[11:14] + bosses[17:-1]
#   world bosses
bosswo = [b for b in bosses if b not in bossfl]

# 'name'es that 'alt'ernate
bosalt = ['Mirtis',
          'Rexipher',
          'Helgasercle',
          'Demon Lord Marnox']

# 'name' - N - 'special'
#   list of bosses with unusual spawn time of 2h
bos02s = ['Abomination',
          'Dullahan Event']
#   list of bosses with unusual spawn time of 16h
bos16s = ['Demon Lord Nuaele',
          'Demon Lord Zaura',
          'Demon Lord Blut']
boseve = ['Kubas Event',
          'Dullahan Event',
          'Legwyn Crystal Event']

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
          'Demon Lord Blut':['blut'],
          'Legwyn Crystal Event':['legwyn','crystal']}

# 'boss synonyms short'
# - list of synonyms of boss names
bossns = []
for l in list(bossyn.values()):
    bossns.extend(l)

# 'boss location'
# - keys: boss names (var `bosses`)
# - values: list of locations, full name
    bosslo = {'Blasphemous Deathweaver':['Crystal Mine 2F',
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
                                 'Tevhrin Stalactite Cave Section 5'],
              'Legwyn Crystal Event':['Residence of the Fallen Legwyn Family']
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
@client.event
async def on_message(message):
    # 'name' channel processing
    if not message.channel or not message.channel.name:
        # ignore direct messages for now
        return

    if "timer" in message.channel.name or "boss" in message.channel.name:
        command_server  = message.server.id # changed to id
        command_message = message.content
    
        # TODO: Replace hard-coded words with custom setting if set
        if vaivora_constants.regex.boss.command.prefix.match(command_message):
            # sanitize & standardize
            command_message = vaivora_constants.regex.format.matching.to_sanitize.sub('', command_message)
            command_message = command_message.lower()             
            # strip leading command/arg
            command_message = vaivora_constants.regex.boss.command.prefix.sub('', command_message)
            message_args    = dict() # keys(): name, channel, map, time, 
            boss_channel    = 1
            maps_idx        = -1

            # if odd amount of quotes, drop
            if len(vaivora_constants.regex.format.matching.quotes.findall(command_message)) % 2:
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][4], vaivora_constants.regex.commands.boss)
                return err_code

            # command: list of arguments
            command = shlex.split(command_message)
            if command[0] == "help":
                await client.send_message(message.channel, message.author.mention + " " + \
                                          vaivora_constants.command.boss.command)
                return True

            # if command[0] == "synonyms"

            if len(command) < 2:
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][1], \
                                       vaivora_constants.regex.commands.boss, command_message)
                return err_code

            # begin checking validity
            #     arg validity
            #         count: [3,5] - killed/anchored
            #                [2,3] - erase
            if (vaivora_constants.regex.boss.status.all_status.match(command[1]) and \
               (len(command) < vaivora_constants.command.boss.arg_min or len(command) > vaivora_constants.command.boss.arg_max)):
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][2], \
                                       vaivora_constants.regex.commands.boss, len(command))
                return err_code

            if (vaivora_constants.regex.boss.command.arg_erase.match(command[1]) and (len(command) < 2 or len(command) > 3)): #### TODO: change constants
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][2], \
                                       vaivora_constants.regex.commands.boss, len(command))
                return err_code

            #         boss: letters
            #         status: anchored, died
            #         time: format
            if not vaivora_constants.regex.format.matching.letters.match(command[0]):
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][1], \
                                       vaivora_constants.regex.commands.boss)
                return err_code
            if not (vaivora_constants.regex.boss.status.all_status.match(command[1]) or \
               vaivora_constants.regex.boss.command.arg_erase.match(command[1]) or \
               vaivora_constants.regex.boss.command.arg_list.match(command[1])): 
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][1], \
                                       vaivora_constants.regex.commands.boss)
                return err_code
            if vaivora_constants.regex.boss.status.all_status.match(command[1]) and not vaivora_constants.regex.format.time.full.match(command[2]):
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][1], \
                                       vaivora_constants.regex.commands.boss)
                return err_code

            #     boss validity
            #         all list
            bossrec_str = list()
            if vaivora_constants.regex.boss.command.arg_all.match(command[0]) and \
               vaivora_constants.regex.boss.command.arg_list.match(command[1]):
                bossrec = await func_discord_db(command_server, check_boss_db, bosses) # possible return
                if not bossrec: # empty
                    await client.send_message(message.channel, message.author.mention + " No results found! Try a different boss.")
                    return True
                for brec in bossrec:
                    recdate = datetime(int(brec[5]), \
                                       int(brec[6]), \
                                       int(brec[7]), \
                                       int(brec[8]), \
                                       int(brec[9])) \
                              + vaivora_constants.values.time.offset.pacific2server
                    tense = " and "
                    tense_time = " minutes "
                    difftime = datetime.now()+vaivora_constants.values.time.offset.pacific2server-recdate
                    days = int(difftime.days)
                    if days >= 0:
                        tense += "should have respawned at "
                        tense_time += "ago"
                        tense_mins = int(difftime.seconds / 60) + int(difftime.days*vaivora_constants.values.time.seconds.in_day/60)
                    else:
                        tense += "will respawn around "
                        tense_time += "from now"
                        tense_mins = int((vaivora_constants.values.time.seconds.in_day - difftime.seconds) / 60)

                    if tense_mins > 0:
                        tense_mins = str(int(tense_mins/60)) + " hours, " + str(tense_mins % 60)
                    elif tense_mins < 0:
                        tense_mins = str(int(24 + tense_mins/60)) + " hours, " + str(tense_mins % 60)
                    else:
                        tense_mins = str(tense_mins)

                    if days > 1:
                        tense_mins = str(abs(days)) + " days, " + tense_mins
                    elif days > 0:
                        tense_mins = str(abs(days)) + " day, " + tense_mins


                    bossrec_str.append("\"" + brec[0] + "\" " + brec[3] + " in ch." + str(int(brec[1])) + tense + \
                                       recdate.strftime("%Y/%m/%d \"%H:%M\"") + \
                                       " (" + tense_mins + tense_time + ")" + \
                                       ". Last known map: # " + brec[2])
                await client.send_message(message.channel, message.author.mention + " Records: ```python\n" + \
                                          '\n\n'.join(bossrec_str) + "\n```")
                return True

            elif vaivora_constants.regex.boss.command.arg_all.match(command[0]) and \
              vaivora_constants.regex.boss.command.arg_erase.match(command[1]):
                for boss in bosses:
                    await func_discord_db(command_server, rm_ent_boss_db, xargs=boss)
                await client.send_message(message.channel, message.author.mention + " Records successfully erased.\n")
                return True

            elif vaivora_constants.regex.boss.command.arg_all.match(command[0]):
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][1], \
                                       vaivora_constants.regex.commands.boss)
                return err_code
            
            boss_idx = await check_boss(command[0])
            if boss_idx < 0  or boss_idx >= len(bosses):
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][1], \
                                       vaivora_constants.regex.commands.boss, command[0])
                return err_code

            #         boss erase
            if vaivora_constants.regex.boss.command.arg_erase.match(command[1]) and len(command) < 3:
                await func_discord_db(command_server, rm_ent_boss_db, bosses[boss_idx])
                await client.send_message(message.channel, message.author.mention + " Record successfully erased.\n")
                return True
            elif vaivora_constants.regex.boss.command.arg_erase.match(command[1]):
                await func_discord_db(command_server, rm_ent_boss_db, (bosses[boss_idx], command[2],))
                await client.send_message(message.channel, message.author.mention + " Record successfully erased.\n")
                return True

            #         boss list
            bossrec_str = list()
            if vaivora_constants.regex.boss.command.arg_list.match(command[1]):
                bossrec = await func_discord_db(command_server, check_boss_db, (bosses[boss_idx],)) # possible return
                if not bossrec: # empty
                    await client.send_message(message.channel, message.author.mention + " No results found! Try a different boss.\n")
                    return True
                for brec in bossrec:
                    # following block should be made into function
                    recdate = datetime(int(brec[5]), \
                                       int(brec[6]), \
                                       int(brec[7]), \
                                       int(brec[8]), \
                                       int(brec[9])) \
                              + vaivora_constants.values.time.offset.pacific2server
                    tense = " and "
                    tense_time = " minutes "
                    difftime = datetime.now()+vaivora_constants.values.time.offset.pacific2server-recdate
                    if int(difftime.days) >= 0:
                        tense += "should have respawned at "
                        tense_time += "ago"
                        tense_mins = int(difftime.seconds / 60)
                    else:
                        tense += "will respawn around "
                        tense_time += "from now"
                        tense_mins = int((vaivora_constants.values.time.seconds.in_day - difftime.seconds) / 60)

                    if tense_mins > 99:
                        tense_mins = str(int(tense_mins/60)) + " hours, " + str(tense_mins % 60)
                    elif tense_mins < 0:
                        tense_mins = str(int(24 + tense_mins/60)) + " hours, " + str(tense_mins % 60)
                    else:
                        tense_mins = str(tense_mins)

                    bossrec_str.append("\"" + brec[0] + "\" " + brec[3] + " in ch." + str(int(brec[1])) + tense + \
                                       recdate.strftime("%Y/%m/%d \"%H:%M\"") + \
                                       " (" + str(tense_mins) + tense_time + ")" + \
                                       ". Last known map: # " + brec[2])
                await client.send_message(message.channel, message.author.mention + " Records: ```python\n" + \
                                          '\n\n'.join(bossrec_str) + "\n```")
                return True


            #     (opt) channel: reject if field boss & ch > 1 or if ch > 4
            #     (opt) map: validity
            ##### TODO: Make channel limit specific per boss
            if len(command) > 3:
                #     channel is set
                #     keep track of arg position in case we have 5
                argpos = 3
                if vaivora_constants.regex.boss.location.channel.match(command[argpos]):
                    boss_channel = int(vaivora_constants.regex.format.matching.letters.sub('', command[argpos]))
                    argpos += 1

                #     specifically not an elif - sequential handling of args
                #     cases:
                #         4 args: 4th arg is channel
                #         4 args: 4th arg is map
                #         5 args: 4th and 5th arg are channel and map respectively
                try:
                    if not vaivora_constants.regex.boss.location.channel.match(command[argpos]) or len(command) == 5 or bosses[boss_idx] in bossfl:
                        maps_idx = await check_maps(command[argpos], bosses[boss_idx])
                        if maps_idx < 0 or maps_idx >= len(bosslo[boss]):
                            err_code = await error(message.author, message.channel, \
                                                   vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][2], vaivora_constants.regex.commands.boss, command[1])
                            return err_code
                except:
                    pass

            #         check if boss is a field boss, and discard if boss channel is not 1
            if bosses[boss_idx] in bossfl and boss_channel != 1:
                err_code = await error(message.author, message.channel, vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][4], vaivora_constants.regex.commands.boss, boss_channel, bosses[boss_idx])
                return err_code

            # everything looks good if the string passes through
            # begin compiling record in dict form 'message_args'
            message_args['name'] = bosses[boss_idx]
            message_args['channel'] = boss_channel
            if maps_idx >= 0:
                message_args['map'] = bosslo[message_args['name']][maps_idx]
            elif not message_args['name'] in bossfl:
                message_args['map'] = bosslo[message_args['name']][0]
            else:
                message_args['map'] = 'N/A'

            # process time
            #     antemeridian
            if vaivora_constants.regex.format.time.am.search(command[2]):
                btime = vaivora_constants.regex.format.time.delim.split(vaivora_constants.regex.format.time.am.sub('', command[2]))
                bhour = int(btime[0]) % 12
            #     postmeridian
            elif vaivora_constants.regex.format.time.pm.search(command[2]):
                btime = vaivora_constants.regex.format.time.delim.split(vaivora_constants.regex.format.time.pm.sub('', command[2]))
                bhour = (int(btime[0]) % 12) + 12
            #     24h time
            else:
                btime = command[2].split(':')
                bhour = int(btime[0])
            #     handle bad input

            if bhour > 24:
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.BOSS][3], \
                                       vaivora_constants.regex.commands.boss, msg=command[2])
                return err_code
            bminu = int(btime[1])
            oribhour  = bhour
            approx_server_time = datetime.now() + vaivora_constants.values.time.offset.pacific2server
            btday = approx_server_time.day if bhour <= int((datetime.now() + vaivora_constants.values.time.offset.pacific2server).hour) \
                                           else (approx_server_time.day-1)
            btmon = approx_server_time.month
            byear = approx_server_time.year

            # late recorded time; correct with -1 day
            mdate = datetime(byear, btmon, btday, hour=bhour, minute=bminu)
            tdiff = approx_server_time-mdate
            if tdiff.seconds < 0:  #or tdiff.seconds > 64800:
                with open(vaivora_constants.values.filenames.debug_file,'a') as f:
                    f.write("server", message.server, "; tdiff", tdiff, "; mdate",mdate)
                return await error(message.author, message.channel, vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][3], vaivora_constants.regex.commands.boss, msg=command[2])

            #wait_time = vaivora_constants.values.time.offset.anchor_spawn if vaivora_constants.regex.boss.status.anchored.match(command[1]) else vaivora_constants.values.time.offset.boss_spawn_04h
            wait_time = vaivora_constants.values.time.offset.boss_spawn_04h + \
                        vaivora_constants.values.time.offset.server2pacific
            print(wait_time)
            bhour = bhour + (int(wait_time.seconds) / 3600) # bhour in Pacific/local
            print(wait_time.seconds)
            if message_args['name'] in boseve and vaivora_constants.regex.boss.status.anchored.match(command[1]):
                return await error(message.author, message.channel, \
                                   vaivora_constants.command.syntax.cmd_error\
                                   [vaivora_constants.command.syntax.R]\
                                   [vaivora_constants.command.syntax.BAD]\
                                   [vaivora_constants.command.syntax.BOSS][5], \
                                   vaivora_constants.regex.commands.boss, msg=command[1])
            elif message_args['name'] in bos02s or vaivora_constants.regex.boss.status.warning.match(command[1]):
                if bhour < 2:
                    bhour += 22
                    btday -= 1
                else:
                    bhour -= 2
            elif message_args['name'] in bos16s:
                bhour += 12 # 12 + 4 = 16
                
            print(bhour)
            if int(bhour / 24):
                bhour = bhour % 24
                tomorrow = (datetime(byear, btmon, btday)+timedelta(days=1))
                btday = tomorrow.day
                btmon = tomorrow.month
                byear = tomorrow.year

            # add them to dict
            message_args['hour']      = bhour
            message_args['mins']      = bminu
            message_args['day']       = btday
            message_args['month']     = btmon
            message_args['year']      = byear
            message_args['status']    = command[1] # anchored or died
            message_args['srvchn']    = message.channel.id

            status  = await func_discord_db(command_server, validate_discord_db)
            if not status: # db is not valid
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error\
                                       [vaivora_constants.command.syntax.R]\
                                       [vaivora_constants.command.syntax.BAD]\
                                       [vaivora_constants.command.syntax.SYN][3], \
                                       vaivora_constants.regex.commands.boss)
                await func_discord_db(command_server, create_discord_db) # (re)create db
                return err_code

            status = await func_discord_db(command_server, update_boss_db, message_args)
            if not status: # update_boss_db failed
                err_code = await error(message.author, message.channel, \
                                       vaivora_constants.command.syntax.cmd_error\
                                       [vaivora_constants.command.syntax.R][0], \
                                       vaivora_constants.regex.commands.boss)
                return err_code

            await client.send_message(message.channel, message.author.mention + " " + \
                                      vaivora_constants.command.boss.acknowledge + \
                                      message_args['name'] + " " + message_args['status'] + " at " + \
                                      ("0" if oribhour < 10 else "") + \
                                      str(oribhour) + ":" + \
                                      ("0" if message_args['mins'] < 10 else "") + \
                                      str(message_args['mins']) + ", CH" + str(message_args['channel']) + ": " + \
                                      (message_args['map'] if message_args['map'] != "N/A" else ""))

            #await client.process_commands(message)
            return True # command processed
    
    elif vaivora_constants.fun.ohoho.search(message.content):
        await client.send_message(message.channel, "https://youtu.be/XzBCBIVC7Qg?t=12s")
        return True
    elif vaivora_constants.fun.meme.match(message.content):
        await client.send_message(message.channel, message.author.mention + " " + "http://i.imgur.com/xiuxzUW.png")
        return True
    else:
        #await client.process_commands(message)
        return False

def get_file_length(f):
    with open(f) as a_file:
        n = -1
        for n, ln in enumerate(f):
            pass
        return n + 1

# @func:    check_databases()
async def check_databases():
    await client.wait_until_ready()
    results = dict()
    today = datetime.today() # check on first launch

    while not client.is_closed:
        await asyncio.sleep(60)
        valid_dbs = []
        no_repeat = []
        try:
            f = open(vaivora_constants.values.filenames.valid_db,'r')
        except:
            open(vaivora_constants.values.filenames.valid_db,'a').close()
            f = open(vaivora_constants.values.filenames.valid_db,'r')
        try:
            g = open(vaivora_constants.values.filenames.no_repeat,'r')
        except:
            open(vaivora_constants.values.filenames.no_repeat,'a').close()
            g = open(vaivora_constants.values.filenames.no_repeat,'r')
        for line_f in f:
            valid_dbs.append(line_f.strip())
        for line_g in g:
            no_repeat.append(line_g.strip())
        print("Valid DBs: ", len(valid_dbs))
        for valid_db in valid_dbs:
            # check all timers
            message_send = list()
            cur_channel = str()
            results[valid_db] = await func_discord_db(valid_db, check_boss_db, bosses)
            # sort by time
            if not results[valid_db]:
                continue
            results[valid_db].sort(key=itemgetter(5,6,7,8,9))
            for result in results[valid_db]:
                list_time = [int(t) for t in result[5:10]]
                try:
                    rtime = datetime(*list_time)
                except:
                    #TODO: remove entry
                    continue
                rtime_east = rtime + vaivora_constants.values.time.offset.pacific2server
                tdiff = rtime-datetime.now()
                # if tdiff < 0: # stale data; delete
                #     await func_discord_db(valid_db, rm_ent_boss_db, bd=result)
                # elif tdiff.seconds < 10800 and vaivora_constants.regex.boss.status.anchored.match(result[3]):
                #     message_send.append(format_message_boss(result[0], result[3], rtime_east, result[1]))
                #elif
                if tdiff.days < 0:
                    continue
                if tdiff.seconds < 900 and tdiff.days == 0:
                    msgb = []
                    msgb.append(format_message_boss(result[0], result[3], rtime_east, result[2], result[1]))
                    msgb.append(str(result[4]),)
                    strm = str(result[4]) + ":" + str(result[0]) + ":" + str(result[3]) + ":" + \
                           str(rtime_east) + ":" + str(result[1]) + "\n"
                    if strm.rstrip() in no_repeat or strm in no_repeat:
                        continue
                    else:
                        with open(vaivora_constants.values.filenames.no_repeat, 'a') as h:
                            h.write(strm)
                        message_send.append(msgb)
                # elif tdiff.seconds > 72000:
                #     await func_discord_db(valid_db, rm_ent_boss_db, result)
            # message: str, str
            if len(message_send) == 0:
                continue
            # right_now = datetime.now()
            # dated_fil = "-" + str(right_now.year) + str(right_now.month) + str(right_now.day) + \
            #             "." + str(right_now.hour) + str(right_now.minute)
            # # remove clutter while nothing is reported
            # os.rename(vaivora_constants.values.filenames.no_repeat, vaivora_constants.values.filenames.no_repeat + dated_fil)
            # with open('wings-norepeat-temp','a')
            # len(line_g)-len(message_send)
            # for i in range(len(line_g)):
            # implement later.

            r = "@here"
            srv = client.get_server(vaivora_constants.regex.db.ext.sub('', valid_db))
            for role in srv.roles:
                if role.mentionable and role.name == "Boss Hunter":
                    r = role.mention
                    break
            cur_channel = ''
            for message in message_send:
                if cur_channel != message[-1] and not vaivora_constants.regex.format.matching.letters.match(message[-1]):
                    if cur_channel:
                        messtr += "```"
                        await client.send_message(srv.get_channel(cur_channel), messtr)
                    cur_channel = message[-1]
                    #TODO: Replace 15 with custom server time threshold
                    messtr = r + " The following bosses will spawn within " + "15" + " minutes: ```python\n"
                messtr += message[0]
            # flush
            messtr += "```"
            await client.send_message(srv.get_channel(cur_channel), messtr)
        #await client.process_commands(message)
        f.close()
        g.close()
        await asyncio.sleep(1)

def format_message_boss(boss, status, time, bossmap, channel):
    if status == "warned":
        bossmap = [(bossmap,)]
    elif not boss in bossfl:
        bossmap = bosslo[boss]
    elif bossmap == 'N/A':
        bossmap = ['[Map Unknown]',]
    elif boss == "Blasphemous Deathweaver" and re.search("[Aa]shaq", bossmap):
        bossmap = [m for m in bosslo[boss][2:-1] if m != bossmap]
    elif boss == "Blasphemous Deathweaver":
        bossmap = [m for m in bosslo[boss][0:2] if m != bossmap]
    else:
        bossmap = [m for m in bosslo[boss] if m != bossmap]

    if vaivora_constants.regex.boss.status.anchored.search(status):
        report_time = time+timedelta(hours=-3)
        status_str = " was anchored"
    elif vaivora_constants.regex.boss.status.warning.search(status):
        report_time = time+timedelta(hours=-2)
        status_str = " was warned to spawn"
    else:
        if boss in bos02s:
            report_time = time+timedelta(hours=-2)
        elif boss in bos16s:
            report_time = time+timedelta(hours=-16)
            print(report_time)
        else:
            report_time = time+timedelta(hours=-4)
        status_str = " died"

    status_str  = status_str + " in ch." + str(int(channel)) + " at "
    # if boss not in bos16s and boss not in bos02s:
    #     time_exp    = vaivora_constants.values.time.offset.boss_spawn_04h
    # elif boss in bos16s:
    #     time_exp    = con['TIME.WAIT.16H']
    # elif boss in bos02s:
    #     time_exp    = con['TIME.WAIT.2H']
    expect_str  = (("between " + (time-timedelta(hours=1)).strftime("%Y/%m/%d %H:%M") + " and ") \
                   if vaivora_constants.regex.boss.status.anchored.match(status) else "at ") + \
                  (time).strftime("%Y/%m/%d %H:%M") + \
                  " (in " + str(int((time-datetime.now()+vaivora_constants.values.time.offset.server2pacific).seconds/60)) + " minutes)"

    if "[Map Unknown]" in bossmap:
        map_str     = '.'
    else:
        map_str     = ", in one of the the following maps:" + '\n#    ' + '\n#    '.join(bossmap[0:])
    message     = "\"" + boss + "\"" + status_str + report_time.strftime("%Y/%m/%d %H:%M") + ", and should spawn " + \
                  expect_str + map_str + "\n"
    return message

# @func:    check_boss(str): begin code for checking boss validity
# @arg:
#     boss: str; boss name from raw input
# @return:
#     boss index in list, or -1 if not found
async def check_boss(boss):
    for bossa in bosses:
        if boss in bossa.lower():
            return bosses.index(bossa)
    else:
        # for b in bosses:
        #     if b in boss:
        #         return bosses.index(b)
        for b, syns in bossyn.items():
            if boss in syns or b in boss:
                return bosses.index(b)
    return -1
# end of check_boss

# @func:    check_maps(str, str): begin code for checking map validity
# @arg:
#     maps: str; map name from raw input
#     boss: str; the corresponding boss
# @return:
#     map index in list, or -1 if not found
async def check_maps(maps, boss):
    if boss == "Blasphemous Deathweaver" and not vaivora_constants.regex.boss.location.loc[DW][A].search(maps):
        return -1

    elif vaivora_constants.regex.boss.location.floors_fmt.search(maps) or boss == "Blasphemous Deathweaver":
        # rearrange letters, and remove map name
        if boss == "Wrathful Harpeia":
            mapnum = vaivora_constants.regex.boss.location.floors_fmt.sub(r'\g<floornumber>', maps)
            maps = "Demon Prison District " + mapnum
        else:
            mapnum = vaivora_constants.regex.boss.location.floors_fmt.sub(r'\g<district>\g<basement>\g<floornumber>\g<floor>', maps)
            mapnum = str(mapnum).upper()

        
        if boss == "Blasphemous Deathweaver" and vaivora_constants.regex.boss.location.loc[DW][CM].search(maps):
            mapnum = vaivora_constants.regex.boss.location.loc[DW][CM].sub('', mapnum) # erase name and redo
            maps = "Crystal Mine " + mapnum
        elif boss == "Blasphemous Deathweaver":
            mapnum = vaivora_constants.regex.boss.location.loc[DW][AS].sub('', mapnum) # erase name and redo
            maps = "Ashaq Underground Prison " + mapnum
        # elif boss == "Wrathful Harpeia":
        #     if vaivora_constants.regex.boss.location.loc[HA][A].search(maps):
        #         mapnum = vaivora_constants.regex.boss.location.loc[HA][A].sub('', mapnum) # erase name and redo
        #     if vaivora_constants.regex.boss.location.floors_chk.search(maps):
        #         mapnum = vaivora_constants.regex.boss.location.floors_chk.sub('', mapnum) # erase d or f; doesn't matter!
        #     if vaivora_constants.regex.boss.location.loc[HA][DP].search(maps):
        #         mapnum = vaivora_constants.regex.boss.location.loc[HA][DN].sub('', mapnum) # erase district, keep number, and redo
        #     maps = "Demon Prison District " + mapnum
    # elif vaivora_constants.regex.format.matching.one_number.search(maps) and boss != "Bleak Chapparition":
    #     mapname = vaivora_constants.regex.format.matching.one_number.sub('', bosslo[boss][0])
    #     maps = mapname + maps

    mapidx = -1
    for m in bosslo[boss]:
        if m.lower() in maps.lower():
            if mapidx != -1:
                return -1
            mapidx = bosslo[boss].index(m)
        elif maps.lower() in m.lower():
            if mapidx != -1:
                return -1
            mapidx = bosslo[boss].index(m)
    return mapidx

# @func:  error(**): begin code for error message printing to user
# @arg:
#     user:     Discord.user
#     channel:  server channel
#     etype:    [e]rror type
#     ecmd:     [e]rror (invoked by) command
#     msg:      (optional) message for better error clarity
# @return:
#     -1:     BROAD:  the command was correctly formed but the argument is too broad
#     -2:     WRONG:  the command was correctly formed but could not validate arguments
#     -127:   SYNTAX: malformed command: quote mismatch, argument count
async def error(user, channel, etype, ecmd, msg='', xmsg=''):
    # get the user in mentionable string
    user_name = user.mention
    # convert args
    if msg:
        msg = str(msg)
    if xmsg:
        xmsg = str(xmsg)
    # prepare a list to send message
    ret_msg   = list()

    # boss command only
    if ecmd == vaivora_constants.regex.commands.boss:
        # broad
        if etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][1]:
            ret_msg.append(user_name + the_following_argument('name') + msg + \
                           ") for `$boss` has multiple matching spawn points:\n")
            ret_msg.append(cmd_usage['code_block'])
            ret_msg.append('\n'.join(bosslo[msg]))
            ret_msg.append(cmd_usage['code_block'])
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][2])
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.B][2])
            ecode = vaivora_constants.values.error_codes.broad
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][0]:
            ret_msg.append(user_name + " I'm sorry. Your command failed for unknown reasons.\n" + \
                           "This command failure has been recorded.\n" + \
                           "Please try again shortly.\n")
            with open('wings_of_vaivora-error.txt', 'a') as f:
                f.write(str(datetime.today()) + " An error was detected when " + user_name + " sent a command.")
            ecode = vaivora_constants.values.error_codes.wrong
        # unknown boss
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][1]:
            ret_msg.append(user_name + the_following_argument('name') + msg + \
                           ") is invalid for `$boss`. This is a list of bosses you may use:\n")
            ret_msg.append(cmd_usage['code_block'])
            ret_msg.append('\n'.join(bosses))
            ret_msg.append(cmd_usage['code_block'])
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.B][1])
            ecode = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][5]:
            ret_msg.append(user_name + the_following_argument('status') + msg + \
                           ") is invalid for `$boss`. You may not select `anchored` for its status.\n")
            ecode = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][2]:
            try_msg = list()
            try_msg.append(user_name + the_following_argument('map') + msg + \
                           ") (number) is invalid for `$boss`. This is a list of maps you may use:\n")
            try: # make sure the data is valid by `try`ing
              try_msg.append(cmd_usage['code_block'])
              try_msg.append('\n'.join(bosslo[xmsg]))
              try_msg.append(cmd_usage['code_block'])
              try_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.B][2])
              # seems to have succeeded, so extend to original
              ret_msg.extend(try_msg)
              ecode = vaivora_constants.values.error_codes.wrong
            except: # boss not found! 
              ret_msg.append(user_name + cmd_usage['debug'])
              ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
              ecode = vaivora_constants.values.error_codes.syntax
              with open(vaivora_constants.values.filenames.debug_file, 'a') as f:
                  f.write('boss not found\n')
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][4]:
            ret_msg.append(user_name + the_following_argument('channel') + msg + \
                           ") (number) is invalid for `$boss`. " + xmsg + " is a field boss, thus " + \
                           "variants that spawn on channels other than 1 (or other maps) are considered world bosses " + \
                           "with unpredictable spawns.\n")
            ecode = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][3]:
            ret_msg.append(user_name + the_following_argument('time') + msg + \
                           ") is invalid for `$boss`.\n")
            ret_msg.append("Omit spaces; record in 12H (with AM/PM) or 24H time.\n")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
            ecode = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.BOSS][5]:
            ret_msg.append(user_name + the_following_argument('status') + 'anchored' + \
                           ") is invalid for `$boss`.\n" +
                           "You cannot anchor events or bosses of this kind.\n")
            ecode = vaivora_constants.values.error_codes.wrong
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.SYN][2]:
            ret_msg.append(user_name + " Your command for `$boss` had too few arguments.\n" + \
                           "Expected: 4 to 6; got: " + msg + ".\n")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
            ecode = vaivora_constants.values.error_codes.syntax
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.SYN][4]:
            ret_msg.append(user_name + " Your command for `$boss` had misused quotes somewhere.\n")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
            ecode = vaivora_constants.values.error_codes.syntax
        elif etype == vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.R][vaivora_constants.command.syntax.BAD][vaivora_constants.command.syntax.SYN][1]:
            ret_msg.append(user_name + " Your command could not be parsed. Re-check the syntax, and try again.\n" + \
                           ("Message: " + msg) if msg else "")
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
            ecode = vaivora_constants.values.error_codes.syntax
        else:
            ret_msg.append(user_name + cmd_usage['debug'] + "\n" + etype)
            ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
            ecode = vaivora_constants.values.error_codes.syntax
            await client.send_message(channel, '\n'.join(ret_msg))
            return ecode
        # end of conditionals for vaivora_constants.regex.commands.boss

        # begin common return for $boss
        ret_msg.append("For syntax: $boss help")
        await client.send_message(channel, '\n'.join(ret_msg))
        return ecode
        # end of common return for $boss

    # todo: reminders, Talt tracking, permissions
    else:
        # todo
        ret_msg.append(user_name + cmd_usage['debug'])
        ret_msg.append(vaivora_constants.command.syntax.cmd_error[vaivora_constants.command.syntax.G][1])
        ecode = vaivora_constants.values.error_codes.syntax
        await client.send_message(channel, '\n'.join(ret_msg))
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

with open('discordtoken', 'r') as f:
    secret = f.read()

client.loop.create_task(check_databases())
client.run(secret)