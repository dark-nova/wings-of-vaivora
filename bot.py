#!/usr/bin/env python
import re
import os
import sys
import asyncio
from datetime import timedelta
from operator import itemgetter
from math import floor

import discord
from discord.ext import commands
import pendulum

import checks
import secrets
import vaivora.db
import vaivora.utils
import constants.main
import constants.boss
import constants.settings
import constants.events


bot = commands.Bot(command_prefix=['$','Vaivora, ','vaivora ','vaivora, '])

initial_extensions = ['cogs.admin',
                      'cogs.settings',
                      'cogs.boss',
                      'cogs.meme',
                      'cogs.gems',
                      'cogs.offset',
                      'cogs.events'
                      ]

# snippet from https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)

bot.remove_command('help')

vdbs = {} # a dict containing db.py instances, with indices = server id's


@bot.event
async def on_ready():
    """Handles whenever the bot is ready.

    Returns:
        bool: True

    """
    print("Logging in...")
    #await bot.change_presence(status=discord.Status.dnd)
    await bot.change_presence(activity=discord.Game(name=("in {} guilds. [$help] for info"
                                                          .format(str(len(bot.guilds))))),
                              status=discord.Status.online)
    print('Successsfully logged in as: {}#{}. Ready!'.format(bot.user.name, bot.user.id))
    return True


@bot.event
async def on_guild_join(guild):
    """Handles what to do when a guild adds Wings of Vaivora.

    Args:
        guild (discord.Guild): the guild which this client has joined

    Returns:
        bool: True if successful; False otherwise

    """
    #vaivora_version = vaivora.version.get_current_version()

    if guild.unavailable:
        return False

    vdbs[guild.id] = vaivora.db.Database(str(guild.id))
    owner = guild.owner
    #vdst[guild.id] = vaivora.settings.Settings(str(guild.id), str(owner.id))

    #await greet(guild.id, owner)
    await owner.send(owner, constants.main.WELCOME)

    return True


@bot.command(aliases=['halp'])
async def help(ctx):
    """Retrieves the help pages for `$help`.

    Args:
        ctx (discord.ext.commands.context): context of the message

    Returns:
        bool: True if successful; False otherwise

    """
    try:
        await ctx.author.send(constants.main.MSG_HELP)
    except:
        return False

    return True


