#!/usr/bin/env python
import discord
from discord.ext import commands
import logging
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
from constants.errors import en_us as lang_err
from constants.settings import en_us as lang_settings
from constants.boss import en_us as lang_boss
from constants.db import en_us as lang_db
from constants.main import en_us as lang


# basic declarations and initializations
#client              =   discord.Client()
bot = commands.Bot(command_prefix=['$','Vaivora, ','vaivora ','vaivora, '])
bot.remove_command('help')

# vdbs & vdst will now use int for dict keys; previously str of int
vdbs = {}
vdst = {}


### BGN CONST ###


### BGN REGEX ###

rgx_help = re.compile(r'help', re.IGNORECASE)
rgx_user = re.compile(r'@')
to_sanitize = re.compile(r"""[^a-z0-9 .:$"',-]""", re.IGNORECASE)

### END REGEX



welcome = """
Thank you for inviting me to your server!
I am a representative bot for the Wings of Vaivora, here to help you record your journey.
Please read the following before continuing.
""" + vaivora_modules.disclaimer.disclaimer + """
Anyone may contribute to this bot's development: https://github.com/dark-nova/wings-of-vaivora
"""

### END CONST

bosses = []

@bot.event
async def on_ready():
    """
    :func:`on_ready` handles file prep before the bot is ready.

    Returns:
        True
    """
    print("Logging in...")
    print('Successsfully logged in as: {}#{}. Ready!'.format(bot.user.name, bot.user.id))
    await bot.change_presence(status=discord.Status.dnd)
    await bot.change_presence(activity=discord.Game(name=("in {} guilds. [$help] for info"
                                                          .format(str(len(bot.guilds))))),
                              status=discord.Status.online)
    return True


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
    #vaivora_version = vaivora_modules.version.get_current_version()

    if guild.unavailable:
        return False

    vdbs[guild.id] = vaivora_modules.db.Database(str(guild.id))
    owner = guild.owner
    vdst[guild.id] = vaivora_modules.settings.Settings(str(guild.id), str(owner.id))

    #await greet(guild.id, owner)
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
        await ctx.author.send(lang.MSG_HELP)
    except:
        return False

    return True


@bot.group()
async def boss(ctx, arg: str):
    """
    :func:`boss` handles "$boss" commands.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        arg (str): the boss to check

    Returns:
        True if successful; False otherwise
    """
    arg = await sanitize(arg)

    if rgx_help.match(arg):
        _help = vaivora_modules.boss.help()
        for _h in _help:
            await ctx.author.send(_h)
        return True

    ctx.boss = arg

    return True


# $boss <boss> <status> <time> [channel]
@boss.command(name='died', aliases=['die', 'dead', 'anch', 'anchor', 'anchored'])
async def status(ctx, time: str, map_or_channel = None):
    """
    :func:`status` is a subcommand for `boss`.
    Essentially stores valid data into a database.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        time (str): time when the boss died
        map_or_channel: (default: None) the map xor channel in which the boss died

    Returns:
        True if run successfully, regardless of result
    """
    if ctx.guild == None: # not a guild
        await ctx.send(lang_err.CANT_DM.format(lang_boss.COMMAND))
        return False

    subcmd = await vaivora_modules.boss.what_status(ctx.subcommand_passed)


    if ctx.boss == lang_boss.CMD_ARG_TARGET_ALL:
       await ctx.send(lang_err.IS_INVALID_3
                      .format(ctx.author.mention, ctx.boss,
                              lang_boss.CMD_ARG_TARGET, subcmd))
       return False

    try:
        _boss, _time, _map, _channel = await boss_helper(ctx.boss, time, map_or_channel)
    except:
        which_fail = await boss_helper(ctx.boss, time, map_or_channel)
        if len(which_fail) == 1:
            await ctx.send(lang_err.IS_INVALID_2
                           .format(ctx.author.mention, ctx.boss,
                                   lang_boss.CMD_ARG_TARGET))
        elif len(which_fail) == 2:
            await ctx.send(lang_err.IS_INVALID_3
                           .format(ctx.author.mention, time,
                                   ctx.subcommand_passed, 'time'))
        else:
            pass
        return False

    opt = {lang_db.COL_BOSS_CHANNEL: _channel, lang_db.COL_BOSS_MAP: _map}
    msg = await (vaivora_modules.boss
                 .process_cmd_status(ctx.guild.id, ctx.channel.id,
                                     _boss, subcmd, _time, opt))
    await ctx.send('{} {}'.format(ctx.author.mention, msg))

    return True


