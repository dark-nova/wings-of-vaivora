#!/usr/bin/env python
import discord
from discord.ext import commands
import logging
import sqlite3
import asyncio
import random
import shlex
#from queue import Queue as q
from hashlib import blake2b
from itertools import chain
import json
import re
import os
from datetime import datetime, timedelta
from operator import itemgetter

# import additional constants
from importlib import import_module as im
import vaivora_modules
for mod in vaivora_modules.modules:
    im(mod)
from constants.boss import en_us as lang_boss


# basic declarations and initializations
#client              =   discord.Client()
bot = commands.Bot(command_prefix=['$','Vaivora, ','vaivora ','vaivora, '])
bot.remove_command('help')

# vdbs & vdst will now use int for dict keys; previously str of int
vdbs = dict()
vdst = dict()


### BGN CONST

#### File related constants

wings       = "wings-"
txt         = ".txt"
log         = ".log"
tmp         = ".tmp"

logger      = wings + "logger"

valid_db    = wings + "valid_db"    + txt
valid_db_t  = wings + "valid_db"    + tmp
records_t = wings + "records"
records   = records_t           + txt
welcomed    = wings + "welcomed"    + txt
welcomed_t  = wings + "welcomed"    + tmp
f_unsubbed  = wings + "unsubbed"    + txt
f_subbed    = wings + "subbed"      + txt

log_file    = logger                + log
debug_file  = wings + "debug"       + log

####

first_run           =   0

cmd_boss = "boss"
cmd_settings = "settings"

msg_sub             =   "Your subscription preference for changelogs has been updated:"

omae_wa_mou         =   "You are already " # dead

none_matched        =   "```\n*crickets chirping*\n```\n"

### BGN REGEX

rgx_help            =   re.compile(r'help', re.IGNORECASE)
rgx_prefix          =   re.compile(r'^(va?i[bv]ora ,?|\$)', re.IGNORECASE)
# this screws up with boss role if I remove the prefix #### to investigate
rgx_boss            =   re.compile(r'^(va?i[bv]ora ,?|\$)boss .+', re.IGNORECASE)
rgx_settings        =   re.compile(r'settings .+', re.IGNORECASE)
rgx_meme            =   re.compile(r'pl(ea)?[sz]e?', re.IGNORECASE)
rgx_ch_hash         =   re.compile(r'#')
rgx_ch_member       =   re.compile(r'@')
rgx_talt            =   re.compile(r'talt', re.IGNORECASE)
rgx_ini             =   re.compile(r'^```\n?ini\n?(```)?$', re.IGNORECASE) # match hidden blocks
rgx_py              =   re.compile(r'^```\n?python\n?(```)?$', re.IGNORECASE) # match hidden blocks again

to_sanitize         =   re.compile(r"""[^a-z0-9 .:$"',-]""", re.IGNORECASE)

### END REGEX

msg_help            =   """
Here are commands. Valid prefixes are `$` (dollar sign) and `Vaivora,<space>`,
e.g. `$boss` or `Vaivora, help`

```
"Changelogs" commands
    $unsubscribe
    $subscribe

* These functions are currently disabled.
```
```
"Boss" commands
    $boss [args ...]
    $boss help

* Use "$boss help" for more information.

Examples:
    $boss all list
    $boss mineloader died 13:00 forest
    $boss ml died 1:00p "forest of prayer"

* More examples in "$boss help"
```
```
"Settings" commands
    $settings [args ...]
    $settings help

* Use "$settings help" for more information.

Examples
    $settings set role auth @Leaders
    $settings set role member @Members
```
```
General
    $help: prints this page in Direct Message
```
"""

welcome     =   """
Thank you for inviting me to your server!
I am a representative bot for the Wings of Vaivora, here to help you record your journey.
Please read the following before continuing.
""" + vaivora_modules.disclaimer.disclaimer + """
Anyone may add this bot using the short URL: https://dark-nova.me/wings-of-vaivora
Anyone may contribute to this bot's development: https://github.com/dark-nova/wings-of-vaivora
"""

### END CONST


def splitDblQuotesSpaces(command):
    lex = shlex.shlex(command)
    lex.quotes = '"'
    lex.commenters = ""
    lex.whitespace_split = True
    return list(lex)



