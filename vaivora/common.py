import asyncio
import logging
import re
from datetime import timedelta
from hashlib import blake2b
from inspect import cleandoc
from itertools import zip_longest
from math import floor

import discord
import pendulum
import yaml

import vaivora.db


default_tz = 'America/New_York'

regex_nonalnum = re.compile(
    f'[^a-z0-9 -]',
    re.IGNORECASE
    )
regex_time = re.compile(
    r'[0-2]?[0-9][:.]?[0-5][0-9] ?([ap]m?)*',
    re.IGNORECASE
    )
regex_noon = re.compile(
    r'^12.*',
    re.IGNORECASE
    )
regex_ampm = re.compile(
    r'[ap]m?',
    re.IGNORECASE
    )
regex_pm = re.compile(
    r'pm?',
    re.IGNORECASE
    )
regex_delim = re.compile(r'[:.]')
regex_digits = re.compile(r'^[0-9]{3,4}$')
regex_minutes = re.compile(r'.*([0-9]{2})$')

logger = logging.getLogger('vaivora.vaivora.common')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('vaivora.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

try:
    with open('emoji.yaml', 'r') as f:
        location_emoji = yaml.safe_load(f)['location']
except FileNotFoundError:
    # Fallback on default
    with open('emoji.yaml.example', 'r') as f:
        location_emoji = yaml.safe_load(f)['location']

with open('boss.yaml', 'r') as f:
    boss_conf = yaml.safe_load(f)


async def process_boss_record(boss: str, status: str, time, diff: timedelta,
    boss_map: str, channel: int, guild_id: int):
    """Processes a boss record to print out.

    Args:
        boss (str): the boss in question
        status (str): the status of the boss
        time (pendulum.datetime): the `datetime` of the target
            set to its next approximate spawn
        diff (timedelta): the difference in time from server to local
        boss_map (str): the map containing the last recorded spawn
        channel (int): the channel of the world boss if applicable; else, 1
        guild_id (int): the guild's id

    Returns:
        str: a formatted message containing the records

    """
    if boss_map == 'N/A':
        # If previous map isn't known, just list all possible spawn maps
        map_fmt = '\n'.join(
            [
                f"""{location_emoji} {loc} CH {channel}"""
                for loc in boss_conf['maps'][boss]
                ]
            )
    elif boss in boss_conf['bosses']['demon']:
        map_fmt = '\n'.join(
            [
                f"""{location_emoji} {loc} CH {channel})"""
                for loc in boss_conf['maps'][boss]
                if loc != boss_map
                ]
            )
    elif boss == 'Kubas Event':
        # valid while Crystal Mine Lot 2 - 2F has 2 channels
        channel = str(int(channel) % 2 + 1)
        map_fmt = (
            f"""{location_emoji} {boss_map}; """
            f"""Machine of Riddles CH {channel}"""
            )
    else:
        map_fmt = (
            f"""{location_emoji} {boss_map} CH {channel}"""
            )

    minutes = floor(diff.seconds / 60)

    # Calculate the original reported time from spawn time
    # to use in message
    time_diff = await get_boss_offset(boss, status, coefficient=-1)
    report_time = time + time_diff

    time_fmt = f'**{time.strftime("%Y/%m/%d %H:%M")}** ({minutes} minutes)'

    if status == 'anchored':
        plus_one = time + timedelta(hours=1)
        time_fmt = f'{time_fmt} to {plus_one.strftime("%Y/%m/%d %H:%M")}'

    return cleandoc(
        f"""**{boss}**
        - {status} at {report_time.strftime("%Y/%m/%d %H:%M")}
        - should spawn at **{time_fmt} in:
        {map_fmt}
        """
        )


async def get_time_diff(guild_id):
    """Retrieves the time difference between local and `server_tz`,
    to process the time difference.

    Args:
        guild_id (int): the guild id, of course

    Returns:
        tuple of int: (hours, minutes)

    """
    vdb = vaivora.db.Database(guild_id)

    tz = await vdb.get_tz()
    if not tz:
        tz = default_tz

    offset = await vdb.get_offset()
    if not offset:
        offset = 0

    try:
        local_time = pendulum.today()
        server_time = local_time.in_timezone(tz=tz)
        days = server_time.day - local_time.day
        hours = server_time.hour - local_time.hour
        minutes = server_time.minute - local_time.minute
        # The greatest day difference will always be 2:
        # e.g. compare the time difference between
        # 'Pacific/Kiritimati' (UTC+14) and 'Pacific/Pago_Pago' (UTC-11)
        # A new day starting in the former will be 2 calendar days ahead.
        if abs(days) > 2 or days >= 1:
            hours += days_diff * 24

        return (hours + offset, minutes)
    except:
        return (0, 0)


async def get_tz(guild_id):
    """Gets the guild (per `guild_id`) time zone.

    Args:
        guild_id (int): the guild id, of course

    Returns:
        str: a tz str

    """
    vdb = vaivora.db.Database(guild_id)

    tz = await vdb.get_tz()
    if not tz:
        tz = default_tz

    return tz


async def validate_time(time):
    """Validates whether a string representing time is valid,
    returning a standardized one.

    Args:
        time (str): the time str to check

    Returns:
        str: a standardized time unit, e.g. 0:00 (midnight) or 13:00 (1 PM)
        bool: False, if invalid

    """
    if not regex_time.match(time):
        return False

    offset = 0

    # Search and process time strings with no delimeter, with 3 or 4 digits
    if regex_digits.match(time):
        minutes = regex_minutes.match(time).group(1)
        hours = re.sub(minutes, '', time)
        return f"""{hours.rjust(2, '0')}:{minutes}"""
    # Search and process time strings with AM/PM
    elif regex_ampm.search(time):
        if regex_pm.search(time):
            # e.g. 12:00 PM -> 0:00 PM -> 12:00
            if regex_noon.match(time):
                offset -= 12
            # e.g. 1:00 PM -> 13:00
            offset += 12
        else:
            # e.g. 12.00 AM -> 0:00 AM -> 0:00
            if regex_noon.match(time):
                offset -= 12
        time = regex_ampm.sub('', time)

    delim = regex_delim.search(time)
    hours, minutes = [int(t) for t in time.split(delim.group(0))]
    hours += offset

    if hours >= 24 or hours < 0:
        return False

    return f"""{hours.rjust(2, '0')}:{minutes.rjust(2, '0')}"""


async def validate_date(date):
    """Validates whether a string representing date is valid,
    returning a standardized one.

    Args:
        date (str): the date str to check

    Returns:
        dict: of ints (year, month, day)
        bool: False, if invalid

    """
    delims = ['.', '/', '-']
    for delim in delims:
        split_date = date.split(delim)
        if len(split_date) != 3:
            continue
        else:
            date_list = [int(d) for d in split_date]
            end = pendulum.datetime(*date_list)
            now = pendulum.now()
            time_diff = end - now
            # Reject events that have already ended
            if time_diff.seconds <= 0:
                return False
            else:
                return {
                    'year': date_list[0],
                    'month': date_list[1],
                    'day': date_list[2]
                    }
    # Nothing was validated
    return False


async def sanitize_nonalnum(text: str):
    """Removes all non-alphanumeric characters.

    Spaces and hyphens are valid.

    Args:
        text (str): the text to sanitize

    Returns:
        str: a sanitized string

    """
    return regex_nonalnum.sub('', text)


async def get_boss_offset(boss: str, status: str, coefficient: int = 1):
    """Gets the timedelta offset for a given boss.

    Args:
        boss (str): the name of the boss
        status (str): the status code for the boss
        coefficient (int): either 1 or -1 depending on
            - 1: calculating the spawn time
            - -1: recreating kill time

    Returns:
        datetime.timedelta: an appropriate timedelta

    """
    if boss == 'Abominaton' or boss == 'Dullahan Event':
        minutes = boss_conf['spawns']['short']
    if boss in boss_conf['bosses']['demon']:
        minutes = boss_conf['spawns']['demon']
    elif boss in boss_conf['bosses']['field']:
        minutes = boss_conf['spawns']['field']
    else:
        minutes = boss_conf['spawns']['world']

    return timedelta(minutes = (coefficient * minutes))


async def hash_object(channel_id: str, obj: str, time: str,
    etc: str = None):
    """Hashes an object to use in the background loop of
    `bot.py`.

    Args:
        channel_id (str): the Discord channel id, as a str
        object (str): the object to hash
        time (str): the time associated with the object
        etc (str, optional): any extra characteristics to use;
            defaults to None

    Returns:
        str: a hashed string representing the unique record

    """
    record = bytearray(f'{channel_id}:{obj}:{time}:{etc}', 'utf-8')
    hashed = blake2b(digest_size=48)
    hashed.update(record)
    return hashed.hexdigest()


async def chunk_messages(iterable, n: int, fillvalue = None, newlines: int = 2):
    """Takes an `iterable` and combines `n` elements to form chunks.
    The chunks are then used to output in a clean way, without
    the need for an accumulator, buffer, or counter.

    Adapted from Python `itertools` recipes "grouper".

    Args:
        iterable: the iterable to make into chunks
        n (int): number of elements per chunk
        fillvalue (optional): the character to pad the last chunk if not full;
            defaults to None
        newlines (int, optional): number of newlines to join between the
            chunks; defaults to 2

    Returns:
        list: of strings

    """
    joins = '\n' * newlines
    args = [iter(iterable)] * n
    messages = []
    for zipped in zip_longest(*args, fillvalue=fillvalue):
        fillcount = zipped.count(fillvalue)
        messages.append(
            joins.join(
                zipped[:-fillcount]
                if fillcount > 0
                else zipped
                )
            )
    return messages


async def send_messages(guild: discord.Guild, messages: list, role: str):
    """Sends messages compiled by the background loop.

    Args:
        guild (discord.Guild): the Discord guild
        messages (list of dict): messages to send, in a structure:
            - 'record': the actual content
            - 'discord_channel': the Discord channel to send to
        role (str): either 'boss' or 'events'

    Returns:
        bool: True if run successfully regardless of result

    """
    channels_in = {}
    discord_roles = await get_roles(guild, role)

    channels = [
        int(message['discord_channel'])
        for message
        in messages
        ]

    for channel in channels:
        can_send = True
        # Before attempting to send messages, make sure to
        # check it can receive messages
        try:
            guild_channel = guild.get_channel(channel)
            guild_channel.name
        except AttributeError as e:
            # remove invalid channel
            logger.error(
                f'Caught {e} in vaivora.common: send_messages; '
                f'guild: {guild.id}; '
                f'channel: {channel}'
                )
            await vaivora.db.Database(guild.id).remove_channel(
                role,
                channel
                )
            continue
        except Exception as e:
            # can't retrieve channel definitively; abort
            logger.error(
                f'Caught {e} in vaivora.common: send_messages; '
                f'guild: {guild.id}; '
                f'channel: {channel}'
                )
            continue

        messages_in_channel = [
            message['record']
            for message
            in messages
            if int(message['discord_channel']) == channel
            ]

        if not messages_in_channel:
            continue

        discord_channel = guild.get_channel(channel)

        if role == 'boss':
            await discord_channel.send(
                cleandoc(
                    f"""{discord_roles}

                    The following bosses will spawn within 15 minutes:
                    """
                    )
                )
        else:
            await discord_channel.send(
                cleandoc(
                    f"""{discord_roles}

                    The following events will conclude within 60 minutes:
                    """
                    )
                )

        for message in await chunk_messages(
            messages_in_channel, 8, newlines=1
            ):
            await asyncio.sleep(1)
            try:
                await discord_channel.send(message)
            except Exception as e:
                logger.error(
                    f'Caught {e} in vaivora.common: send_messages; '
                    f'guild: {guild.id}; '
                    f'channel: {channel}'
                    )
                break

    return True


async def get_roles(guild: discord.Guild, role: str):
    """Gets roles from a guild.

    Invalid roles will be purged during this process.

    Args:
        guild (discord.Guild): the Discord guild
        role (str): the Vaivora role to get

    Returns:
        str: a space delimited string of mentionable roles

    """
    mentionable = []
    invalid = []
    guild_db = vaivora.db.Database(guild.id)
    role_ids = await guild_db.get_users(role)
    for role_id in role_ids:
        try:
            idx = [
                role.id
                for role
                in guild.roles
                ].index(role_id)
            mentionable.append(guild.roles[idx].mention)
        except ValueError as e:
            # Discord role no longer exists; mark as invalid
            logger.error(
                f'Caught {e} in vaivora.common: get_roles; '
                f'guild: {guild.id}'
                )
            invalid.append(role_id)

    if invalid:
        await guild_db.remove_users(
            role,
            invalid
            )

    return ' '.join(mentionable)