@boss.command(name='list', aliases=['ls', 'erase', 'del', 'delete', 'rm'])
async def entry(ctx, channel=None):
    """
    :func:`_list` is a subcommand for `boss`.
    Lists records for bosses given.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        channel: (default: None) the channel to show, if supplied

    Returns:
        True if run successfully, regardless of result 
    """
    if ctx.guild == None: # not a guild
        await ctx.send(lang_err.CANT_DM.format(lang_boss.COMMAND))
        return False

    if ctx.boss != lang_boss.CMD_ARG_TARGET_ALL:
        boss_idx = await vaivora_modules.boss.check_boss(ctx.boss)
        if boss_idx == -1:
            await ctx.send(lang_err.IS_INVALID_2
                           .format(ctx.author.mention, ctx.boss,
                                   lang_boss.CMD_ARG_TARGET))
            return False
        boss = lang_boss.ALL_BOSSES[boss_idx]
    else:
        boss = lang_boss.ALL_BOSSES

    if channel is not None:
        channel = lang_boss.REGEX_OPT_CHANNEL.match(channel)
        channel = int(channel.group(2))

    subcmd = await vaivora_modules.boss.what_entry(ctx.subcommand_passed)

    msg = await (vaivora_modules.boss
                 .process_cmd_entry(ctx.guild.id, ctx.channel.id,
                                    boss, subcmd, channel))

    await ctx.send('{}\n\n{}'.format(ctx.author.mention, msg[0]))
    combined_message = ''
    for _msg, i in zip(msg[1:], range(len(msg)-1)):
        combined_message = '{}\n\n{}'.format(combined_message, _msg)
        if i % 5 == 4:
            await ctx.send(combined_message)
            combined_message = ''
    if combined_message:
        await ctx.send(combined_message)

    return True


@boss.command(name='maps', aliases=['map', 'alias', 'aliases'])
async def query(ctx):
    """
    :func:`query` returns a user-usable list of maps and aliases for a given target.

    Args:
        ctx (discord.ext.commands.Context): context of the message

    Returns:
        True if run successfully, regardless of result
    """
    subcmd = await vaivora_modules.boss.what_query(ctx.subcommand_passed)

    if ctx.boss == lang_boss.CMD_ARG_TARGET_ALL:
       await ctx.send(lang_err.IS_INVALID_3
                      .format(ctx.author.mention, ctx.boss,
                              lang_boss.CMD_ARG_TARGET, subcmd))
       return False
    else:
        boss_idx = await vaivora_modules.boss.check_boss(ctx.boss)
        if boss_idx == -1:
            await ctx.send(lang_err.IS_INVALID_2
                           .format(ctx.author.mention, ctx.boss,
                                   lang_boss.CMD_ARG_TARGET))
            return False
        boss = lang_boss.ALL_BOSSES[boss_idx]

    msg = await vaivora_modules.boss.process_cmd_query(boss, subcmd)

    await ctx.send('{}\n\n{}'.format(ctx.author.mention, msg))


@boss.command(name='world', aliases=['w', 'field', 'f', 'demon', 'd', 'dl'])
async def _type(ctx):
    """
    :func:`_type` returns a user-usable list of types of bosses: World, Field, Demon.

    Args:
        ctx (discord.ext.commands.Context): context of the message

    Returns:
        True if run successfully, regardless of result
    """
    subcmd = await vaivora_modules.boss.what_type(ctx.subcommand_passed)

    if ctx.boss != lang_boss.CMD_ARG_TARGET_ALL:
       await ctx.send(lang_err.IS_INVALID_3
                      .format(ctx.author.mention, ctx.boss,
                              lang_boss.CMD_ARG_TARGET, subcmd))
       return False

    msg = await vaivora_modules.boss.get_bosses(subcmd)

    await ctx.send('{}\n\n{}'.format(ctx.author.mention, msg))