@bot.event
async def on_ready():
    """
    :func:`on_ready` handles file prep before the bot is ready.

    Returns:
        None
    """
    global first_run
    print("Logging in...")
    print('Successsfully logged in as: {}#{}. Ready!'.format(bot.user.name, bot.user.id))
    await bot.change_presence(activity=discord.Game(name="with startup. Please wait a moment..."),
                              status=discord.Status.idle)
    first_run += len(bot.guilds)
    await bot.change_presence(activity=discord.Game(name=("with files. Processing {} guilds...".format(str(first_run)))),
                              status=discord.Status.dnd)
    for guild in bot.guilds:
        if not guild.unavailable:
            guild_id = str(guild.id)
            guild_owner_id = str(guild.owner.id)
            vdbs[guild.id] = vaivora_modules.db.Database(guild_id)
            vdst[guild.id] = vaivora_modules.settings.Settings(guild_id, guild_owner_id)
            await greet(guild.id, guild.owner)
        first_run -= 1
    await asyncio.sleep(1)
    first_run = 0
    await bot.change_presence(activity=discord.Game(name=("in {} guilds # [$help] or [Vaivora, help] for info".format(str(len(bot.guilds))))),
                              status=discord.Status.online)
    return


@bot.event
async def greet(guild_id, guild_owner):
    """
    :func:`greet` sends welcome messages to new participants of Wings of Vaivora.

    Args:
        guild_id (int): the Discord guild's id
        guild_owner (discord.Member): the owner of the aforementioned server

    Returns:
        True if successful; False otherwise
    """

    try:
        do_not_msg = await get_unsubscribed()
    except:
        # can't get unsubscribed? avoid sending messages entirely
        return False

    if guild_owner.id in do_not_msg:
        return True

    iters = 0
    nrevs = vdst[guild_id].greet(vaivora_modules.version.get_current_version())
    if nrevs == 0:
        return True

    for vaivora_log in vaivora_modules.version.get_changelogs(nrevs):
        iters += 1
        print('{}.{}_{}: receiving {} logs of {}'.format(guild_id, str(guild_owner), guild_owner.id,
                                                         str(iters), str(nrevs*-1)))
        try:
            await guild_owner.send(vaivora_log)
        except: # cannot send messages, ignore
            ### TODO: handle deletion/kick from server(?)
            return False

    return True


@bot.event
async def on_guild_join(guild):
    """
    :func:`on_guild_join` handles what to do when a guild adds Wings of Vaivora.

    Args:
        guild (discord.Guild): the guild which this client has joined

    Returns:
        True if successful; False otherwise
    """
    vaivora_version = vaivora_modules.version.get_current_version()
    if guild.unavailable:
        return False
    vdbs[guild.id] = vaivora_modules.db.Database(str(guild.id))
    owner = guild.owner
    vdst[guild.id] = vaivora_modules.settings.Settings(str(guild.id), str(owner.id))
    await greet(guild.id, owner)
    await owner.send(owner, welcome)
    return True


@bot.command(aliases=['halp'])
async def help(ctx):
    """
    :func:`help` handles "$help" commands.

    Args:
        ctx (discord.ext.commands.context): context of the message

    Returns:
        True if successful; False otherwise
    """
    try:
        await ctx.author.send(msg_help)
    except:
        return False

    return True


@bot.command()
async def boss(ctx, *args):
    """
    :func:`boss` handles "$boss" commands.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        *args (tuple): arguments to be supplied for the command

    Returns:
        True if successful; False otherwise
    """
    args = await sanitize(args)

    if rgx_help.match(args[0]):
        boss_help = vaivora_modules.boss.help()
        for bh in boss_help:
            await ctx.author.send(bh)
            return True

    if not await check_channel(ctx.guild.id, ctx.message.channel.id, cmd_boss):
        return False

    arg_target = args[0]

    if vaivora_modules.boss.what_status(args[1]):
        arg_subcmd = lang_boss.CMD_ARG_STATUS
    elif vaivora_modules.boss.what_query(args[1]):
        arg_subcmd = lang_boss.CMD_ARG_QUERY
    elif vaivora_modules.boss.what_type(args[1]):
        arg_subcmd = lang_boss.CMD_ARG_TYPE
    else:
        await ctx.send('{} {} is invalid for {}.'.format(ctx.author.mention, args[1],
                                                         lang_boss.CMD_ARG_SUBCMD))
        return False

    if arg_target == "all":
        if arg_subcmd == lang_boss.CMD_ARG_STATUS or arg_subcmd == lang_boss.CMD_ARG_QUERY:
            await ctx.send('{} {} is invalid for {} {}.'.format(ctx.author.mention, args[1],
                                                                lang_boss.CMD_ARG_TARGET, arg_target))
            return False
        else: # same as `elif arg_subcmd == lang_boss.CMD_ARG_TYPE:`
            boss_type = vaivora_modules.boss.what_type(args[1])
            await ctx.send('{} {}'.format(ctx.author.mention,
                                          vaivora_modules.boss.get_bosses(boss_type)))

    else:
        boss_idx = vaivora_modules.boss.check_boss(arg_target)
        if boss_idx == -1:
            await ctx.send('{} {} is invalid for {}.'.format(ctx.author.mention, arg_target, 
                                                             lang_boss.CMD_ARG_TARGET))
            return False

        if arg_subcmd == lang_boss.CMD_ARG_STATUS:
            if len(args) < lang_boss.ARG_MIN_STATUS or len(args) > lang_boss.ARG_MAX_STATUS:
                await ctx.send('{} Usage: {}'.format(ctx.author.mention,
                                                     lang_boss.CMD_USAGE_STATUS))
                return False


    return True


