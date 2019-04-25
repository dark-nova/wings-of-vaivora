import asyncio
import re
from datetime import timedelta
from math import floor
from hashlib import blake2b

import pendulum

import constants.boss
import vaivora.db


nonalnum = re.compile('[^A-Za-z0-9 -]')


async def process_record(boss: str, status: str, time, diff: timedelta,
    boss_map: str, channel: int, guild_id: int):
    """Processes a record to print out.

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
    if boss_map == constants.boss.CMD_ARG_QUERY_MAPS_NOT:
        # use all maps for Demon Lord if not previously known
        if boss in constants.boss.BOSSES[constants.boss.KW_DEMON]:
            boss_map = '\n'.join([constants.boss.RECORD
                                  .format(constants.boss.EMOJI_LOC,
                                          loc, channel)
                                  for loc in constants.boss.BOSS_MAPS[boss]])
        # this should technically not be possible
        else:
            boss_map = (constants.boss.RECORD
                        .format(constants.boss.EMOJI_LOC,
                                constants.boss.BOSS_MAPS[boss], channel))
    # use all other maps for Demon Lord if already known
    elif boss in constants.boss.BOSSES[constants.boss.KW_DEMON]:
        boss_map = '\n'.join(['{} {}'.format(constants.boss.EMOJI_LOC, loc)
                              for loc in constants.boss.BOSS_MAPS[boss]
                              if loc != boss_map])
    elif boss == constants.boss.BOSS_W_KUBAS:
        # valid while Crystal Mine Lot 2 - 2F has 2 channels
        channel = str(int(channel) % 2 + 1)
        boss_map = (constants.boss.RECORD_KUBAS
                    .format(constants.boss.EMOJI_LOC, boss_map, channel))
    else:
        boss_map = (constants.boss.RECORD
                    .format(constants.boss.EMOJI_LOC, boss_map, channel))

    local = pendulum.now()

    minutes = floor(diff.seconds / 60)
    minutes = '{} minutes'.format(str(minutes))

    # set time difference based on status and type of boss
    # takes the negative (additive complement) to get the original time
    time_diff = await get_boss_offset(boss, status, coefficient=-1)
    # and add it back to get the reported time
    report_time = time + time_diff

    if status == constants.boss.CMD_ARG_STATUS_ANCHORED:
        plus_one = time + timedelta(hours=1)
        time_fmt = '**{}** ({}) to {}'.format(time.strftime("%Y/%m/%d %H:%M"),
                                              minutes, plus_one.strftime("%Y/%m/%d %H:%M"))
    else:
        time_fmt = '**{}** ({})'.format(time.strftime("%Y/%m/%d %H:%M"), minutes)

    return ('**{}**\n- {} at {}\n- should spawn at {} in:\n{}\n\n'
            .format(boss, status, report_time.strftime("%Y/%m/%d %H:%M"), time_fmt, boss_map))


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
        tz = constants.offset.DEFAULT

    offset = await vdb.get_offset()
    if not offset:
        offset = 0

    try:
        local_time = pendulum.today()
        server_time = local_time.in_timezone(tz=tz)
        day_diff = server_time.day - local_time.day
        hours = server_time.hour - local_time.hour
        minutes = server_time.minute - local_time.minute
        # The greatest day difference will always be 2:
        # e.g. compare the time difference between
        # 'Pacific/Kiritimati' (UTC+14) and 'Pacific/Pago_Pago' (UTC-11)
        # A new day starting in the former will be 2 calendar days ahead.
        if abs(day_diff) > 2 or day_diff >= 1:
            hours += days_diff * 24

        return (hours + offset, minutes)
    except:
        return (0, 0)


    

    


async def validate_time(time):
    """Validates whether a string representing time is valid,
    returning a standardized one.

    Args:
        time (str): the time str to check

    Returns:
        str: a standardized time unit, e.g. 0:00 (midnight) or 13:00 (1 PM)
        None: if invalid

    """
    if not constants.boss.REGEX_TIME.match(time):
        return None

    offset = 0

    # e.g. 900 (or 9:00)
    if constants.boss.REGEX_TIME_DIGITS.match(time):
        minutes = constants.boss.REGEX_TIME_MINUTES.match(time).group(1)
        hours = re.sub(minutes, '', time)
        return constants.boss.TIME.format(hours, minutes)
    # e.g. 12:00 am (or 0:00)
    elif constants.boss.REGEX_TIME_AMPM.search(time):
        if constants.boss.REGEX_TIME_PM.search(time):
            if constants.boss.REGEX_TIME_NOON.match(time):
                offset -= 12
            offset += 12
        else:
            if constants.boss.REGEX_TIME_NOON.match(time):
                offset -= 12
        time = constants.boss.REGEX_TIME_AMPM.sub('', time)

    delim = constants.boss.REGEX_TIME_DELIM.search(time)
    hours, minutes = [int(t) for t in time.split(delim.group(0))]
    hours += offset

    if hours >= 24 or hours < 0:
        return None

    return constants.boss.TIME.format(str(hours).rjust(2, '0'),
                                      str(minutes).rjust(2, '0'))


async def validate_date(date):
    """Validates whether a string representing date is valid,
    returning a standardized one.

    Args:
        date (str): the date str to check

    Returns:
        dict: of ints (year, month, day)
        None: if invalid

    """
    delims = ['.', '/', '-']
    for delim in delims:
        split_date = date.split(delim)
        if len(split_date) != 3:
            continue
        else:
            date_list = [int(_d) for _d in split_date]
            end = pendulum.datetime(*date_list)
            now = pendulum.now()
            time_diff = now - end
            # reject events that have already ended
            if time_diff.seconds <= 0:
                return None
            else:
                return {
                    'year': date_list[0],
                    'month': date_list[1],
                    'day': date_list[2]
                    }

    # nothing was validated
    return None


async def sanitize_nonalnum(text: str):
    """Removes all non-alphanumeric characters.

    Spaces and hyphens are valid.

    Args:
        text (str): the text to sanitize

    Returns:
        str: a sanitized string

    """
    return nonalnum.sub('', text)


async def get_boss_offset(boss: str, status: str, coefficient: int=1):
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
    if boss in constants.boss.BOSSES[constants.boss.KW_DEMON]:
        multiplier = constants.boss.TIME_STATUS_DEMON
    elif boss in constants.boss.BOSSES[constants.boss.KW_FIELD]:
        multiplier = constants.boss.TIME_STATUS_FIELD
    elif boss == constants.boss.BOSS_W_ABOMINATION:
        multiplier = constants.boss.TIME_STATUS_ABOM
    else:
        multiplier = constants.boss.TIME_STATUS_WB

    return timedelta(minutes=(coefficient * multiplier))


async def hash_object(channel_id: str, obj: str, time: str,
    etc: str=None):
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
    record = "{}:{}:{}:{}".format(
        channel_id,
        obj,
        time,
        etc
        )

    record = bytearray(record, 'utf-8')
    hashedblake = blake2b(digest_size=48)
    hashedblake.update(record)
    return hashedblake.hexdigest()