async def boss_helper(boss, time, map_or_channel):
    """
    :func:`boss_helper` processes for `died` and `anchored`.

    Args:
        time (str): time when the boss died
        map_or_channel: (default: None) the map xor channel in which the boss died

    Returns:
        tuple: (boss_idx, channel, map)
    """
    channel = 1 # base case
    map_idx = None # don't assume map

    boss_idx = await vaivora_modules.boss.check_boss(boss)

    if boss_idx == -1: # invalid boss
        return (None,)

    time = await vaivora_modules.boss.validate_time(time)

    if not time: # invalid time
        return (None,None)

    boss = lang_boss.ALL_BOSSES[boss_idx]

    if len(lang_boss.BOSS_MAPS[boss]) == 1:
        map_idx = 0 # it just is

    if map_or_channel and type(map_or_channel) is int:
        if map_or_channel <= 4 or map_or_channel > 1:
            channel = map_or_channel # use user-input channel only if valid
    elif map_or_channel and lang_boss.REGEX_OPT_CHANNEL.match(map_or_channel):
        channel = lang_boss.REGEX_OPT_CHANNEL.match(map_or_channel)
        channel = int(channel.group(2)) # channel will always be 1 through 4 inclusive
    elif type(map_or_channel) is str and map_idx != 0: # possibly map
        map_idx = await vaivora_modules.boss.check_maps(boss_idx, map_or_channel)

    if (not map_idx and map_idx != 0) or map_idx == -1:
        _map = ""
    else:
        _map = lang_boss.BOSS_MAPS[boss][map_idx]

    return (boss, time, _map, channel)


# @bot.command()
# async def settings(ctx, *args):
#     """
#     :func:`settings` handles "$settings" commands.

#     Args:
#         ctx (discord.ext.commands.Context): context of the message
#         *args (tuple): arguments to be supplied for the command

#     Returns:
#         True if successful; False otherwise
#     """
#     args = await sanitize(args)

#     if rgx_help.match(args[0]):
#         _help = vaivora_modules.settings.help()
#         for _h in _help:
#             await ctx.author.send(_h)
#         return True

#     try:
#         # invalid channel
#         if not await check_channel(ctx.guild.id,
#                                    ctx.message.channel.id,
#                                    lang_settings.CHANNEL_MGMT):
#             return False
#     except AttributeError:
#         # not a guild
#         await ctx.send(lang_err.CANT_DM.format(lang_boss.COMMAND))
#         return False

#     if vaivora_modules.settings.what_setting(args[0]):
#         arg_subcmd = lang_settings.CMD_ARG_SETTING
#     elif vaivora_modules.settings.what_validation(args[0]):
#         arg_subcmd = lang_settings.CMD_ARG_VALIDATION
#     elif vaivora_modules.settings.what_rolechange(args[0]):
#         arg_subcmd = lang_settings.CMD_ARG_ROLECHANGE
#     else:
#         await ctx.send(lang_err.IS_INVALID_2.format(ctx.author.mention, args[0],
#                                                     lang_settings.CMD_ARG_SUBCMD))
#         return False

#     if arg_subcmd == lang_settings.CMD_ARG_SETTING:
#         setting = vaivora_modules.settings.what_setting(args[0])
#         target = vaivora_modules.settings.what_setting_target(args[1])
#         if target is None or (target != lang_settings.TARGET_TALT and
#                               setting == lang_settings.SETTING_ADD):
#             await ctx.send(lang_err.IS_INVALID_3.format(ctx.author.mention, args[0],
#                                                         lang_settings.CMD_ARG_SETTING, arg_subcmd))
#             return False



#     pass


# @bot.command(aliases=['pls', 'plz', 'ples'])
# async def please(ctx):
#     """
#     :func:`please` is a meme

