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

# basic declarations and initializations
client    = discord.Client()

# variables to use
#valid_dbs = list()

# begin constants for strings for error messages
#   command - usage
cmd_usage = dict()
cmd_usage['heading']      = "`+` Usage:"
#   command - [us]age - [c]ode [bl]oc[k]
cmd_usage['code_block']   = "```"
#   command - [us]age - [a]rguments [bl]oc[k]
cmd_usage['back_tick']    = "`"
#   command - [us]age - [c]ode [arg]uments
cmd_usage['heading.arg']  = "Arguments:\n"
cmd_usage['debug']        = " Debug message. Something went wrong.\n"

#   begin $boss specific constants
cmd_usage['boss.arg.1']   = "boss"
cmd_usage['boss.prefix']  = ("$boss ", "Vaivora, boss ")
cmd_usage['name']         = ["***'Boss' commands*** [`$boss`]"]
cmd_usage['name'].append(cmd_usage['heading'])
cmd_usage['name'].append(cmd_usage['code_block'])
#   end of $boss specific constants
# end of constants for strings for error messages

# begin $boss usage string, in cmd_usage['name'] : list
#     command - usage - [b]oss - [n]th command -- reuse after every append
#         boss arg [n] - cmd_usage['boss.args'][n]
cmd_usage['boss.args'] = list()
cmd_usage['boss.args'].append(cmd_usage['boss.arg.1'] + " (died|anchored|warned) time [chN] [map]\n",)
cmd_usage['boss.args'].append("(boss|all) (erase|list) [chN]\n",)

cmd_usage['name'].append('\n'.join([("PREFIX " + boss_arg) for boss_arg in cmd_usage['boss.args']]))
cmd_usage['name'].append(cmd_usage['code_block'])
cmd_usage['name'].append("`+` Valid " + cmd_usage['back_tick'] + "PREFIX" + cmd_usage['back_tick'] + "es: `" + \
                         '` & `'.join(cmd_usage['boss.prefix']) + "`\n")

# cmd_usage['name'].append('\n'.join([(' '.join(t) for t in zip(cmd_usage['boss.prefix'], cmd_usage['boss.args'][1]*2))]))
# cmd_usage['name'].append('\n'.join([(' '.join(t) for t in zip(cmd_usage['boss.prefix'], cmd_usage['boss.args'][2]*2))]))
# cmd_usage['name'].append('\n'.join([(' '.join(t) for t in zip(cmd_usage['boss.prefix'], cmd_usage['boss.args'][3]*2))]))
#     command - usage - [b]oss - [a]rgument descriptors
#             n=5
cmd_usage['boss.arg'] = "`+` `boss` or `all`\n" + \
                "`+`   Either part of, or full name; if spaced, enclose in double-quotes (`\"`)\n" + \
                "`-`   `all` for all bosses\n" + \
                "`+` `died`|`anchored`|`warned`\n" + \
                "`-`   Valid for `boss` only, to indicate its status. Do not use with `erase` or `list`.\n" + \
                "`+` `erase`|`list`\n" + \
                "`-`   Valid for both `boss` and `all`, to `erase` or `list` entries. Do not use with `died`, `anchored`, or `warned`.\n" + \
                "`+` `time` **(required for `died` and `anchored`)**\n" + \
                "`-`   Remove spaces. 12 hour and 24 hour times acceptable, with valid delimiters `:` and `.`. Use server time.\n" + \
                "`+` `map` *(optional)*\n" + \
                "`-`   Handy for field bosses* only. If unlisted, this will be unassumed.\n" + \
                "`+` `chN` *(optional)*\n" + \
                "`-`   Suitable only for world bosses.* If unlisted, CH1 will be assumed.\n" + \
                "\n" + \
                "`.` * Notes about world and field bosses: Field bosses in channels other than 1 are considered 'world boss' variants.\n" + \
                "`.`    and should not be recorded because they have unpredictable spawns.\n"
