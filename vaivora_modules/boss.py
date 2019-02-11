from datetime import datetime, timedelta
import re
import math
import asyncio
from importlib import import_module as im
import vaivora_modules
for mod in vaivora_modules.modules:
    im(mod)
from vaivora_modules.settings import channel_boss as channel_boss
from constants.boss import en_us as lang_boss
from constants.db import en_us as lang_db


def help():
    """
    :func:`help` returns help for this module.

    Returns:
        a list of detailed help messages
    """
    return lang_boss.HELP


async def what_status(entry):
    """
    :func:`what_status` checks what "status" the input may be.
    "Statuses" are defined to be "died" and "anchored".

    Args:
        entry (str): the string to check for "status"

    Returns:
        str: the correct "status" if successful
        None: if unsuccessful
    """
    if lang_boss.REGEX_STATUS_DIED.match(entry):
        return lang_boss.CMD_ARG_STATUS_DIED
    elif lang_boss.REGEX_STATUS_ANCHORED.match(entry):
        return lang_boss.CMD_ARG_STATUS_ANCHORED
    #elif lang_boss.REGEX_STATUS_WARNED.match(entry):
    #    return lang_boss.CMD_ARG_STATUS_WARNED
    else:
        return None


async def what_entry(entry):
    """
    :func:`what_entry` checks what "entry" the input may be.
    "Entries" are defined to be "maps" and "alias".

    Args:
        entry (str): the string to check for "query"

    Returns:
        str: the correct "entry" if successful
        None: if unsuccessful
    """
    if lang_boss.REGEX_ENTRY_LIST.search(entry):
        return lang_boss.CMD_ARG_ENTRY_LIST
    elif lang_boss.REGEX_ENTRY_ERASE.search(entry):
        return lang_boss.CMD_ARG_ENTRY_ERASE
    else:
        return None


async def what_query(entry):
    """
    :func:`what_query` checks what "query" the input may be.
    "Queries" are defined to be "maps" and "alias".

    Args:
        entry (str): the string to check for "query"

    Returns:
        str: the correct "query" if successful
        None: if unsuccessful
    """
    if lang_boss.REGEX_QUERY_MAPS.match(entry):
        return lang_boss.CMD_ARG_QUERY_MAPS
    elif lang_boss.REGEX_QUERY_ALIAS.match(entry):
        return lang_boss.CMD_ARG_QUERY_ALIAS
    else:
        return None


async def what_type(entry):
    """
    :func:`what_type` checks what "type" the input may be.
    "Types" are defined to be "world", "event", "field", and "demon".

    Args:
        entry (str): the string to check for "type"

    Returns:
        str: the correct "type" if successful
        None: if unsuccessful
    """
    if lang_boss.REGEX_TYPE_WORLD.search(entry):
        return lang_boss.KW_WORLD
    elif lang_boss.REGEX_TYPE_FIELD.search(entry):
        return lang_boss.KW_FIELD
    elif lang_boss.REGEX_TYPE_DEMON.search(entry):
        return lang_boss.KW_DEMON
    else:
        return None


async def check_boss(entry):
    """
    :func:`check_boss` checks whether an input string is a valid boss.

    Args:
        entry (str): the string to check for valid boss

    Returns:
        int: the boss index if valid and matching just one; otherwise, -1
    """
    match = None

    for boss in lang_boss.BOSS_SYNONYMS:
        for boss_syn in lang_boss.BOSS_SYNONYMS[boss]:
            if entry == boss_syn:
                return lang_boss.ALL_BOSSES.index(boss) # synonyms are unique and exact match only

    for boss in lang_boss.ALL_BOSSES:
        if re.search(entry, boss, re.IGNORECASE):
            if not match:
                match = boss
            else:
                return -1 # duplicate or too ambiguous

    if not match:
        return -1

    return lang_boss.ALL_BOSSES.index(match)


async def check_maps(boss_idx, maps):
    """
    :func:`check_maps` checks whether a string refers to a valid map.

    Args:
        boss_idx (int): the valid boss index to check
        maps (str): the string to check for valid map

    Returns:
        int: the map index if valid and matching just one; otherwise, -1
    """
    map_idx = -1
    map_floor = re.search('.*([0-9]).*', maps)
    boss = lang_boss.ALL_BOSSES[boss_idx]

    if map_floor:
        map_floor = map_floor.group(1)
        maps = re.sub(map_floor, '', maps).strip()

    for boss_map in lang_boss.BOSS_MAPS[boss]:
        if re.search(maps, boss_map, re.IGNORECASE):
            if map_floor and not re.search(map_floor, boss_map, re.IGNORECASE):
                continue # similar name; wrong number
            elif map_idx != -1: 
                return -1 # multiple matched; invalid
            else:
                map_idx = lang_boss.BOSS_MAPS[boss].index(boss_map)

    return map_idx