@bot.command()
async def settings(ctx, *args):
    """
    :func:`settings` handles "$settings" commands.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        *args (tuple): arguments to be supplied for the command

    Returns:
        True if successful; False otherwise
    """
    args = await sanitize(args)

    if rgx_help.match(args[0]):
        pass

    if not await check_channel(ctx.guild.id, ctx.message.channel.id, "management"):
        return False

    pass


@bot.command(aliases=['pls', 'plz', 'ples'])
async def please(ctx):
    """
    :func:`please` is a meme

    Args:
        ctx (discord.ext.commands.Context): context of the message

    Returns:
        True if successful; False otherwise
    """
    try:
        await ctx.send('{} https://i.imgur.com/kW3o6eC.png'.format(ctx.author.mention))
    except:
        return False

    return True


@bot.event
async def check_channel(guild_id, ch_id: str, ch_type):
    """
    :func:`check_channel` checks whether a channel is allowed to interact with Wings of Vaivora.

    Args:
        guild_id (int): the id of the guild involved
        ch_id (str, int): the id of the channel to check (i.e. "boss":boss, "management":settings)
        ch_type (str): the type (name) of the channel

    Returns:
        True if successful; False otherwise
    """

    chs = vdst[guild_id].get_channel(ch_type)

    if chs and ch_id not in chs:
        return False
    else: # in the case of `None` chs, all channels are valid
        return True


async def sanitize(args: list):
    """
    :func:`sanitize` sanitizes command arguments of invalid characters, including setting to lowercase.

    Args:
        args (list): the arguments to sanitize

    Returns:
        a list containing the sanitized arguments
    """
    sanitized = []
    for arg in args:
        arg = to_sanitize.sub('', arg).lower()
        sanitized.append(arg)

    return sanitized


async def check_subscription(user, mode="subscribe"):
    """
    :func:`check_subscription` checks if the user is subscribed.
    This function may be moved to :mod:`vaivora_modules.changelogs` in the future.

    Args:
        user (discord.User): the user who requested his/her subscription status
        mode (str): (default: )

    Returns:
        list: A list containing the users who have unsubscribed.
    """
    file_unsub  = []
    file_sub    = []
    status      = True
    vaivora_version   = vaivora_modules.version.get_current_version()
    try:
        status_hit  = False
        with open(f_unsubbed, 'r') as unsubbed:
            for line in unsubbed:
                if vaivora_modules.changelogs.empty_line.match(line):
                    continue
                if user.id in line and mode == "subscribe":
                    status_hit  = True
                    continue
                elif user.id in line and mode == "unsubscribe":
                    status = False
                    status_hit  = True
                file_unsub.append(line)
        if not status_hit and mode == "unsubscribe":
            file_unsub.append(user.id)
        with open(f_unsubbed, 'w+') as unsubbed:
            if len(file_unsub) == 0:
                pass
            elif len(file_unsub) > 1:
                unsubbed.write('\n'.join(file_unsub[:-1]))
            if len(file_unsub) >= 1:
                unsubbed.write(file_unsub[-1] + "\n")
    except:
        with open(f_unsubbed, 'w+') as f:
            if mode == "unsubscribe":
                f.write(user.id + "\n")
    try:
        status_hit  = False
        with open(f_subbed, 'r') as subbed:
            for line in subbed:
                if vaivora_modules.changelogs.empty_line.match(line):
                    continue
                if user.id in line and mode == "subscribe":
                    status = False
                    status_hit  = True
                elif user.id in line and mode == "unsubscribe":
                    status_hit  = True
                    continue
                file_sub.append(line)
        if not status_hit and mode == "subscribe":
            file_sub.append(user.id)
        with open(f_subbed, 'w+') as subbed:
            if vaivora_modules.changelogs.empty_line.match(line):
                pass
            elif len(file_sub) > 1:
                subbed.write((':' + vaivora_version + '\n').join(file_sub[:-1]))
            if len(file_sub) >= 1:
                subbed.write(file_sub[-1] + ":" + vaivora_version + "\n")
    except:
        with open(f_subbed, 'w+') as f:
            if mode == "subscribe":
                f.write(user.id + ":" + vaivora_version + "\n")
    return status


async def get_unsubscribed():
    """
    :func:`get_unsubscribed` retrieves the list of unsubscribed users.
    This function may be moved to :mod:`vaivora_modules.changelogs` in the future.

    Args:
        None

    Returns:
        list: A list containing the users who have unsubscribed.
    """
    unsubbed    = []
    try:
        with open(f_unsubbed, 'r') as f:
            for line in f:
                unsubbed.append(line.rstrip('\n'))
        return unsubbed
    except:
        return []