#     Args:
#         ctx (discord.ext.commands.Context): context of the message

#     Returns:
#         True if successful; False otherwise
#     """
#     try:
#         await ctx.send('{} https://i.imgur.com/kW3o6eC.png'.format(ctx.author.mention))
#     except:
#         return False

#     return True


# @bot.event
# async def check_channel(guild_id, ch_id: str, ch_type):
#     """
#     :func:`check_channel` checks whether a channel is allowed to interact with Wings of Vaivora.

#     Args:
#         guild_id (int): the id of the guild involved
#         ch_id (str): the id of the channel to check (i.e. "boss":boss, "management":settings)
#         ch_type (str): the type (name) of the channel

#     Returns:
#         True if successful; False otherwise
#         Note that this means if no channels have registered, *all* channels are valid.
#     """

#     chs = vdst[guild_id].get_channel(ch_type)

#     if chs and ch_id not in chs:
#         return False
#     else: # in the case of `None` chs, all channels are valid
#         return True


async def sanitize(arg):
    """
    :func:`sanitize` sanitizes command arguments of invalid characters, including setting to lowercase.

    Args:
        arg (str, iter): the argument (or arguments) to sanitize

    Returns:
        same type as arg, sanitized
    """
    if type(arg) is str:
        return to_sanitize.sub('', arg).lower()
    else:
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