async def get_syns(boss):
    """
    :func:`get_syns` gets the synonyms of a valid boss.

    Args:
        boss (str): the string to get the boss's synonyms

    Returns:
        str: a formatted markdown message with synonyms
    """
    return ("**{}** can be called using the following aliases:\n\n- {}"
            .format(boss, '\n- '.join(lang_boss.BOSS_SYNONYMS[boss])))


async def get_maps(boss):
    """
    :func:`get_maps` gets the maps of a valid boss.

    Args:
        boss (str): the valid boss to get maps

    Returns:
        str: a formatted markdown message with maps for a boss
    """
    _maps = (lang_boss.GET_MAPS
             .format(boss, '\n- '.join(lang_boss.BOSS_MAPS[boss])))

    warps = lang_boss.NEAREST_WARPS[boss]
    if type(warps[0]) is not str:
        return (lang_boss.MAPAWAY_PLURAL
                .format(lang_boss.NEAREST_PLURAL.format(_maps),
                        warps[0][0], warps[0][1],
                        warps[1][0], warps[1][1]))
    else:
        return (lang_boss.MAPAWAY_SINGLE
                .format(lang_boss.NEAREST_SINGLE.format(_maps),
                        warps[0], warps[1]))


async def get_bosses(boss_type):
    """
    :func:`get_bosses` gets the bosses of a certain boss type.

    Args:
        boss_type (str): the type of the boss

    Returns:
        str: a formatted markdown message with bosses of the specified type
    """
    return (lang_boss.GET_BOSSES
            .format(boss_type, '\n- '.join(lang_boss.BOSSES[boss_type])))


def get_offset(boss, status, coefficient=1):
    """
    :func:`get_offset` returns the timedelta offset for a given boss.

    Args:
        boss (str): the name of the boss
        status (str): the status code for the boss
        coefficient (int): either 1 or -1 to use for calculating offset

    Returns:
        timedelta: an appropriate timedelta
    """
    # ignore status for all bosses except world bosses
    if boss in lang_boss.BOSSES[lang_boss.KW_DEMON]:
        return timedelta(minutes=(coefficient * lang_boss.TIME_STATUS_DEMON))
    elif boss in lang_boss.BOSSES[lang_boss.KW_FIELD]:
        return timedelta(minutes=(coefficient * lang_boss.TIME_STATUS_FIELD))
    elif boss == lang_boss.BOSS_W_ABOMINATION:
        return timedelta(minutes=(coefficient * lang_boss.TIME_STATUS_ABOM))
    else:
        return timedelta(minutes=(coefficient * lang_boss.TIME_STATUS_WB))
    # else:
    #     return timedelta(minutes=(coefficient * lang_boss.TIME_STATUS_ANCHORED))


async def validate_time(time):
    """
    :func:`validate_time` validates whether a string representing time is valid or not, returning a standardized one.

    Args:
        time (str): the time str to check

    Returns:
        str: a standardized time unit, e.g. 0:00 (midnight) or 13:00 (1 PM); or None if invalid
    """
    if not lang_boss.REGEX_TIME.match(time):
        return None

    offset = 0

    # e.g. 900 (or 9:00)
    if lang_boss.REGEX_TIME_DIGITS.match(time):
        minutes = lang_boss.REGEX_TIME_MINUTES.match(time).group(1)
        hours = re.sub(minutes, '', time)
        return lang_boss.TIME.format(hours, minutes)
    # e.g. 12:00 am (or 0:00)
    elif lang_boss.REGEX_TIME_AMPM.search(time):
        if lang_boss.REGEX_TIME_PM.search(time):
            if lang_boss.REGEX_TIME_NOON.match(time):
                offset -= 12
            offset += 12
        else:
            if lang_boss.REGEX_TIME_NOON.match(time):
                offset -= 12

    delim = lang_boss.REGEX_TIME_DELIM.search(time)
    hours, minutes = [int(t) for t in time.split(delim.group(0))]
    hours += offset

    if hours >= 24 or hours < 0:
        return None

    return lang_boss.TIME.format(str(hours).rjust(2, '0'),
                                 str(minutes).rjust(2, '0'))


