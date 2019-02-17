#!/usr/bin/env python
import re
import os
import asyncio
from hashlib import blake2b
from datetime import datetime, timedelta
from operator import itemgetter

import discord
from discord.ext import commands

import vaivora_modules.boss
import vaivora_modules.db
import vaivora_modules.disclaimer
import vaivora_modules.secrets
import vaivora_modules.settings
import constants.main
import constants.boss
import constants.db
import constants.errors
import constants.settings
# from constants.errors import en_us as constants.main_err
# from constants.settings import en_us as constants.main_settings
# from constants.boss import en_us as constants.main_boss
# from constants.db import en_us as constants.main_db
# from constants.main import en_us as constants.main


bot = commands.Bot(command_prefix=['$','Vaivora, ','vaivora ','vaivora, '])
bot.remove_command('help')

# vdbs & vdst will now use int for dict keys; previously str of int
vdbs = {}
#vdst = {}

rgx_help = re.compile(r'help', re.IGNORECASE)
rgx_user = re.compile(r'@')
to_sanitize = re.compile(r"""[^a-z0-9 .:$"',-]""", re.IGNORECASE)

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


def check_channel(ch_type):
    """
    :func:`check_channel` checks whether a channel is allowed
    to interact with Wings of Vaivora.

    Args:
        ch_type (str): the type (name) of the channel

    Returns:
        True if successful; False otherwise
            Note that this means if no channels have registered,
            *all* channels are valid.
    """
    @commands.check
    async def check(ctx):
        chs = await (vaivora_modules.settings
                     .get_channel(ctx.guild.id, ch_type))

        if chs and ctx.channel.id not in chs:
            return False # silently ignore wrong channel
        else: # in the case of `None` chs, all channels are valid
            return True
    return check


def check_role():
    """
    :func:`check_role` sees whether the user is authorized
    to run a settings command.

    Returns:
        True if the user is authorized; False otherwise
    """
    @commands.check
    async def check(ctx):
        users = await (vaivora_modules.settings
                       .get_users(ctx.guild.id,
                                  constants.settings.ROLE_SUPER_AUTH))

        if users and str(ctx.author.id) in users:
            return True
        else:
            users = await (vaivora_modules.settings
                           .get_users(ctx.guild.id,
                                      constants.settings.ROLE_AUTH))

        if users and str(ctx.author.id) in users:
            return True
        else:
            await ctx.send('{} {}'
                            .format(ctx.author.mention,
                                    constants.settings.FAIL_NOT_AUTH))
            return False
    return check


def only_in_guild():
    """
    :func:`only_in_guild` checks whether a command can run.

    Returns:
        True if guild; False otherwise
    """
    @commands.check
    async def check(ctx):
        if ctx.guild == None: # not a guild
            await ctx.send(constants.errors.CANT_DM.format(constants.boss.COMMAND))
            return False
        return True
    return check


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
    #vdst[guild.id] = vaivora_modules.settings.Settings(str(guild.id), str(owner.id))

    #await greet(guild.id, owner)
    await owner.send(owner, constants.main.WELCOME)

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
        await ctx.author.send(constants.main.MSG_HELP)
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
@only_in_guild()
@check_channel(constants.main.ROLE_BOSS)
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
    subcmd = await vaivora_modules.boss.what_status(ctx.subcommand_passed)

    if ctx.boss == constants.boss.CMD_ARG_TARGET_ALL:
       await ctx.send(constants.errors.IS_INVALID_3
                      .format(ctx.author.mention, ctx.boss,
                              constants.boss.CMD_ARG_TARGET, subcmd))
       return False

    try:
        _boss, _time, _map, _channel = await boss_helper(ctx.boss, time, map_or_channel)
    except:
        which_fail = await boss_helper(ctx.boss, time, map_or_channel)
        if len(which_fail) == 1:
            await ctx.send(constants.errors.IS_INVALID_2
                           .format(ctx.author.mention, ctx.boss,
                                   constants.boss.CMD_ARG_TARGET))
        elif len(which_fail) == 2:
            await ctx.send(constants.errors.IS_INVALID_3
                           .format(ctx.author.mention, time,
                                   ctx.subcommand_passed, 'time'))
        else:
            pass
        return False

    opt = {constants.db.COL_BOSS_CHANNEL: _channel, constants.db.COL_BOSS_MAP: _map}
    msg = await (vaivora_modules.boss
                 .process_cmd_status(ctx.guild.id, ctx.channel.id,
                                     _boss, subcmd, _time, opt))
    await ctx.send('{} {}'.format(ctx.author.mention, msg))

    return True