<<<<<<< HEAD
=======
    ch_type     =   "management" if command_type == command_settings else command_boss
    channels    =   vdst[message.server.id].get_channel(ch_type)
    if channels and not message.channel.id in channels:
        return False # silently deny command if not in proper channel

    # remove extraneous punctuation, and lower case
    cmd_message =   to_sanitize.sub('', message.content)
    cmd_message =   cmd_message.lower()

    # attempt quote splitting
    try:
        command =   splitDblQuotesSpaces(cmd_message)
    except ValueError:
        await client.send_message(message.author if not message.server else message.channel, 
                                  "Your command for `$" + command_type + "` had misused quotes somewhere.\n")
        return False

    # silently ignore commands if they have no arguments
    if len(command) == 1:
        return False

    # extract arguments
    command     =   command[1:]

    if not message.server or rgx_help.match(command[0]):
        server_id   =   message.author.id
        msg_ch_id   =   message.author
        msg_channel =   message.author
        msg_prefix  =   ""
    else:
        server_id   =   message.server.id
        msg_ch_id   =   message.channel.id
        msg_channel =   message.channel
        msg_prefix  =   message.author.mention + " "

    if command_type == command_boss:
        return_msg  =   vaivora_modules.boss.process_command(server_id, msg_ch_id, command)
        if not return_msg:
            await client.send_message(msg_channel, msg_prefix + "No records were retrieved.")

        if type(return_msg) is str:
            await client.send_message(msg_channel, msg_prefix + return_msg)
            return True
            
        await client.send_message(msg_channel, msg_prefix + return_msg[0])

        message_to_send =   "```python\n"
        i   =   0

        if len(return_msg) > 1:
            for msg_frag in return_msg[1:]:
                message_to_send +=  msg_frag + "\n"
                i   +=  1

                if i % 5 == 0:
                    message_to_send +=  "```"
                    await client.send_message(msg_channel, message_to_send)
                    message_to_send =   "```python\n"

            try:
                # flush remaining
                if message_to_send and not rgx_py.match(message_to_send):
                    await client.send_message(msg_channel, message_to_send + "```\n")
                elif message_to_send and i < 5:
                    await client.send_message(msg_channel, none_matched)
            except Exception as e:
                # do something with e later
                pass
        return True

    elif command_type == command_settings:

        if rgx_help.match(command[0]):
            return_msg  =   vaivora_modules.settings.get_help()
            if len(return_msg) > 1:
                for msg_frag in return_msg[1:]:
                    await client.send_message(msg_channel, msg_frag)
            return True

        set_cmd     =   command[0]
        mention_u   =   [mention.id for mention in message.mentions]
        mention_g   =   [mention.id for mention in message.role_mentions]
        mention_c   =   [mention.id for mention in message.channel_mentions]
        mention_a   =   mention_u + mention_g + mention_c
        xargs       =   [c for c in command[1:] if c not in mention_a]
        
        
        #def process_command(server_id, msg_channel, settings_cmd, cmd_user, usr_roles, users, groups, xargs=None):
        return_msg  = vdst[server_id].process_command(msg_ch_id, set_cmd,
                                                      message.author.id, message.author.roles,
                                                      mention_u, mention_g, mention_c, xargs=xargs)
        
        # case 1: a list of str, len 1
        if len(return_msg) == 1:
            if return_msg[0]:
                await client.send_message(msg_channel, msg_prefix + return_msg[0])
                vdst[server_id].toggle_lock(False)
                return True
            else:
                vdst[server_id].toggle_lock(False)
                return False
        # case 2: a list of tuples of IDs and message
        await client.send_message(msg_channel, msg_prefix + return_msg[1])

        if type(return_msg[0]) == dict:
            return_msg[0]   =   [ t for t in return_msg[0].items() if t[0] != 'guild' and t[0] != 'remainder' ]
            return_msg[0]   =   sorted(return_msg[0], key=lambda t: t[1], reverse=True)
            return_msg[0]   =   [ (t[0]+'@'," has contributed " + str(int(t[1])) + " Talt.") for t in return_msg[0] ]

        message_to_send =   "```ini\n"

        # loop count
        i   =   0

        for ret in return_msg[0]:
            await client.send_typing(msg_channel)
            message_to_send +=   "\n"
            # case 2a: tuples contain list of IDs and message
            if type(ret[0]) == list:
                r_ids   =   ret[0]
            # case 2b: tuples contain ID and message
            else:
                r_ids   =   [ret[0]]

            if not r_ids:
                await client.send_message(msg_channel, message_to_send + "*crickets chirping*\n" + "```\n")
                return True

            for r_id in r_ids:
                # if type(r_id[0]) is list:
                #     ident   =   r_id[-1]
                #     things  =   r_id[0]
                # else:
                #     ident   =   ret[-1]
                #     things  =   [r_id]

                # channel
                if rgx_ch_hash.search(r_id):
                    chn =   rgx_ch_hash.sub('', r_id)
                    try:
                        nom =   message.server.get_channel(chn).name
                        message_to_send +=  "[" + nom + "]" + " " + ret[1] + "\n"
                    except: # channel no longer exists; purge
                        vdst[server_id].unset_channel(chn)

                # user
                elif rgx_ch_member.search(r_id):
                    mem =   rgx_ch_member.sub('', r_id)
                    try:
                        tgt =   message.server.get_member(mem)
                        nom =   tgt.name + "#" + tgt.discriminator
                    except:
                        if not rgx_talt.search(ret[1]):
                            vdst[server_id].set_role(mem, "users")
                        else:
                            message_to_send +=  "[ missing user ] " + ret[1] + "\n"
                        continue
                    message_to_send +=  "[" + nom + "]" + " " + ret[1] + "\n"

                # unknown; no identifying character detected, but role most likely
                else:
                    try:
                        tgt =   [ro.id for ro in message.server.roles].index(r_id)
                        nom =   "&" + message.server.roles[tgt].name
                        message_to_send +=  "[" + nom + "]" + " " + ret[1] + "\n"
                    except: # user or role no longer exists; total purge (remove all permissions)
                        try:
                            tgt =   message.server.get_member(r_id)
                            nom =   tgt.name + "#" + tgt.discriminator
                            message_to_send +=  "[" + nom + "]" + " " + ret[1] + "\n"
                        except:
                            if not rgx_talt.search(ret[1]):
                                vdst[server_id].rm_boss(r_id)
                                vdst[server_id].set_role(r_id, "users")
                            else:
                                message_to_send +=  "[ missing user ] " + ret[1] + "\n"
                            continue


            i   +=  1

            if i % 5 == 0:                    
                await client.send_message(msg_channel, message_to_send + "```\n")
                message_to_send =   "```ini"


        try:
            # flush remaining
            if message_to_send and not rgx_ini.match(message_to_send):
                await client.send_message(msg_channel, message_to_send + "```\n")
            elif message_to_send and i < 5:
                await client.send_message(msg_channel, none_matched)
        except Exception as e:
            # do something with e later
            pass

        vdst[server_id].toggle_lock(False)

    else:
        return False # command was incorrect