async def process_cmd_status(server_id, msg_channel, boss, status, time, options):
    """
    :func:`process_cmd_status` processes a specific boss command: status related to recording.

    Args:
        server_id (int): the id of the server of the originating message
        msg_channel: the id of the channel of the originating message (belonging to server of `server_id`)
        boss (str): the boss in question
        status (str): the boss's status, or the status command
        time (str): time represented for the associated event
        options (dict): a dict containing optional parameters with possible default values

    Returns:
        str: an appropriate message for success or fail of command, e.g. boss data recorded
    """
    offset = 0
    target = {}

    if (boss not in lang_boss.BOSSES[lang_boss.KW_WORLD] and
        status == lang_boss.CMD_ARG_STATUS_ANCHORED):
        return lang_boss.FAIL_TEMPLATE.format(lang_boss.FAIL_STATUS_NO_ANCHOR, lang_boss.MSG_HELP)

    target[lang_db.COL_BOSS_NAME] = boss
    target[lang_db.COL_BOSS_TXT_CHANNEL] = msg_channel
    target[lang_db.COL_BOSS_CHANNEL] = options[lang_db.COL_BOSS_CHANNEL]
    target[lang_db.COL_BOSS_MAP] = options[lang_db.COL_BOSS_MAP]
    target[lang_db.COL_BOSS_STATUS] = status

    time_offset = get_offset(boss, status)

    hours, minutes = [int(t) for t in time.split(':')]

    record = {}

    server_date = datetime.now() + timedelta(hours=lang_boss.TIME_H_LOCAL_TO_SERVER)

    if hours > int(server_date.hour):
        # adjust to one day before, e.g. record on 23:59, July 31st but recorded on August 1st
        server_date += timedelta(days=-1)

    # dates handled like above example, e.g. record on 23:59, December 31st but recorded on New Years Day
    record[lang_db.COL_TIME_YEAR] = int(server_date.year)
    record[lang_db.COL_TIME_MONTH] = int(server_date.month)
    record[lang_db.COL_TIME_DAY] = int(server_date.day)
    record[lang_db.COL_TIME_HOUR] = hours
    record[lang_db.COL_TIME_MINUTE] = minutes

    # reconstruct boss kill time
    record_date = datetime(*record.values())
    record_date += time_offset

    # reassign to target data
    target[lang_db.COL_TIME_YEAR] = int(record_date.year)
    target[lang_db.COL_TIME_MONTH] = int(record_date.month)
    target[lang_db.COL_TIME_DAY] = int(record_date.day)
    target[lang_db.COL_TIME_HOUR] = int(record_date.hour)
    target[lang_db.COL_TIME_MINUTE] = int(record_date.minute)

    vdb = vaivora_modules.db.Database(server_id)
    await vdb.check_if_valid()

    if await vdb.update_db_boss(target):
        return (lang_boss.SUCCESS_STATUS.format(lang_boss.ACKNOWLEDGED,
                                                boss, status, time,
                                                lang_boss.EMOJI_LOC,
                                                options[lang_db.COL_BOSS_MAP],
                                                options[lang_db.COL_BOSS_CHANNEL]))
    else:
        return lang_boss.FAIL_TEMPLATE.format(lang_boss.FAIL_STATUS, lang_boss.MSG_HELP)