async def check_databases():
    """Checks the database for entries roughly every minute.

    Records are output to the relevant Discord channels.

    """
    # list of guild id's to skip for event checking
    skip_events = []

    await bot.wait_until_ready()
    print('Startup completed; starting check_databases')

    await asyncio.sleep(1)

    print('Attempting to check user permissions and event config...')

    # Check guild databases
    for guild in bot.guilds:
        if not guild.unavailable:
            print('Checking guild {}...'.format(guild.id))
            vdbs[guild.id] = vaivora.db.Database(guild.id)

            if not await vdbs[guild.id].init_events():
                print(
                    '...event check failed! Removing guild {} from loop'
                    .format(guild.id)
                    )
                skip_events.append(guild.id)
            else:
                print('Guild', guild.id, 'event table looks OK!')

            try:
                if not await vdbs[guild.id].update_user_sauth(
                        guild.owner.id, owner=True):
                    print(
                        '...permission check failed! in {} with owner {}'
                        .format(guild.id, guild.owner.id)
                        )
                    raise Exception

                if guild.owner.id != secrets.discord_user_id:
                    if not await vdbs[guild.id].update_user_sauth(
                            secrets.discord_user_id, owner=False):
                        print(
                            '...permission check failed! in {} with owner id {}'
                            .format(guild.id, guild.owner.id)
                            )
                        raise Exception

                print('Guild', guild.id, 'permissions look OK!')

                if await vdbs[guild.id].clean_duplicates():
                    print(
                        'Duplicates have been removed from tables from guild',
                        guild.id
                        )
            except:
                print('Guild', guild.id,
                    'might be corrupt! Rebuilding and skipping...')
                await vdbs[guild.id].create_all(guild.owner.id)
                del vdbs[guild.id] # do not use corrupt/invalid db

    minutes = {}
    hashed_records = []

    while not bot.is_closed():
        loop_time = pendulum.now()
        print(loop_time.strftime("%Y/%m/%d %H:%M"),
              "- Valid DBs:", len(vdbs))

        # prune hashed_records once they're no longer alert-able
        purged = []
        if len(minutes) > 0:
            for rec_hash, rec_mins in minutes.items():
                mins_now = pendulum.now().minute
                # e.g. 48 > 03 (if record was 1:03
                # and time now is 12:48), passes conds 1 & 2 but fails cond 3
                if ((rec_mins < mins_now)
                    and ((mins_now-rec_mins) > 0)
                    and ((mins_now-rec_mins+15+1) < 60)):
                    hashed_records.remove(rec_hash)
                    purged.append(rec_hash)

        for purge in purged:
            try:
                del minutes[purge]
            except:
                continue

        # iterate through every valid database
        for vdb_id, valid_db in vdbs.items():
            print(loop_time.strftime("%H:%M"), "- in DB:", vdb_id)

            # check all timers
            messages = []
            if not await valid_db.check_if_valid(constants.settings.ROLE_BOSS):
                await valid_db.create_db(constants.settings.ROLE_BOSS)
                continue
            results_boss = await valid_db.check_db_boss()
            results_events = await valid_db.list_all_events()

            # empty record; dismiss
            if not (results_boss and results_events):
                continue

            diff_h, diff_m = await vaivora.utils.get_time_diff(vdb_id)
            full_diff = timedelta(hours=diff_h, minutes=diff_m)

            # sort by time - YYYY, MM, DD, hh, mm
            results_boss.sort(key=itemgetter(5,6,7,8,9))

            for result in results_boss:
                discord_channel = result[4]
                time = [int(t) for t in result[5:10]]
                boss, channel, _map, status = [str(r) for r in result[0:4]]

                try:
                    entry_time = pendulum.datetime(
                        *time, tz=loop_time.timezone_name
                        )
                except ValueError as e:
                    print('check_databases', vdb_id, '\n', e)
                    continue

                # process time difference
                time_diff = entry_time - (loop_time + full_diff)

                # record is in the past
                if time_diff.hours < 0 or time_diff.minutes < 0:
                    continue

                record = await vaivora.utils.process_boss_record(
                    boss,
                    status,
                    entry_time,
                    time_diff,
                    _map,
                    channel,
                    vdb_id
                    )

                hashed_record = await vaivora.utils.hash_object(
                    discord_channel,
                    boss,
                    entry_time,
                    channel
                    )

                # don't add a record that is already stored
                if hashed_record in hashed_records:
                    continue

                # record is within range of alert
                if time_diff.seconds <= 900 and time_diff.seconds > 0:
                    hashed_records.append(hashed_record)
                    messages.append({
                        'record': record,
                        'type': constants.settings.ROLE_BOSS,
                        'discord_channel': discord_channel
                        })
                    minutes[str(hashed_record)] = entry_time.minute

            # only check for events if the db passed the earlier check
            if vdb_id not in skip_events:
                for result in results_events:
                    events_channels = await valid_db.get_channel(
                        constants.settings.ROLE_EVENTS
                        )
                    if not events_channels:
                        continue

                    status = ''
                    name = result[0]
                    time = result[1:-1]

                    if name in vaivora.db.permanent_events:
                        # don't even try if it's disabled
                        if result[-1] == 0:
                            continue
                        today = pendulum.today()
                        to_add = (vaivora.db.event_days[name] - today.day_of_week) % 7
                        next_day = today + timedelta(days=to_add)
                        time = [
                            next_day.year,
                            next_day.month,
                            next_day.day,
                            *vaivora.db.event_times[name]
                            ]
                        status = constants.events.EMOJI_ALERT
                        name = '{} {}'.format(name, status)

                    try:
                        entry_time = pendulum.datetime(
                            *time, tz=loop_time.timezone_name
                            )
                    except ValueError as e:
                        print('check_databases', vdb_id, '\n', e)
                        continue

                    time_diff = entry_time - (loop_time + full_diff)

                    # record is in the past
                    if time_diff.hours < 0 or time_diff.minutes < 0:
                        continue

                    if time_diff.minutes == 1:
                        mins = '{} minute'.format(time_diff.minutes)
                    else:
                        mins = '{} minutes'.format(time_diff.minutes)

                    ending = 'ends'

                    if name in vaivora.db.permanent_events:
                        ending = 'resets'

                    end_date = entry_time.strftime("%Y/%m/%d %H:%M")

                    record = ('**{}**\n- {} at **{}** ({})'
                              .format(name, ending, end_date,
                                      mins))

                    hashed_record = await vaivora.utils.hash_object(
                        discord_channel,
                        name,
                        entry_time
                        )

                    # don't add a record that is already stored
                    if hashed_record in hashed_records:
                        continue

                    # record is within range of alert
                    if time_diff.seconds <= 3600 and time_diff.seconds > 0:
                        hashed_records.append(hashed_record)
                        messages.append({
                            'record': record,
                            'type': constants.settings.ROLE_EVENTS,
                            'discord_channel': discord_channel
                            })
                        minutes[str(hashed_record)] = entry_time.minute

            # empty record for this guild
            if len(messages) == 0:
                continue

            await send_messages(messages, bot.get_guild(vdb_id))

        #await client.process_commands(message)
        await asyncio.sleep(59)