cmd_usage['boss.examples'] = "`+` **`$boss` Examples:**\n" + \
                             "`-`  `$boss cerb died 12:00pm 4f` - channel can be omitted for field bosses\n" + \
                             "`-`  `Vaivora, crab died 14:00 ch2` - map can be omitted for world bosses\n"
cmd_usage['name'].append(cmd_usage['boss.arg'])
cmd_usage['name'].append(cmd_usage['boss.examples'])
# end of $boss usage string, in cmd_usage['boss.args']

cmd_usage['boss.acknowledged'] = " Thank you! Your command has been acknowledged and recorded.\n"

# begin constants to use for error(**)
#     general command errors
cmd_usage['error.badsyntax']  = "Your command was malformed.\n"
cmd_usage['error.ambiguous']  = "Your command was ambiguous.\n"

#     specific command errors
#         command - usage - [b]oss - [m]ap
cmd_usage['boss.name']        = "Make sure to properly spell the boss name.\n"
cmd_usage['boss.map']         = "Make sure to properly record the map.\n"
cmd_usage['boss.status']      = "Make sure to properly record the status.\n"
# end of constants for error(**)

# constants
#   constant dictionary
con = dict()
con['BOSSCMD.ARG.COUNTMIN'] = 3
con['BOSSCMD.ARG.COUNTMAX'] = 5
con['STR.REASON']           = "Reason: "
con['TIME.OFFSET.EASTERN']  = timedelta(hours=3)
con['TIME.OFFSET.PACIFIC']  = timedelta(hours=-3)
con['TIME.WAIT.4H']         = timedelta(hours=4)
con['TIME.WAIT.ANCHOR']     = timedelta(hours=3)
con['TIME.SECONDS.IN.DAY']  = 24 * 60 * 60
con['LOGGER']               = "tos.wingsofvaivora"
con['LOGGER.FILE']          = "tos.wingsofvaivora.log"
con['DEBUG.FILE']           = 'tos.wingsofvaivora.debug.log'
con['FILES.VALIDDB']        = 'wings-valid_db' #+ '_TEST'
con['FILES.NOREPEAT']       = 'wings-norepeat' #+ '_TEST'
con['FILES.WELCOMED']       = 'wings-welcomed' #+ '_TEST'
con['STR.MESSAGE.WELCOME']  = "Thank you for inviting me to your server! " + \
                              "I am a representative bot for the Wings of Vaivora, here to help you record your journey.\n" + \
                              "\nHere are some useful commands: \n\n" + \
                              '\n'.join(cmd_usage['name']) + \
                              '\n'*2 + \
                              "(To be implemented) Talt, Reminders, and Permissions. Check back soon!\n"
                              # '\n'.join(cmd_usage['talt']) # + \
                              # '\n'.join(cmd_usage['remi']) # + \
                              # '\n'.join(cmd_usage['perm'])
