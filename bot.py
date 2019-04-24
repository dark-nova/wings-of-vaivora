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


bot = commands.Bot(command_prefix=['$','Vaivora, ','vaivora ','vaivora, '])

initial_extensions = ['cogs.admin',
                      'cogs.settings',
                      'cogs.boss',
                      'cogs.meme',
                      'cogs.gems',
                      'cogs.offset']

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
    records = []

    while not bot.is_closed():
        await asyncio.sleep(59)
        loop_time = pendulum.now()
        print(loop_time.strftime("%Y/%m/%d %H:%M"),
              "- Valid DBs:", len(vdbs))

        # prune records once they're no longer alert-able
        purged = []
        if len(minutes) > 0:
            for rec_hash, rec_mins in minutes.items():
                mins_now = pendulum.now().minute
                # e.g. 48 > 03 (if record was 1:03
                # and time now is 12:48), passes conds 1 & 2 but fails cond 3
                if ((rec_mins < mins_now)
                    and ((mins_now-rec_mins) > 0)
                    and ((mins_now-rec_mins+15+1) < 60)):
                    records.remove(rec_hash)
                    purged.append(rec_hash)

        for purge in purged:
            try:
                del minutes[purge]
            except:
                continue

        # iterate through database results_boss
        for vdb_id, valid_db in vdbs.items():
            print(loop_time.strftime("%H:%M"), "- in DB:", vdb_id)
            results_boss = []


            # check all timers
            message_to_send = []
            discord_channel = None
            if not await valid_db.check_if_valid(constants.settings.ROLE_BOSS):
                await valid_db.create_db(constants.settings.ROLE_BOSS)
                continue
            results_boss = await valid_db.check_db_boss()
            results_events = await valid_db.list_all_events()

            # empty record; dismiss
            if not (results_boss and results_events):
                continue

            tz = await valid_db.get_tz()
            if not tz:
                tz = constants.offset.DEFAULT

            offset = await valid_db.get_offset()
            if not offset:
                offset = 0

            diff_h, diff_m = await vaivora.utils.get_time_diff(tz)
            full_diff = timedelta(hours=(diff_h + offset), minutes=diff_m)

            # sort by time - yyyy, mm, dd, hh, mm
            results_boss.sort(key=itemgetter(5,6,7,8,9))

            # iterate through all results_boss
            for result in results_boss:
                discord_channel = result[4]
                list_time = [ int(t) for t in result[5:10] ]
                record_info = [ str(r) for r in result[0:4] ]

                current_boss = record_info[0]
                current_channel = record_info[1]
                current_time = record_info[2]
                current_status = record_info[3]

                entry_time = pendulum.datetime(
                    *list_time,
                    tz=pendulum.now().timezone_name)

                # process time difference
                time_diff = entry_time - (loop_time + full_diff)

                # record is in the past
                if time_diff.hours < 0 or time_diff.minutes < 0:
                    continue

                record =  await vaivora.utils.process_record(
                    current_boss,
                    current_status,
                    entry_time,
                    time_diff,
                    current_time,
                    current_channel,
                    vdb_id
                    )

                hashed_record = await vaivora.utils.hash_object(
                    discord_channel,
                    current_boss,
                    entry_time,
                    current_channel
                    )

                # don't add a record that is already stored
                if hashed_record in records:
                    continue

                # record is within range of alert
                if time_diff.seconds <= 900 and time_diff.seconds > 0:
                    records.append(hashed_record)
                    message_to_send.append([record, discord_channel,])
                    minutes[str(hashed_record)] = entry_time.minute

            if vdb_id not in skip_events:
                for result in results_events:
                    events_channels = await valid_db.get_channel('events')
                    if not event_channels:
                        pass

            # empty record for this server
            if len(message_to_send) == 0:
                continue

            roles = []

            # compare roles against server
            guild = bot.get_guild(vdb_id)
            guild_boss_roles = await vdbs[vdb_id].get_users(
                                    constants.settings.ROLE_BOSS)
            for boss_role in guild_boss_roles:
                try:
                    idx = [role.id for role in guild.roles].index(boss_role)
                    roles.append(guild.roles[idx].mention)
                except Exception as e:
                    # Discord role no longer exists
                    print(e)
                    await vdbs[vdb_id].remove_users(
                            constants.settings.ROLE_BOSS,
                            (boss_role,))

            roles = ' '.join(roles)

            discord_channel = None
            discord_message = None
            for message in message_to_send:
                if discord_channel != int(message[-1]):
                    if discord_channel:
                        try:
                            await (guild.get_channel(discord_channel)
                                   .send(discord_message))
                        except Exception as e:
                            # eventually handle removing invalid channels
                            print('check_databases', guild.id, '\n', e)
                        discord_message = None

                    discord_channel = int(message[-1])
                    discord_message = (constants.main.BOSS_ALERT
                                       .format(roles))

                discord_message = '{} {}'.format(discord_message,
                                                 message[0])

            try:
                await guild.get_channel(discord_channel).send(discord_message)
            except Exception as e:
                print('check_databases', e)
                pass

        #await client.process_commands(message)
        await asyncio.sleep(1)
####
# end of periodic database check


# begin everything
secret = secrets.discord_token

bot.loop.create_task(check_databases())
bot.run(secret)