async def send_messages(messages: list, guild):
    """Sends messages compiled by the background loop.

    Args:
        messages (list of dict): messages to send, in a structure:
            - 'record': the actual content
            - 'type': the channel and role type
            - 'discord_channel': the Discord channel to send to
        guild: the Discord guild

    Returns:
        bool: True if run successfully regardless of result

    """
    roles = {}
    channels_in = {}
    can_send = True
    v_roles = [constants.settings.ROLE_BOSS, constants.settings.ROLE_EVENTS]
    for v_role in v_roles:
        roles[v_role] = await get_roles(guild, v_role)
        channels_in[v_role] = [
            int(message['discord_channel']) for message in messages
            if message['type'] == v_role
            ]

    channels = [int(message['discord_channel']) for message in messages]

    for channel in channels:
        # before attempting to send messages, make sure to
        # check it can receive messages
        try:
            guild_channel = guild.get_channel(channel)
            guild_channel.name
        except AttributeError as e:
            # remove invalid channel
            print('check_databases', guild.id, '\n', e)
            for v_role in v_roles:
                if channel in channels_in[v_role]:
                    await vdbs[guild.id].remove_channel(
                        v_role, channel
                        )
            continue
        except:
            # can't retrieve channel definitively; abort
            print('check_databases', guild.id, '\n', e)
            continue

        only_ch_messages = [message for message in messages
                            if int(message['discord_channel']) == channel]
        for v_role in v_roles:
            messages_for = [message['record'] for message in only_ch_messages
                            if message['type'] == v_role]
            if len(messages_for) == 0:
                # skip if the channel has no records for a given type
                continue

            if v_role == 'boss':
                alert = constants.main.BOSS_ALERT
            else:
                alert = constants.main.EVENTS_ALERT

            discord_message = alert.format(roles[v_role])
            for message in messages_for:
                # maximum Discord message length is 2000
                if len(discord_message) >= 1600:
                    try:
                        await (
                            guild.get_channel(channel)
                            .send(discord_message)
                            )
                    except:
                        # message could not be sent; ignore
                        can_send = False
                        break
                    discord_message = message
                else:
                    discord_message = '{} {}'.format(
                        discord_message,
                        message
                        )
            if not can_send:
                break
            if discord_message:
                await (
                    guild.get_channel(channel)
                    .send(discord_message)
                    )

        can_send = True

    return True


async def get_roles(guild, role: str):
    """Gets roles from a guild.

    Invalid roles will be purged during this process.

    Args:
        guild: the Discord guild
        role (str): the Vaivora role to get

    Returns:
        str: a space delimited string of mentionable roles

    """
    mentionable = []
    invalid = []
    role_ids = await vdbs[guild.id].get_users(role)
    for role_id in role_ids:
        try:
            idx = [role.id for role in guild.roles].index(role_id)
            mentionable.append(guild.roles[idx].mention)
        except Exception as e:
            # Discord role no longer exists
            print('get_roles', e)
            invalid.append(role_id)

    if invalid:
        await vdbs[guild_id].remove_users(
            role, invalid
            )

    return ' '.join(mentionable)


# begin everything
secret = secrets.discord_token

bot.loop.create_task(check_databases())
bot.run(secret)