# begin periodic database check
####

# @func:    check_databases() : void
#       Checks databases routinely, by minute.
>>>>>>> 68eeae999794084814288b8bbfe625d30b6a5ec1
async def check_databases():
    """
    :func:`check_databases` checks the database for entries roughly every minute.
    Records are output to the relevant Discord channels.
    """
    await bot.wait_until_ready()
    print('Startup completed; starting check_databases')

    for guild in bot.guilds:
        if not guild.unavailable:
            guild_id = str(guild.id)
            guild_owner_id = str(guild.owner.id)
            vdbs[guild.id] = vaivora_modules.db.Database(guild_id)
            vdst[guild.id] = vaivora_modules.settings.Settings(guild_id, guild_owner_id)
            #await greet(guild.id, guild.owner)

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
            discord_channel = None
            if not await valid_db.check_if_valid():
                await valid_db.create_db()
                continue
            results[vdb_id] = await valid_db.check_db_boss()

            # empty record; dismiss
            if not results[vdb_id]:
                continue

            # sort by time - yyyy, mm, dd, hh, mm
            results[vdb_id].sort(key=itemgetter(5,6,7,8,9))

            # iterate through all results
            for result in results[vdb_id]:
                discord_channel = result[4]
                list_time = [ int(t) for t in result[5:10] ]
                record_info = [ str(r) for r in result[0:4] ]

                current_boss = record_info[0]
                current_channel = record_info[1]
                current_time = record_info[2]
                current_status = record_info[3]

                entry_time = datetime(*list_time)

                record = vaivora_modules.boss.process_record(current_boss,
                                                             current_status,
                                                             entry_time,
                                                             current_time,
                                                             current_channel)

                record2byte = "{}:{}:{}:{}".format(discord_channel,
                                                   current_boss,
                                                   entry_time.strftime("%Y/%m/%d %H:%M"),
                                                   current_channel)
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
                    message_to_send.append([record, discord_channel,])
                    minutes[str(hashed_record)] = entry_time.minute

            # empty record for this server
            if len(message_to_send) == 0:
                continue

            roles = []

            # compare roles against server
            guild = bot.get_guild(vdb_id)
            for uid in vdst[vdb_id].get_role(lang.ROLE_BOSS):
                try:
                    # group mention
                    idx = [role.id for role in guild.roles].index(uid)
                    roles.append[guild.roles[idx].mention]
                except:
                    if rgx_user.search(uid):
                        uid = rgx_user.sub('', uid)

                    try:
                        # user mention
                        boss_user = guild.get_member(uid)
                        roles.append(boss_user.mention)
                    except:
                        # user or group no longer exists
                        vdst[vdb_id].rm_boss(uid)

            role_str = ' '.join(roles)

            discord_channel = None
            discord_message = None
            for message in message_to_send:
                if discord_channel != int(message[-1]):
                    if discord_channel:
                        try:
                            await guild.get_channel(discord_channel).send(discord_message)
                        except:
                            pass

                        discord_message = None
                    discord_channel = int(message[-1])

                    # replace time_str with server setting warning, eventually
                    discord_message = lang.BOSS_ALERT.format(role_str)
                discord_message = '{} {}'.format(discord_message, message[0])

            try:
                await guild.get_channel(discord_channel).send(discord_message)
            except Exception as e:
                print(e)
                pass

        #await client.process_commands(message)
        await asyncio.sleep(1)
####
# end of periodic database check


# begin everything
secret = vaivora_modules.secrets.discord_token

bot.loop.create_task(check_databases())
bot.run(secret)