async def process_cmd_entry(server_id: int, msg_channel, bosses, entry, channel=None):
    """
    :func:`process_cmd_entry` processes a specific boss command: entry to retrieve records.

    Args:
        server_id (int): the id of the server of the originating message
        msg_channel: the id of the channel of the originating message (belonging to server of `server_id`)
        bosses (list): a list of bosses to check
        entry (str): the entry command (list, erase)
        channel: (default: None) the channel for the record

    Returns:
        str: an appropriate message for success or fail of command, e.g. confirmation or list of entries
    """
    if type(bosses) is str:
        bosses = [bosses]

    vdb = vaivora_modules.db.Database(server_id)
    if not await vdb.check_if_valid():
        await vdb.create_db()

    # $boss <target> erase ...
    if entry == lang_boss.CMD_ARG_ENTRY_ERASE:
        if channel and bosses in lang_boss.BOSSES[lang_boss.KW_WORLD]:
            records = await vdb.rm_entry_db_boss(boss_list=bosses, boss_ch=channel)
        else:
            records = await vdb.rm_entry_db_boss(boss_list=bosses)

        if records:
            records = '\n'.join(['**{}**'.format(rec) for rec in records])
            return ['{}{}'.format(lang_boss.SUCCESS_ENTRY_ERASE_ALL.format(len(records)),
                                  '\n\n{}'.format(records)),]
        else:
            return [lang_boss.FAIL_ENTRY_ERASE,]
    # $boss <target> list ...
    else:
        valid_boss_records = []
        valid_boss_records.append("Records:")
        boss_records = await vdb.check_db_boss(bosses=bosses) # possible return

        if not boss_records: # empty
            return [lang_boss.FAIL_ENTRY_LIST,]

        for boss_record in boss_records:
            boss_name = boss_record[0]
            boss_channel = str(math.floor(boss_record[1]))
            boss_prev_map = boss_record[2]
            boss_status = boss_record[3]

            # year, month, day, hour, minutes
            record_date = datetime(*[int(rec) for rec in boss_record[5:10]])
            
            time_diff = (datetime.now()
                         + timedelta(hours=lang_boss.TIME_H_LOCAL_TO_SERVER)
                         - record_date)

            if int(time_diff.days) >= 0 and boss_status != lang_boss.CMD_ARG_STATUS_ANCHORED:
                spawn_msg = lang_boss.TIME_SPAWN_MISSED
                minutes = math.floor(time_diff.seconds/60) + int(time_diff.days)*86400

            # anchored
            elif boss_status == lang_boss.CMD_ARG_STATUS_ANCHORED:
                spawn_msg = lang_boss.TIME_SPAWN_EARLY
                if int(time_diff.days) < 0:
                    minutes = math.floor((86400-int(time_diff.seconds))/60)
                else:
                    minutes = math.floor(time_diff.seconds/60) + int(time_diff.days)*86400

            else: #elif boss_status == lang_boss.CMD_ARG_STATUS_DIED:
                spawn_msg = lang_boss.TIME_SPAWN_ONTIME
                minutes = math.floor((86400-int(time_diff.seconds))/60)

            # absolute date and time for spawn
            # e.g. 2017/07/06 "14:47"
            spawn_time = record_date.strftime("%Y/%m/%d %H:%M")

            if minutes < 0:
                minutes = abs(int(time_diff.days))*86400 + minutes

            # print day or days conditionally
            msg_days = None
            
            if int(time_diff.days) > 1:
                msg_days = '{} days'.format(str(time_diff.days))
            elif int(time_diff.days) == 1:
                msg_days = '1 day'

            # print hour or hours conditionally
            msg_hours = None

            if minutes > 119:
                msg_hours = '{} hours'.format(str(math.floor((minutes % 86400)/60)))
            elif minutes > 59:
                msg_hours = '1 hour'

            # print minutes unconditionally
            # e.g.              0 minutes from now
            # e.g.              59 minutes ago
            msg_minutes = '{} minutes'.format(str(math.floor(minutes % 60)))
            msg_when = 'from now' if int(time_diff.days) < 0 else "ago"

            if msg_days is None and msg_hours is None:
                msg_time = '{} {}'.format(msg_minutes, msg_when)
            elif msg_days is None:
                msg_time = '{}, {} {}'.format(msg_hours, msg_minutes, msg_when)
            elif msg_hours is None:
                msg_time = '{}, {} {}'.format(msg_days, msg_minutes, msg_when)
            else:
                msg_time = '{}, {}, {} {}'.format(msg_days, msg_hours, msg_minutes, msg_when)

            # print extra anchored message conditionally
            if boss_status == lang_boss.CMD_ARG_STATUS_ANCHORED:
                msg_time = '{} {}'.format(msg_time, 'and as late as one hour later')

            last_map = 'last known map: {} {}'.format(lang_boss.EMOJI_LOC, boss_prev_map)

            message = ('**{}**\n- {} **{}** ({})\n- {} CH {}'
                       .format(boss_name, spawn_msg, spawn_time,
                               msg_time, last_map, boss_channel))

            valid_boss_records.append(message)

        #valid_boss_records.append("```\n")
        return valid_boss_records #'\n'.join(valid_boss_records)


async def process_cmd_query(boss, query):
    """
    :func:`process_cmd_query` processes a query relating to bosses.

    Args:
        boss (str): the boss to query
        query (str): the query (synonyms, maps)

    Returns:
        str: an appropriate message for success or fail of command, i.e. maps or aliases
    """
    # $boss <target> syns
    if query == lang_boss.CMD_ARG_QUERY_ALIAS:
        return await get_syns(boss)
    # $boss <target> maps
    else:
        return await get_maps(boss)