con['ERROR.BROAD']          = -1
con['ERROR.WRONG']          = -2
con['ERROR.SYNTAX']         = -127


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
# rx['boss.floors.arrange']   = re.compile(r'\g<floor>\g<floornumber>\g<basement>', re.IGNORECASE)
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
# cmd['talt']                 = "Command: Talt Tracker"
# cmd['reminders']            = "Command: Reminders"
#     error(**) constants for "reason" argument
#### TODO: Replace con['STR.REASON'] applied to each one? Priority: low
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
logger = logging.getLogger(con['LOGGER'])
logger.setLevel(logging.WARNING)
handler = logging.FileHandler(con['LOGGER.FILE'], encoding="utf-8")
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
    if rx['str.ext.db'].search(discord_server):
        discord_db = discord_server
    elif rx['str.fnm.db'].search(discord_server):
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
    if sorted(tuple(r.keys())) != sorted(prototype['boss']):
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
    if len(contents) >= 1: #and boss_dict['name'] not in bos16s:
        await rm_ent_boss_db(c, boss_dict)

    # if entry has newer data, discard previous
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
    if bd:
        rm_name, rm_channel = bd['name'], bd['channel']
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
        s = open(con['FILES.WELCOMED'], 'r')
    except:
        open(con['FILES.WELCOMED'], 'a').close()
        s = open(con['FILES.WELCOMED'], 'r')
    for server in client.servers:
        if not str(server.id) in s:
            await on_server_join(server)

    try:
        f = open(con['FILES.VALIDDB'], 'a')
    except:
        open(con['FILES.VALIDDB'], 'a').close()
        f = open(con['FILES.VALIDDB'], 'w')

    with open(con['FILES.VALIDDB'], 'r') as vdbs:
        valid_list = [ vdb.rstrip('\n') for vdb in vdbs ]
    with os.scandir() as items:
        for item in items:
            if item.is_file() and rx['str.fnm.db'].search(item.name) and rx['str.ext.db'].search(item.name) and \
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
        g = open(con['FILES.VALIDDB'], 'r')
    except:
        open(con['FILES.VALIDDB'], 'a').close()
        g = open(con['FILES.VALIDDB'], 'r')
    with open(con['FILES.VALIDDB'], 'a') as f:
        n = str(srvnm) + ".db"
        if not n in '\n'.join(g):
            f.write(n + "\n")
    h = open(con['FILES.WELCOMED'], 'r')
    with open(con['FILES.WELCOMED'], 'a') as f:
        if not srvnm in '\n'.join(h):
            f.write(srvnm + "\n")
            await client.send_message(server.owner, con['STR.MESSAGE.WELCOME'])
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
bos02s = ['Kubas Event',
          'Dullahan Event']