@boss.command(name='list', aliases=['ls', 'erase', 'del', 'delete', 'rm'])
@only_in_guild()
@check_channel(constants.main.ROLE_BOSS)
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
    if ctx.boss != constants.boss.CMD_ARG_TARGET_ALL:
        boss_idx = await vaivora_modules.boss.check_boss(ctx.boss)
        if boss_idx == -1:
            await ctx.send(constants.errors.IS_INVALID_2
                           .format(ctx.author.mention, ctx.boss,
                                   constants.boss.CMD_ARG_TARGET))
            return False
        boss = constants.boss.ALL_BOSSES[boss_idx]
    else:
        boss = constants.boss.ALL_BOSSES

    if channel is not None:
        channel = constants.boss.REGEX_OPT_CHANNEL.match(channel)
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
    Unlike other boss commands, :func:`query` and :func:`_type` can be used in DMs.

    Args:
        ctx (discord.ext.commands.Context): context of the message

    Returns:
        True if run successfully, regardless of result
    """
    subcmd = await vaivora_modules.boss.what_query(ctx.subcommand_passed)

    if ctx.boss == constants.boss.CMD_ARG_TARGET_ALL:
       await ctx.send(constants.errors.IS_INVALID_3
                      .format(ctx.author.mention, ctx.boss,
                              constants.boss.CMD_ARG_TARGET, subcmd))
       return False
    else:
        boss_idx = await vaivora_modules.boss.check_boss(ctx.boss)
        if boss_idx == -1:
            await ctx.send(constants.errors.IS_INVALID_2
                           .format(ctx.author.mention, ctx.boss,
                                   constants.boss.CMD_ARG_TARGET))
            return False
        boss = constants.boss.ALL_BOSSES[boss_idx]

    msg = await vaivora_modules.boss.process_cmd_query(boss, subcmd)

    await ctx.send('{}\n\n{}'.format(ctx.author.mention, msg))


@boss.command(name='world', aliases=['w', 'field', 'f', 'demon', 'd', 'dl'])
async def _type(ctx):
    """
    :func:`_type` returns a user-usable list of types of bosses: World, Field, Demon.
    Unlike other boss commands, :func:`query` and :func:`_type` can be used in DMs.

    Args:
        ctx (discord.ext.commands.Context): context of the message

    Returns:
        True if run successfully, regardless of result
    """
    subcmd = await vaivora_modules.boss.what_type(ctx.subcommand_passed)

    if ctx.boss != constants.boss.CMD_ARG_TARGET_ALL:
       await ctx.send(constants.errors.IS_INVALID_3
                      .format(ctx.author.mention, ctx.boss,
                              constants.boss.CMD_ARG_TARGET, subcmd))
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

    boss = constants.boss.ALL_BOSSES[boss_idx]

    if len(constants.boss.BOSS_MAPS[boss]) == 1:
        map_idx = 0 # it just is

    if map_or_channel and type(map_or_channel) is int:
        if map_or_channel <= 4 or map_or_channel > 1:
            channel = map_or_channel # use user-input channel only if valid
    elif map_or_channel and constants.boss.REGEX_OPT_CHANNEL.match(map_or_channel):
        channel = constants.boss.REGEX_OPT_CHANNEL.match(map_or_channel)
        channel = int(channel.group(2)) # channel will always be 1 through 4 inclusive
    elif type(map_or_channel) is str and map_idx != 0: # possibly map
        map_idx = await vaivora_modules.boss.check_maps(boss_idx, map_or_channel)

    if (not map_idx and map_idx != 0) or map_idx == -1:
        _map = ""
    else:
        _map = constants.boss.BOSS_MAPS[boss][map_idx]

    return (boss, time, _map, channel)


@bot.group()
async def settings(ctx):
    """
    :func:`boss` handles "$boss" commands.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        arg: (default: None) e.g. 'help'

    Returns:
        True
    """
    return True


@settings.command(name='help')
async def s_help(ctx):
    """
    :func:`_help` retrieves help pages for `$settings`.

    Args:
        ctx (discord.ext.commands.Context): context of the message

    Returns:
        True
    """
    _help = vaivora_modules.settings.help()
    for _h in _help:
        await ctx.author.send(_h)
    return True


# $settings set <target> <kind> <discord object>
@settings.command()
@only_in_guild()
@check_channel(constants.main.ROLE_SETTINGS)
@check_role()
async def set(ctx, target, kind, ids: commands.Greedy[int] = 0):
    """
    :func:`set` sets `target`s to `kind`s.
    e.g. sets a channel (target) to boss (kind)

    Args:
        ctx (discord.ext.commands.Context): context of the message
        target (str): the object to set
        kind (str): the kind/type to use

    Returns:
        True if run successfully, regardless of result
    """
    if constants.settings.REGEX_SETTING_TARGET_CHANNEL.match(target):
        target = constants.settings.TARGET_CHANNEL

        if kind != constants.main.ROLE_BOSS and kind != constants.main.ROLE_SETTINGS:
            await ctx.send(constants.errors.IS_INVALID_3.format(
                ctx.author.mention, kind,
                constants.main.ROLE_SETTINGS, target))



        if ctx.message.channel_mentions:
            _ids = []
            for channel_mention in ctx.message.channel_mentions:
                _ids.append(str(channel_mention.id))
            await vaivora_modules.settings
        else:
            await ctx.send(constants.errors.TOO_FEW_ARGS.format(
                ctx.author.mention, constants.main.ROLE_SETTINGS,
                constants.settings.USAGE_SET_CHANNELS))
            return False


        if ids: # a list of id's as ints
            for _id in ids:
                pass


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



#     if vaivora_modules.settings.what_setting(args[0]):
#         arg_subcmd = constants.settings.CMD_ARG_SETTING
#     elif vaivora_modules.settings.what_validation(args[0]):
#         arg_subcmd = constants.settings.CMD_ARG_VALIDATION
#     elif vaivora_modules.settings.what_rolechange(args[0]):
#         arg_subcmd = constants.settings.CMD_ARG_ROLECHANGE
#     else:
#         await ctx.send(constants.errors.IS_INVALID_2.format(ctx.author.mention, args[0],
#                                                     constants.settings.CMD_ARG_SUBCMD))
#         return False

#     if arg_subcmd == constants.settings.CMD_ARG_SETTING:
#         setting = vaivora_modules.settings.what_setting(args[0])
#         target = vaivora_modules.settings.what_setting_target(args[1])
#         if target is None or (target != constants.settings.TARGET_TALT and
#                               setting == constants.settings.SETTING_ADD):
#             await ctx.send(constants.errors.IS_INVALID_3.format(ctx.author.mention, args[0],
#                                                         constants.settings.CMD_ARG_SETTING, arg_subcmd))
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
            try:
                if not await vdbs[guild.id].update_owner_sauth(guild_owner_id):
                    raise Exception
            except:
                del vdbs[guild.id] # do not use corrupt/invalid db
                print('Guild', guild.id, 'might be corrupt! Skipping...')

            if await vdbs[guild.id].clean_duplicates():
                print('Duplicates have been removed from tables from',
                      guild.id)

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
            if not await valid_db.check_if_valid(constants.main.ROLE_BOSS):
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
            guild_boss_roles = await vdbs[vdb_id].get_role(constants.main.ROLE_BOSS)
            for boss_role in guild_boss_roles:
                try:
                    # group mention
                    idx = [role.id for role in guild.roles].index(boss_role)
                    roles.append[guild.roles[idx].mention]
                except:
                    if rgx_user.search(boss_role):
                        boss_role = rgx_user.sub('', boss_role)

                    try:
                        # user mention
                        boss_user = guild.get_member(boss_role)
                        roles.append(boss_user.mention)
                    except:
                        # user or group no longer exists
                        await vdbs[vdb_id].rm_boss(boss_role)

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
                    discord_message = constants.main.BOSS_ALERT.format(role_str)
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