def process_cmd_opt(boss, option=None):
    """
    :func:`process_cmd_opt` processes optional arguments.

    Args:
        boss (str): the boss related to the option
        option (str): (default: None) an optional argument to process

    Returns:
        dict: a k:v of 'map' and 'channel': 'map' is str; 'channel' is int
    """
    target = {}

    # initialize to default values: channel = 1; map = 'N/A'
    target[lang_db.COL_BOSS_CHANNEL] = 1
    target[lang_db.COL_BOSS_MAP] = lang_boss.CMD_ARG_QUERY_MAPS_NOT

    if option is None:
        if boss in (lang_boss.BOSSES[lang_boss.KW_WORLD]
                    +lang_boss.BOSSES[lang_boss.KW_FIELD]):
            target[lang_db.COL_BOSS_MAP] = lang_boss.BOSS_MAPS[boss][0]
        return target

    channel = lang_boss.REGEX_OPT_CHANNEL.match(option)

    # world boss; discard map argument if found and return
    if channel and boss in lang_boss.BOSSES[lang_boss.KW_WORLD]:
        target[lang_db.COL_BOSS_CHANNEL] = int(channel.group(2))
        target[lang_db.COL_BOSS_MAP] = lang_db.BOSS_MAPS[boss]
    # field boss + Demon Lords; discard channel argument nonetheless
    elif not channel and (boss in lang_boss.BOSSES[lang_boss.KW_FIELD] or
                          boss in lang_boss.BOSSES[lang_boss.KW_DEMON]):
        map_idx = check_maps(boss, option)
        if map_idx >= 0 and map_idx < len(lang_boss.BOSS_MAPS[boss]):
            target[lang_db.COL_BOSS_MAP] = lang_boss.BOSS_MAPS[boss][map_idx]

    return target


def process_record(boss, status, time, boss_map, channel):
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
    channel = str(math.floor(float(channel)))

    if boss_map == lang_boss.CMD_ARG_QUERY_MAPS_NOT:
        # use all maps for Demon Lord if not previously known
        if boss in lang_boss.BOSSES[lang_boss.KW_DEMON]:
            boss_map = '\n'.join([lang_boss.RECORD.format(lang_boss.EMOJI_LOC,
                                                          loc, channel)
                                  for loc in lang_boss.BOSS_MAPS[boss]])
        # this should technically not be possible
        else:
            boss_map = lang_boss.RECORD.format(lang_boss.EMOJI_LOC, lang_boss.BOSS_MAPS[boss], channel)
    # use all other maps for Demon Lord if already known
    elif boss in lang_boss.BOSSES[lang_boss.KW_DEMON]:
        boss_map = '\n'.join(['{} {}'.format(lang_boss.EMOJI_LOC, loc)
                              for loc in lang_boss.BOSS_MAPS[boss] if loc != boss_map])
    elif boss == lang_boss.BOSS_W_KUBAS:
        # valid while Crystal Mine Lot 2 - 2F has 2 channels
        channel = str(int(channel) % 2 + 1)
        boss_map = lang_boss.RECORD_KUBAS.format(lang_boss.EMOJI_LOC, boss_map, channel)
    else:
        boss_map = lang_boss.RECORD.format(lang_boss.EMOJI_LOC, boss_map, channel)
        

    minutes = math.floor((time - (datetime.now() 
                                  + timedelta(hours=lang_boss.TIME_H_LOCAL_TO_SERVER)))
                        .seconds / 60)
    minutes = '{} minutes'.format(str(minutes))

    # set time difference based on status and type of boss
    # takes the negative (additive complement) to get the original time
    time_diff = get_offset(boss, status, coefficient=-1)
    # and add it back to get the reported time
    report_time = time + time_diff

    if status == lang_boss.CMD_ARG_STATUS_ANCHORED:
        plus_one = time + timedelta(hours=1)
        time_fmt = '**{}** ({}) to {}'.format(time.strftime("%Y/%m/%d %H:%M"),
                                              minutes, plus_one.strftime("%Y/%m/%d %H:%M"))
    else:
        time_fmt = '**{}** ({})'.format(time.strftime("%Y/%m/%d %H:%M"), minutes)

    return ('**{}**\n- {} at {}\n- should spawn at {} in:\n{}'
            .format(boss, status, report_time.strftime("%Y/%m/%d %H:%M"), time_fmt, boss_map))
    # boss, status at, dead time, timefmt, maps with newlines

    return ret_message