#   list of bosses with unusual spawn time of 16h
bos16s = ['Demon Lord Nuaele',
          'Demon Lord Zaura',
          'Demon Lord Blut']

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
        return
    if "timer" in message.channel.name or "boss" in message.channel.name:
        # 'name' channel command: $boss
        #     arg order:
        #         1. [0] req boss name
        #         2. [1] req status (killed, anchored)
        #         3. [2] req time
        #         4. [3] opt channel
        #         5. [4] opt map
        if message.content.startswith('$boss ') or \
           message.content.startswith('Vaivora, boss '):
            command_server  = message.server.id # changed to id
            command_message = message.content
            command_message = rx['format.letters.inv'].sub('', command_message)   # sanitize
            command_message = command_message.lower()             # standardize
            command_message = rx['vaivora.boss'].sub('', command_message)     # strip leading command/arg
            message_args    = dict() # keys(): name, channel, map, time, 
            boss_channel    = 1
            maps_idx        = -1


            # if odd amount of quotes, drop
            if len(rx['format.quotes'].findall(command_message)) % 2:
                err_code = await error(message.author, message.channel, reason['quote'], cmd['name'])
                return err_code

            # command: list of arguments
            command = shlex.split(command_message)
            if command[0] == "help":
                await client.send_message(message.channel, message.author.mention + '\n'.join(cmd_usage['name']))
                return True

            # if command[0] == "synonyms"

            if len(command) < 2:
                err_code = await error(message.author, message.channel, reason['syntx'], cmd['name'], command_message)
                return err_code

            # begin checking validity
            #     arg validity
            #         count: [3,5] - killed/anchored
            #                [2,3] - erase
            if (rx['boss.status'].match(command[1]) and (len(command) < con['BOSSCMD.ARG.COUNTMIN'] or len(command) > con['BOSSCMD.ARG.COUNTMAX'])):
                err_code = await error(message.author, message.channel, reason['argct'], cmd['name'], len(command))
                return err_code

            if (rx['boss.arg.erase'].match(command[1]) and (len(command) < 2 or len(command) > 3)): #### TODO: change constants
                err_code = await error(message.author, message.channel, reason['argct'], cmd['name'], len(command))
                return err_code

            #         boss: letters
            #         status: anchored, died
            #         time: format
            if not rx['format.letters'].match(command[0]):
                err_code = await error(message.author, message.channel, reason['syntx'], cmd['name'])
                return err_code
            if not (rx['boss.status'].match(command[1]) \
              or rx['boss.arg.erase'].match(command[1]) \
              or rx['boss.arg.list'].match(command[1])): 
                err_code = await error(message.author, message.channel, reason['syntx'], cmd['name'])
                return err_code
            if rx['boss.status'].match(command[1]) and not rx['format.time'].match(command[2]):
                err_code = await error(message.author, message.channel, reason['syntx'], cmd['name'])
                return err_code

            #     boss validity
            #         all list
            bossrec_str = list()
            if rx['boss.arg.all'].match(command[0]) and rx['boss.arg.list'].match(command[1]):
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
                              + con['TIME.OFFSET.EASTERN']
                    tense = " and "
                    tense_time = " minutes "
                    difftime = datetime.now()+con['TIME.OFFSET.EASTERN']-recdate
                    if int(difftime.days) >= 0:
                        tense += "should have respawned at "
                        tense_time += "ago"
                        tense_mins = int(difftime.seconds / 60)
                    else:
                        tense += "will respawn around "
                        tense_time += "from now"
                        tense_mins = int((con['TIME.SECONDS.IN.DAY'] - difftime.seconds)/60)
                    bossrec_str.append("\"" + brec[0] + "\" " + brec[3] + " in ch." + str(int(brec[1])) + tense + \
                                       recdate.strftime("%Y/%m/%d \"%H:%M\"") + \
                                       " (" + str(tense_mins) + tense_time + ")" + \
                                       ". Last known map: # " + brec[2])
                await client.send_message(message.channel, message.author.mention + " Records: ```python\n" + \
                                          '\n\n'.join(bossrec_str) + "\n```")
                return True

            elif rx['boss.arg.all'].match(command[0]) and rx['boss.arg.erase'].match(command[1]):
                for boss in bosses:
                    await func_discord_db(command_server, rm_ent_boss_db, xargs=boss)
                await client.send_message(message.channel, message.author.mention + " Records successfully erased.\n")
                return True

            elif rx['boss.arg.all'].match(command[0]):
                err_code = await error(message.author, message.channel, reason['syntx'], cmd['name'])
                return err_code
            
            boss_idx = await check_boss(command[0])
            if boss_idx < 0  or boss_idx >= len(bosses):
                err_code = await error(message.author, message.channel, reason['unknb'], cmd['name'], command[0])
                return err_code

            #         boss erase
            if rx['boss.arg.erase'].match(command[1]) and len(command) < 3:
                await func_discord_db(command_server, rm_ent_boss_db, bosses[boss_idx])
                await client.send_message(message.channel, message.author.mention + " Record successfully erased.\n")
                return True
            elif rx['boss.arg.erase'].match(command[1]):
                await func_discord_db(command_server, rm_ent_boss_db, (bosses[boss_idx], command[2],))
                await client.send_message(message.channel, message.author.mention + " Record successfully erased.\n")
                return True

            #         boss list
            bossrec_str = list()
            if rx['boss.arg.list'].match(command[1]):
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
                              + con['TIME.OFFSET.EASTERN']
                    tense = " and "
                    tense_time = " minutes "
                    difftime = datetime.now()+con['TIME.OFFSET.EASTERN']-recdate
                    if int(difftime.days) >= 0:
                        tense += "should have respawned at "
                        tense_time += "ago"
                        tense_mins = int(difftime.seconds / 60)
                    else:
                        tense += "will respawn around "
                        tense_time += "from now"
                        tense_mins = int((con['TIME.SECONDS.IN.DAY'] - difftime.seconds)/60)
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
                if rx['boss.channel'].match(command[argpos]):
                    boss_channel = int(rx['format.letters'].sub('', command[argpos]))
                    argpos += 1

                #     specifically not an elif - sequential handling of args
                #     cases:
                #         4 args: 4th arg is channel
                #         4 args: 4th arg is map
                #         5 args: 4th and 5th arg are channel and map respectively
                try:
                    if not rx['boss.channel'].match(command[argpos]) or len(command) == 5 or bosses[boss_idx] in bossfl:
                        maps_idx = await check_maps(command[argpos], bosses[boss_idx])
                        if maps_idx < 0 or maps_idx >= len(bosslo[boss]):
                            err_code = await error(message.author, message.channel, reason['bdmap'], cmd['name'], command[1])
                            return err_code
                except:
                    pass

            #         check if boss is a field boss, and discard if boss channel is not 1
            if bosses[boss_idx] in bossfl and boss_channel != 1:
                err_code = await error(message.author, message.channel, reason['fdbos'], cmd['name'], boss_channel, bosses[boss_idx])
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
            if rx['format.time.am'].search(command[2]):
                btime = rx['format.time.delim'].split(rx['format.time.am'].sub('', command[2]))
                bhour = int(btime[0]) % 12
            #     postmeridian
            elif rx['format.time.pm'].search(command[2]):
                btime = rx['format.time.delim'].split(rx['format.time.pm'].sub('', command[2]))
                bhour = (int(btime[0]) % 12) + 12
            #     24h time
            else:
                btime = command[2].split(':')
                bhour = int(btime[0])
            #     handle bad input

            if bhour > 24:
                err_code = await error(message.author, message.channel, reason['bdtme'], cmd['name'], msg=command[2])
                return err_code
            bminu = int(btime[1])
            oribhour  = bhour
            approx_server_time = datetime.now() + con['TIME.OFFSET.EASTERN']
            btday = approx_server_time.day if bhour <= int((datetime.now() + con['TIME.OFFSET.EASTERN']).hour) \
                                           else (approx_server_time.day-1)
            btmon = approx_server_time.month
            byear = approx_server_time.year

            # late recorded time; correct with -1 day
            mdate = datetime(byear, btmon, btday, hour=bhour, minute=bminu)
            tdiff = approx_server_time-mdate
            if tdiff.seconds < 0:  #or tdiff.seconds > 64800:
                with open(con['DEBUG.FILE'],'a') as f:
                    f.write("server",message.server,"; tdiff",tdiff,"; mdate",mdate)
                err_code = await error(message.author, message.channel, reason['bdtme'], cmd['name'], msg=command[2])
                return err_code

            #wait_time = con['TIME.WAIT.ANCHOR'] if rx['boss.status.anchor'].match(command[1]) else con['TIME.WAIT.4H']
            wait_time = con['TIME.WAIT.4H'] + con['TIME.OFFSET.PACIFIC']
            bhour = bhour + (int(wait_time.seconds) / 3600) # bhour in Pacific/local
            if message_args['name'] in bos02s and rx['boss.status.anchor'].match(command[1]): # you cannot anchor events
                err_code = await error(message.author, message.channel, reason['noanc'], cmd['name'])
            elif message_args['name'] in bos02s or rx['boss.status.warning'].match(command[1]):
                if bhour < 2:
                    bhour += 22
                    btday -= 1
                else:
                    bhour -= 2
            elif message_args['name'] in bos16s:
                bhour += 12 # 12 + 4 = 16
                
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
                err_code = await error(message.author, message.channel, reason['baddb'], cmd['name'])
                await func_discord_db(command_server, create_discord_db) # (re)create db
                return err_code

            status = await func_discord_db(command_server, update_boss_db, message_args)
            if not status: # update_boss_db failed
                err_code = await error(message.author, message.channel, reason['unkwn'], cmd['name'])
                return err_code

            await client.send_message(message.channel, message.author.mention + cmd_usage['boss.acknowledged'] + \
                                      message_args['name'] + " " + message_args['status'] + " at " + \
                                      ("0" if oribhour < 10 else "") + \
                                      str(oribhour) + ":" + \
                                      ("0" if message_args['mins'] < 10 else "") + \
                                      str(message_args['mins']) + ", CH" + str(message_args['channel']) + ": " + \
                                      (message_args['map'] if message_args['map'] != "N/A" else ""))

            #await client.process_commands(message)
            return True # command processed
                
    else:
        #await client.process_commands(message)
        return False