async def check_databases():
    """
    :func:`check_databases` checks the database for entries roughly every minute.
    Records are output to the relevant Discord channels.
    """
    while first_run:
        await asyncio.sleep(1)
    print('Startup completed; starting check_database')
    results = {}
    minutes = {}
    records = []
    today = datetime.today() # check on first launch

    while not bot.is_closed():
        await asyncio.sleep(59)
        print(datetime.today().strftime("%Y/%m/%d %H:%M"), "- Valid DBs:", len(vdbs))

        # prune records once they're no longer alert-able
        purged = []
        if len(minutes) > 0:
            for rec_hash, rec_mins in minutes.items():
                mins_now = datetime.now().minute
                # e.g. 48 > 03 (if record was 1:03 and time now is 12:48), passes conds 1 & 2 but fails cond 3
                if (rec_mins < mins_now) and ((mins_now-rec_mins) > 0) and ((mins_now-rec_mins+15+1) < 60):
                    records.remove(rec_hash)
                    purged.append(rec_hash)

        for purge in purged:
            try:
                del minutes[purge]
            except:
                continue

        # iterate through database results
        for vdb_id, valid_db in vdbs.items():
            loop_time = datetime.today()
            print(loop_time.strftime("%H:%M"), "- in DB:", vdb_id)
            results[vdb_id] = []
            if today.day != loop_time.day:
                today = loop_time

            # check all timers
            message_to_send = []
            cur_channel = None
            results[vdb_id] = valid_db.check_db_boss()

            # empty record; dismiss
            if not results[vdb_id]:
                continue

            # sort by time - yyyy, mm, dd, hh, mm
            results[vdb_id].sort(key=itemgetter(5,6,7,8,9))

            # iterate through all results
            for result in results[vdb_id]:
                cur_channel = result[4]
                list_time = [ int(t) for t in result[5:10] ]
                record_info = [ str(r) for r in result[0:5] ]

                entry_time = datetime(*list_time)

                record = vaivora_modules.boss.process_record(record_info[0], record_info[3], entry_time, record_info[2], record_info[1])
                #                   channel           :    boss              :                       2017/01/01 12:00      :    channel
                record2byte = record_info[4] + ":" + record_info[0] + ":" + entry_time.strftime("%Y/%m/%d %H:%M") + ":" + record_info[1]
                record2byte = bytearray(record2byte, 'utf-8')
                hashedblake = blake2b(digest_size=48)
                hashedblake.update(record2byte)
                hashed_record = hashedblake.hexdigest()

                # don't add a record that is already stored
                if hashed_record in records:
                    continue

                # process time difference
                time_diff = entry_time - datetime.now() + timedelta(hours=-3)

                # record is in the past
                if time_diff.days < 0:
                    continue

                # record is within range of alert
                if time_diff.seconds < 900 and time_diff.days == 0:
                    records.append(hashed_record)
                    message_to_send.append([record, record_info[4],])
                    minutes[str(hashed_record)] = entry_time.minute

            # empty record for this server
            if len(message_to_send) == 0:
                continue

            role_str = str()

            # compare roles against server
            srv = bot.get_guild(vdb_id)
            for uid in vdst[vdb_id].get_role(cmd_boss):
                try:
                    # group mention
                    idx =   [ro.id for ro in srv.roles].index(uid)
                    role_str    +=  srv.roles[idx].mention + " "
                except:
                    if rgx_ch_member.search(uid):
                        uid =   rgx_ch_member.sub('', uid)

                    try:
                        # user mention
                        boss_user   =   srv.get_member(uid)
                        role_str    +=  boss_user.mention + " "
                    except:
                        # user or group no longer exists
                        vdst[vdb_id].rm_boss(uid)

            # no roles detected; use empty string
            role_str = role_str if role_str else ""

            # replace time_str with server setting warning, eventually
            time_str = "15"

            cur_channel = None
            discord_message = ''
            for message in message_to_send:
                if cur_channel != message[-1]:
                    if cur_channel:
                        discord_message += "```"

                        try:
                            await srv.get_channel(cur_channel).send(discord_message)
                        except:
                            pass

                        discord_message = ''
                    cur_channel = message[-1]

                    # replace time_str with server setting warning, eventually
                    discord_message = role_str + "The following bosses will spawn within " + time_str + " minutes: ```python\n"
                discord_message += message[0]
            # flush
            discord_message += "```"

            try:
                await srv.get_channel(cur_channel).send(discord_message)
            except:
                pass

            discord_message = ''
        #await client.process_commands(message)
        await asyncio.sleep(1)
####
# end of periodic database check


# begin everything
secret = vaivora_modules.secrets.discord_token

bot.loop.create_task(check_databases())
bot.run(secret)