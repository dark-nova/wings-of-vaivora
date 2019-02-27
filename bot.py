#!/usr/bin/env python
import re
import os
import sys
import asyncio
from hashlib import blake2b
from datetime import datetime, timedelta
from operator import itemgetter

import discord
from discord.ext import commands

import checks
import secrets
import vaivora.db
import vaivora.disclaimer
import constants.main
import constants.boss
import constants.errors
import constants.settings


bot = commands.Bot(command_prefix=['$','Vaivora, ','vaivora ','vaivora, '])

initial_extensions = ['cogs.settings',
                      'cogs.boss',
                      'cogs.meme']

# snippet from https://gist.github.com/EvieePy/d78c061a4798ae81be9825468fe146be
if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

bot.remove_command('help')

vdbs = {} # a dict containing db.py instances, with indices = server id's

rgx_user = re.compile(r'@')


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
async def on_guild_join(guild):
    """
    :func:`on_guild_join` handles what to do when a guild adds Wings of Vaivora.

    Args:
        guild (discord.Guild): the guild which this client has joined

    Returns:
        True if successful; False otherwise
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


async def process_record(boss, status, time, boss_map, channel):
    """
    :func:`process_records` processes a record to print out

    Args:
        boss (str): the boss in question
        status (str): the status of the boss
        time (datetime): the `datetime` of the target set to its next approximate spawn
        boss_map (str): the map containing the last recorded spawn
        channel (str): the channel of the world boss if applicable; else, 1

    Returns:
        str: a formatted markdown message containing the records
    """
    channel = str(floor(float(channel)))

    if boss_map == constants.boss.CMD_ARG_QUERY_MAPS_NOT:
        # use all maps for Demon Lord if not previously known
        if boss in constants.boss.BOSSES[constants.boss.KW_DEMON]:
            boss_map = '\n'.join([constants.boss.RECORD.format(constants.boss.EMOJI_LOC,
                                                          loc, channel)
                                  for loc in constants.boss.BOSS_MAPS[boss]])
        # this should technically not be possible
        else:
            boss_map = constants.boss.RECORD.format(constants.boss.EMOJI_LOC, constants.boss.BOSS_MAPS[boss], channel)
    # use all other maps for Demon Lord if already known
    elif boss in constants.boss.BOSSES[constants.boss.KW_DEMON]:
        boss_map = '\n'.join(['{} {}'.format(constants.boss.EMOJI_LOC, loc)
                              for loc in constants.boss.BOSS_MAPS[boss] if loc != boss_map])
    elif boss == constants.boss.BOSS_W_KUBAS:
        # valid while Crystal Mine Lot 2 - 2F has 2 channels
        channel = str(int(channel) % 2 + 1)
        boss_map = constants.boss.RECORD_KUBAS.format(constants.boss.EMOJI_LOC, boss_map, channel)
    else:
        boss_map = constants.boss.RECORD.format(constants.boss.EMOJI_LOC, boss_map, channel)
        

    minutes = floor((time - (datetime.now() 
                                  + timedelta(hours=constants.boss.TIME_H_LOCAL_TO_SERVER)))
                        .seconds / 60)
    minutes = '{} minutes'.format(str(minutes))

    # set time difference based on status and type of boss
    # takes the negative (additive complement) to get the original time
    time_diff = get_offset(boss, status, coefficient=-1)
    # and add it back to get the reported time
    report_time = time + time_diff

    if status == constants.boss.CMD_ARG_STATUS_ANCHORED:
        plus_one = time + timedelta(hours=1)
        time_fmt = '**{}** ({}) to {}'.format(time.strftime("%Y/%m/%d %H:%M"),
                                              minutes, plus_one.strftime("%Y/%m/%d %H:%M"))
    else:
        time_fmt = '**{}** ({})'.format(time.strftime("%Y/%m/%d %H:%M"), minutes)

    return ('**{}**\n- {} at {}\n- should spawn at {} in:\n{}'
            .format(boss, status, report_time.strftime("%Y/%m/%d %H:%M"), time_fmt, boss_map))
    # boss, status at, dead time, timefmt, maps with newlines

    return ret_message


async def check_databases():
    """
    :func:`check_databases` checks the database for entries roughly every minute.
    Records are output to the relevant Discord channels.
    """
    await bot.wait_until_ready()
    print('Startup completed; starting check_databases')

    await asyncio.sleep(1)

    print('Attempting to adjust user permissions...')

    for guild in bot.guilds:
        if not guild.unavailable:
            guild_id = str(guild.id)
            vdbs[guild.id] = vaivora.db.Database(guild_id)
            try:
                if not await vdbs[guild.id].update_user_sauth(
                        guild.owner.id, owner=True):
                    print('...failed! in {} with owner {}'
                          .format(guild.id, guild.owner.id))
                    raise Exception

                if guild.owner.id != secrets.discord_user_id:
                    if not await vdbs[guild.id].update_user_sauth(
                            secrets.discord_user_id, owner=False):
                        print('...failed! in {} with owner id {}'
                          .format(guild.id, guild.owner.id))
                        raise Exception

                print('Guild', guild.id, 'looks OK!')

                if await vdbs[guild.id].clean_duplicates():
                    print('Duplicates have been removed from tables from',
                          guild.id)
            except:
                print('Guild', guild.id, 'might be corrupt! Rebuilding and skipping...')
                await vdbs[guild.id].create_all(guild.owner.id)
                del vdbs[guild.id] # do not use corrupt/invalid db

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
                await valid_db.create_db(constants.main.ROLE_BOSS)
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

                record =  await process_record(current_boss,
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
            guild_boss_roles = await vdbs[vdb_id].get_users(
                                    constants.main.ROLE_BOSS)
            for boss_role in guild_boss_roles:
                try:
                    idx = [role.id for role in guild.roles].index(boss_role)
                    roles.append[guild.roles[idx].mention]
                except:
                    # user or group no longer exists
                    await vdbs[vdb_id].remove_users(
                            constants.main.ROLE_BOSS,
                            (boss_role,))

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
secret = secrets.discord_token

bot.loop.create_task(check_databases())
bot.run(secret)