# @func:    check_databases()
async def check_databases():
    await client.wait_until_ready()
    results = dict()
    while not client.is_closed:
        await asyncio.sleep(60)
        valid_dbs = []
        try:
            f = open(con['FILES.VALIDDB'],'r')
        except:
            open(con['FILES.VALIDDB'],'a').close()
            f = open(con['FILES.VALIDDB'],'r')
        try:
            g = open(con['FILES.NOREPEAT'],'r')
        except:
            open(con['FILES.NOREPEAT'],'a').close()
            g = open(con['FILES.NOREPEAT'],'r')
        for line in f:
            valid_dbs.append(line.strip())
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
                tupletime = [int(t) for t in result[5:10]]
                try:
                    rtime = datetime(*tupletime)
                except:
                    #TODO: remove entry
                    continue
                rtime_east = rtime + con['TIME.OFFSET.EASTERN']
                tdiff = rtime-datetime.now()
                # if tdiff < 0: # stale data; delete
                #     await func_discord_db(valid_db, rm_ent_boss_db, bd=result)
                # elif tdiff.seconds < 10800 and rx['boss.status.anchor'].match(result[3]):
                #     message_send.append(format_message_boss(result[0], result[3], rtime_east, result[1]))
                #elif
                if tdiff.days < 0:
                    continue
                if tdiff.seconds < 900 and tdiff.days == 0:
                    msgb = []
                    no_repeat = []
                    msgb.append(format_message_boss(result[0], result[3], rtime_east, result[2], result[1]))
                    msgb.append(str(result[4]),)
                    strm = str(result[4]) + ":" + str(result[0]) + ":" + str(result[3]) + ":" + \
                           str(rtime_east) + ":" + str(result[1]) + "\n"
                    for line_g in g:
                        no_repeat.append(line_g.rstrip())
                    if strm.rstrip() in no_repeat:
                        continue
                    else:
                        with open(con['FILES.NOREPEAT'], 'a') as h:
                            h.write(strm)
                        message_send.append(msgb)
                # elif tdiff.seconds > 72000:
                #     await func_discord_db(valid_db, rm_ent_boss_db, result)
            # message: str, str
            if len(message_send) == 0:
                continue
            messtr = str()
            srv = client.get_server(rx['str.ext.db'].sub('', valid_db))
            cur_channel = ''
            for message in message_send:
                if cur_channel != message[-1] and not rx['format.letters'].match(message[-1]):
                    if cur_channel:
                        messtr += "```"
                        await client.send_message(srv.get_channel(cur_channel), messtr)
                    cur_channel = message[-1]
                    #TODO: Replace 15 with custom server time threshold
                    messtr = "@here The following bosses will spawn within " + "15" + " minutes: ```python\n"
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
    elif bossmap == 'N/A':
        bossmap = ['[Map Unknown]',]
    elif boss == "Blasphemous Deathweaver" and re.search("[Aa]shaq", bossmap):
        bossmap = [m for m in bosslo[boss][2:-1] if m != bossmap]
    elif boss == "Blasphemous Deathweaver":
        bossmap = [m for m in bosslo[boss][0:2] if m != bossmap]
    else:
        bossmap = [m for m in bosslo[boss] if m != bossmap]

    if rx['boss.status.anchor'].search(status):
        report_time = time+timedelta(hours=-3)
        status_str = "was anchored"
    elif rx['boss.status.warning'].search(status):
        report_time = time+timedelta(hours=-2)
        status_str = "was warned to spawn"
    else:
        if boss in bos02s:
            report_time = time+timedelta(hours=-2)
        elif boss in bos16s:
            report_time = time+timedelta(hours=-16)
            print(report_time)
        else:
            report_time = time+timedelta(hours=-4)
        status_str = "died"

    status_str  = " " + status_str + " at "
    # if boss not in bos16s and boss not in bos02s:
    #     time_exp    = con['TIME.WAIT.4H']
    # elif boss in bos16s:
    #     time_exp    = con['TIME.WAIT.16H']
    # elif boss in bos02s:
    #     time_exp    = con['TIME.WAIT.2H']
    expect_str  = (("between " + (time-timedelta(hours=1)).strftime("%Y/%m/%d %H:%M") + " and ") \
                   if rx['boss.status.anchor'].match(status) else "at ") + \
                  (time).strftime("%Y/%m/%d %H:%M") + \
                  " (in " + str(int((time-datetime.now()+con['TIME.OFFSET.PACIFIC']).seconds/60)) + " minutes)"

    if "[Map Unknown]" in bossmap:
        map_str     = '.'
    else:
        map_str     = ", in the following maps: # " + '. '.join(bossmap[0:])
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
    if boss == "Blasphemous Deathweaver" and not rx['boss.dw.ambi'].search(maps):
        return -1


    if rx['boss.floors.format'].search(maps):
        # rearrange letters, and remove map name
        if boss == "Wrathful Harpeia":
            mapnum = rx['boss.floors.format'].sub(r'\g<floornumber>', maps)
            maps = "Demon Prison District " + mapnum
        else:
            mapnum = rx['boss.floors.format'].sub(r'\g<district>\g<basement>\g<floornumber>\g<floor>', maps)
            mapnum = str(mapnum).upper()

        if boss == "Blasphemous Deathweaver" and rx['boss.dw.loc.cm'].search(maps):
            mapnum = rx['boss.dw.loc.cm'].sub('', mapnum) # erase name and redo
            maps = "Crystal Mine " + mapnum
        elif boss == "Blasphemous Deathweaver":
            mapnum = rx['boss.dw.loc.ashaq'].sub('', mapnum) # erase name and redo
            maps = "Ashaq Underground Prison " + mapnum

        # elif boss == "Wrathful Harpeia":
        #     if rx['boss.hp.loc.dp'].search(maps):
        #         mapnum = rx['boss.hp.loc.dp'].sub('', mapnum) # erase name and redo
        #     if rx['boss.floors'].search(maps):
        #         mapnum = rx['boss.floors'].sub('', mapnum) # erase d or f; doesn't matter!
        #     if rx['boss.hp.loc.dp.dist'].search(maps):
        #         mapnum = rx['boss.hp.loc.dp.dist.n'].sub('', mapnum) # erase district, keep number, and redo
        #     maps = "Demon Prison District " + mapnum
    # elif rx['format.numbers'].search(maps) and boss != "Bleak Chapparition":
    #     mapname = rx['format.numbers'].sub('', bosslo[boss][0])
    #     maps = mapname + maps

    for m in bosslo[boss]:
        if m.lower() in maps.lower():
            return bosslo[boss].index(m)
        if maps.lower() in m.lower():
            return bosslo[boss].index(m)
    return -1

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
    if ecmd == cmd['name']:
        # broad
        if etype == reason['broad']:
            ret_msg.append(user_name + the_following_argument('name') + msg + \
                           ") for `$boss` has multiple matching spawn points:\n")
            ret_msg.append(cmd_usage['code_block'])
            ret_msg.append('\n'.join(bosslo[msg]))
            ret_msg.append(cmd_usage['code_block'])
            ret_msg.append(cmd_usage['error.ambiguous'])
            ret_msg.append(cmd_usage['boss.map'])
            ecode = con['ERROR.BROAD']
        elif etype == reason['unkwn']:
            ret_msg.append(user_name + " I'm sorry. Your command failed for unknown reasons.\n" + \
                           "This command failure has been recorded.\n" + \
                           "Please try again shortly.\n")
            with open('wings_of_vaivora-error.txt', 'a') as f:
                f.write(str(datetime.today()) + " An error was detected when " + user_name + " sent a command.")
            ecode = con['ERROR.WRONG']
        # unknown boss
        elif etype == reason['unknb']:
            ret_msg.append(user_name + the_following_argument('name') + msg + \
                           ") is invalid for `$boss`. This is a list of bosses you may use:\n")
            ret_msg.append(cmd_usage['code_block'])
            ret_msg.append('\n'.join(bosses))
            ret_msg.append(cmd_usage['code_block'])
            ret_msg.append(cmd_usage['boss.name'])
            ecode = con['ERROR.WRONG']
        elif etype == reason['noanc']:
            ret_msg.append(user_name + the_following_argument('status') + msg + \
                           ") is invalid for `$boss`. You may not select `anchored` for its status.\n")
            ecode = con['ERROR.WRONG']
        elif etype == reason['bdmap']:
            try_msg = list()
            try_msg.append(user_name + the_following_argument('map') + msg + \
                           ") (number) is invalid for `$boss`. This is a list of maps you may use:\n")
            try: # make sure the data is valid by `try`ing
              try_msg.append(cmd_usage['code_block'])
              try_msg.append('\n'.join(bosslo[xmsg]))
              try_msg.append(cmd_usage['code_block'])
              try_msg.append(cmd_usage['boss.map'])
              # seems to have succeeded, so extend to original
              ret_msg.extend(try_msg)
              ecode = con['ERROR.WRONG']
            except: # boss not found! 
              ret_msg.append(user_name + cmd_usage['debug'])
              ret_msg.append(cmd_usage['error.badsyntax'])
              ecode = con['ERROR.SYNTAX']
              with open(con['DEBUG.FILE'], 'a') as f:
                  f.write('boss not found\n')
        elif etype == reason['fdbos']:
            ret_msg.append(user_name + the_following_argument('channel') + msg + \
                           ") (number) is invalid for `$boss`. " + xmsg + " is a field boss, thus " + \
                           "variants that spawn on channels other than 1 (or other maps) are considered world bosses " + \
                           "with unpredictable spawns.\n")
            ecode = con['ERROR.WRONG']
        elif etype == reason['bdtme']:
            ret_msg.append(user_name + the_following_argument('time') + msg + \
                           ") is invalid for `$boss`.\n")
            ret_msg.append("Omit spaces; record in 12H (with AM/PM) or 24H time.\n")
            ret_msg.append(cmd_usage['error.badsyntax'])
            ecode = con['ERROR.WRONG']
        elif etype == reason['noanc']:
            ret_msg.append(user_name + the_following_argument('status') + 'anchored' + \
                           ") is invalid for `$boss`.\n" +
                           "You cannot anchor events or bosses of this kind.\n")
            ecode = con['ERROR.WRONG']
        elif etype == reason['argct']:
            ret_msg.append(user_name + " Your command for `$boss` had too few arguments.\n" + \
                           "Expected: 4 to 6; got: " + msg + ".\n")
            ret_msg.append(cmd_usage['error.badsyntax'])
            ecode = con['ERROR.SYNTAX']
        elif etype == reason['quote']:
            ret_msg.append(user_name + " Your command for `$boss` had misused quotes somewhere.\n")
            ret_msg.append(cmd_usage['error.badsyntax'])
            ecode = con['ERROR.SYNTAX']
        elif etype == reason['syntx']:
            ret_msg.append(user_name + " Your command could not be parsed. Re-check the syntax, and try again.\n" + \
                           ("Message: " + msg) if msg else "")
            ret_msg.append(cmd_usage['error.badsyntax'])
            ecode = con['ERROR.SYNTAX']
        else:
            ret_msg.append(user_name + cmd_usage['debug'] + "\n" + etype)
            ret_msg.append(cmd_usage['error.badsyntax'])
            ecode = con['ERROR.SYNTAX']
            await client.send_message(channel, '\n'.join(ret_msg))
            return ecode
        # end of conditionals for cmd['name']

        # begin common return for $boss
        ret_msg.append("For syntax: $boss help")
        await client.send_message(channel, '\n'.join(ret_msg))
        return ecode
        # end of common return for $boss

    # todo: reminders, Talt tracking, permissions
    else:
        # todo
        ret_msg.append(user_name + cmd_usage['debug'])
        ret_msg.append(cmd_usage['error.badsyntax'])
        ecode = con['ERROR.SYNTAX']
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