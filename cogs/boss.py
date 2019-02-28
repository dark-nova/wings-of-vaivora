import re
import asyncio
from math import floor
from datetime import datetime, timedelta

import discord
from discord.ext import commands

import checks
import vaivora.db
import constants.boss


def help():
    """
    :func:`help` returns help for this module.

    Returns:
        a list of detailed help messages
    """
    return constants.boss.HELP


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

        boss_idx = await check_boss(boss)

        if boss_idx == -1: # invalid boss
            return (None,)

        time = await validate_time(time)

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
            map_idx = await check_maps(boss_idx, map_or_channel)

        if (not map_idx and map_idx != 0) or map_idx == -1:
            _map = ""
        else:
            _map = constants.boss.BOSS_MAPS[boss][map_idx]

        return (boss, time, _map, channel)


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
    if constants.boss.REGEX_STATUS_DIED.match(entry):
        return constants.boss.CMD_ARG_STATUS_DIED
    elif constants.boss.REGEX_STATUS_ANCHORED.match(entry):
        return constants.boss.CMD_ARG_STATUS_ANCHORED
    #elif constants.boss.REGEX_STATUS_WARNED.match(entry):
    #    return constants.boss.CMD_ARG_STATUS_WARNED
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
    if constants.boss.REGEX_ENTRY_LIST.search(entry):
        return constants.boss.CMD_ARG_ENTRY_LIST
    elif constants.boss.REGEX_ENTRY_ERASE.search(entry):
        return constants.boss.CMD_ARG_ENTRY_ERASE
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
    if constants.boss.REGEX_QUERY_MAPS.match(entry):
        return constants.boss.CMD_ARG_QUERY_MAPS
    elif constants.boss.REGEX_QUERY_ALIAS.match(entry):
        return constants.boss.CMD_ARG_QUERY_ALIAS
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
    if constants.boss.REGEX_TYPE_WORLD.search(entry):
        return constants.boss.KW_WORLD
    elif constants.boss.REGEX_TYPE_FIELD.search(entry):
        return constants.boss.KW_FIELD
    elif constants.boss.REGEX_TYPE_DEMON.search(entry):
        return constants.boss.KW_DEMON
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

    for boss in constants.boss.BOSS_SYNONYMS:
        for boss_syn in constants.boss.BOSS_SYNONYMS[boss]:
            if entry == boss_syn:
                return constants.boss.ALL_BOSSES.index(boss) # synonyms are unique and exact match only

    for boss in constants.boss.ALL_BOSSES:
        if re.search(entry, boss, re.IGNORECASE):
            if not match:
                match = boss
            else:
                return -1 # duplicate or too ambiguous

    if not match:
        return -1

    return constants.boss.ALL_BOSSES.index(match)


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
    boss = constants.boss.ALL_BOSSES[boss_idx]

    if map_floor:
        map_floor = map_floor.group(1)
        maps = re.sub(map_floor, '', maps).strip()

    for boss_map in constants.boss.BOSS_MAPS[boss]:
        if re.search(maps, boss_map, re.IGNORECASE):
            if map_floor and not re.search(map_floor, boss_map, re.IGNORECASE):
                continue # similar name; wrong number
            elif map_idx != -1: 
                return -1 # multiple matched; invalid
            else:
                map_idx = constants.boss.BOSS_MAPS[boss].index(boss_map)

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
            .format(boss, '\n- '.join(constants.boss.BOSS_SYNONYMS[boss])))


async def get_maps(boss):
    """
    :func:`get_maps` gets the maps of a valid boss.

    Args:
        boss (str): the valid boss to get maps

    Returns:
        str: a formatted markdown message with maps for a boss
    """
    _maps = (constants.boss.GET_MAPS
             .format(boss, ('\n{} '.format(constants.boss.EMOJI_LOC))
                            .join(constants.boss.BOSS_MAPS[boss])))

    warps = constants.boss.NEAREST_WARPS[boss]
    _warps = []
    if type(warps[0]) is not str:
        for warp in warps:
            if warp[1] == 0:
                away = constants.boss.SAME_MAP
            elif warp[1] > 1:
                away = '{} {}'.format(str(warp[1]), constants.boss.MAPS_AWAY)
            else:
                away = '{} {}'.format(str(warp[1]), constants.boss.MAP_AWAY)
            _warps.append(constants.boss.MAP_DIST.format(warp[0], away))
        return (constants.boss.MAPAWAY
                .format(constants.boss.NEAREST_PLURAL.format(_maps),
                        '\n'.join(_warps)))
    else:
        if warps[1] == 0:
            away = constants.boss.SAME_MAP
        elif warps[1] > 1:
            away = '{} {}'.format(str(warps[1]), constants.boss.MAPS_AWAY)
        else:
            away = '{} {}'.format(str(warps[1]), constants.boss.MAP_AWAY)
        return (constants.boss.MAPAWAY
                .format(constants.boss.NEAREST_SINGLE.format(_maps),
                        constants.boss.MAP_DIST.format(warps[0], away)))


async def get_bosses(boss_type):
    """
    :func:`get_bosses` gets the bosses of a certain boss type.

    Args:
        boss_type (str): the type of the boss

    Returns:
        str: a formatted markdown message with bosses of the specified type
    """
    return (constants.boss.GET_BOSSES
            .format(boss_type, '\n- '.join(constants.boss.BOSSES[boss_type])))


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
    if boss in constants.boss.BOSSES[constants.boss.KW_DEMON]:
        return timedelta(minutes=(coefficient * constants.boss.TIME_STATUS_DEMON))
    elif boss in constants.boss.BOSSES[constants.boss.KW_FIELD]:
        return timedelta(minutes=(coefficient * constants.boss.TIME_STATUS_FIELD))
    elif boss == constants.boss.BOSS_W_ABOMINATION:
        return timedelta(minutes=(coefficient * constants.boss.TIME_STATUS_ABOM))
    else:
        return timedelta(minutes=(coefficient * constants.boss.TIME_STATUS_WB))
    # else:
    #     return timedelta(minutes=(coefficient * constants.boss.TIME_STATUS_ANCHORED))


async def validate_time(time):
    """
    :func:`validate_time` validates whether a string representing time is valid or not, returning a standardized one.

    Args:
        time (str): the time str to check

    Returns:
        str: a standardized time unit, e.g. 0:00 (midnight) or 13:00 (1 PM); or None if invalid
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

    if (boss not in constants.boss.BOSSES[constants.boss.KW_WORLD] and
        status == constants.boss.CMD_ARG_STATUS_ANCHORED):
        return constants.boss.FAIL_TEMPLATE.format(constants.boss.FAIL_STATUS_NO_ANCHOR, constants.boss.MSG_HELP)

    target['name'] = boss
    target['text_channel'] = msg_channel
    target['channel'] = options['channel']
    target['map'] = options['map']
    target['status'] = status

    time_offset = get_offset(boss, status)

    hours, minutes = [int(t) for t in time.split(':')]

    record = {}

    server_date = datetime.now() + timedelta(hours=constants.boss.TIME_H_LOCAL_TO_SERVER)

    if hours > int(server_date.hour):
        # adjust to one day before, e.g. record on 23:59, July 31st but recorded on August 1st
        server_date += timedelta(days=-1)

    # dates handled like above example, e.g. record on 23:59, December 31st but recorded on New Years Day
    record['year'] = int(server_date.year)
    record['month'] = int(server_date.month)
    record['day'] = int(server_date.day)
    record['hour'] = hours
    record['minute'] = minutes

    # reconstruct boss kill time
    record_date = datetime(*record.values())
    record_date += time_offset

    # reassign to target data
    target['year'] = int(record_date.year)
    target['month'] = int(record_date.month)
    target['day'] = int(record_date.day)
    target['hour'] = int(record_date.hour)
    target['minute'] = int(record_date.minute)

    vdb = vaivora.db.Database(server_id)
    if not await vdb.check_if_valid(constants.boss.MODULE_NAME):
        await vdb.create_db('boss')

    if await vdb.update_db_boss(target):
        return (constants.boss.SUCCESS_STATUS.format(constants.boss.ACKNOWLEDGED,
                                                boss, status, time,
                                                constants.boss.EMOJI_LOC,
                                                options['map'],
                                                options['channel']))
    else:
        return constants.boss.FAIL_TEMPLATE.format(constants.boss.FAIL_STATUS, constants.boss.MSG_HELP)


async def process_cmd_entry(server_id: int, msg_channel, bosses, entry, channel=None):
    """
    :func:`process_cmd_entry` processes a specific boss subcommand:
    entry to retrieve records.

    Args:
        server_id (int): the id of the server of the originating message
        msg_channel: the id of the channel of the originating message
            (belonging to server of `server_id`)
        bosses (list): a list of bosses to check
        entry (str): the entry command (list, erase)
        channel: (default: None) the channel for the record

    Returns:
        list(str): an appropriate message for success or fail of command,
            e.g. confirmation or list of entries
    """
    if type(bosses) is str:
        bosses = [bosses]

    vdb = vaivora.db.Database(server_id)
    if not await vdb.check_if_valid(constants.boss.MODULE_NAME):
        await vdb.create_db('boss')
        return [constants.boss.FAIL_BAD_DB,]

    # $boss <target> erase ...
    if entry == constants.boss.CMD_ARG_ENTRY_ERASE:
        if channel and bosses in constants.boss.BOSSES[constants.boss.KW_WORLD]:
            records = await vdb.rm_entry_db_boss(boss_list=bosses, boss_ch=channel)
        else:
            records = await vdb.rm_entry_db_boss(boss_list=bosses)

        if records:
            if bosses != constants.boss.ALL_BOSSES:
                erase_msg = constants.boss.SUCCESS_ENTRY_ERASE
            else:
                erase_msg = constants.boss.SUCCESS_ENTRY_ERASE_ALL
            _records = '\n- '.join(['**{}**'.format(rec) for rec in records])
            return ['{}{}'.format(erase_msg.format(len(records)),
                                  '\n- {}'.format(_records)),]
        else:
            return [constants.boss.FAIL_ENTRY_ERASE,]
    # $boss <target> list ...
    else:
        valid_boss_records = []
        valid_boss_records.append("Records:")
        boss_records = await vdb.check_db_boss(bosses=bosses) # possible return

        if not boss_records: # empty
            return [constants.boss.FAIL_ENTRY_LIST,]

        for boss_record in boss_records:
            boss_name = boss_record[0]
            boss_channel = str(floor(boss_record[1]))
            boss_prev_map = boss_record[2]
            boss_status = boss_record[3]

            # year, month, day, hour, minutes
            record_date = datetime(*[int(rec) for rec in boss_record[5:10]])
            
            time_diff = (datetime.now()
                         + timedelta(hours=constants.boss.TIME_H_LOCAL_TO_SERVER)
                         - record_date)

            if int(time_diff.days) >= 0 and boss_status != constants.boss.CMD_ARG_STATUS_ANCHORED:
                spawn_msg = constants.boss.TIME_SPAWN_MISSED
                minutes = floor(time_diff.seconds/60) + int(time_diff.days)*86400

            # anchored
            elif boss_status == constants.boss.CMD_ARG_STATUS_ANCHORED:
                spawn_msg = constants.boss.TIME_SPAWN_EARLY
                if int(time_diff.days) < 0:
                    minutes = floor((86400-int(time_diff.seconds))/60)
                else:
                    minutes = floor(time_diff.seconds/60) + int(time_diff.days)*86400

            else: #elif boss_status == constants.boss.CMD_ARG_STATUS_DIED:
                spawn_msg = constants.boss.TIME_SPAWN_ONTIME
                minutes = floor((86400-int(time_diff.seconds))/60)

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
                msg_hours = '{} hours'.format(str(floor((minutes % 86400)/60)))
            elif minutes > 59:
                msg_hours = '1 hour'

            # print minutes unconditionally
            # e.g.              0 minutes from now
            # e.g.              59 minutes ago
            msg_minutes = '{} minutes'.format(str(floor(minutes % 60)))
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
            if boss_status == constants.boss.CMD_ARG_STATUS_ANCHORED:
                msg_time = '{} {}'.format(msg_time, 'and as late as one hour later')

            last_map = 'last known map: {} {}'.format(constants.boss.EMOJI_LOC, boss_prev_map)

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
    if query == constants.boss.CMD_ARG_QUERY_ALIAS:
        return await get_syns(boss)
    # $boss <target> maps
    else:
        return await get_maps(boss)


class BossCog:

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def boss(self, ctx, arg: str):
        """
        :func:`boss` handles "$boss" commands.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            arg (str): the boss to check

        Returns:
            True if successful; False otherwise
        """
        if constants.main.HELP == arg:
            _help = help()
            for _h in _help:
                await ctx.author.send(_h)
            return True

        ctx.boss = arg

        return True

    # $boss <boss> <status> <time> [channel]
    @boss.command(name='died', aliases=['die', 'dead', 'anch', 'anchor', 'anchored'])
    @checks.only_in_guild()
    @checks.check_channel(constants.main.ROLE_BOSS)
    async def status(self, ctx, time: str, map_or_channel = None):
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
        subcmd = await what_status(ctx.subcommand_passed)

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

        opt = {'channel': _channel, 'map': _map}
        msg = await (process_cmd_status(ctx.guild.id, ctx.channel.id,
                                        _boss, subcmd, _time, opt))
        await ctx.send('{} {}'.format(ctx.author.mention, msg))

        return True

    @boss.command(name='list', aliases=['ls', 'erase', 'del', 'delete', 'rm'])
    @checks.only_in_guild()
    @checks.check_channel(constants.main.ROLE_BOSS)
    async def entry(self, ctx, channel=None):
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
            boss_idx = await check_boss(ctx.boss)
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

        subcmd = await what_entry(ctx.subcommand_passed)

        msg = await (process_cmd_entry(ctx.guild.id, ctx.channel.id,
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
    async def query(self, ctx):
        """
        :func:`query` returns a user-usable list of maps and aliases for a given target.
        Unlike other boss commands, :func:`query` and :func:`_type` can be used in DMs.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if run successfully, regardless of result
        """
        subcmd = await what_query(ctx.subcommand_passed)

        if ctx.boss == constants.boss.CMD_ARG_TARGET_ALL:
           await ctx.send(constants.errors.IS_INVALID_3
                          .format(ctx.author.mention, ctx.boss,
                                  constants.boss.CMD_ARG_TARGET, subcmd))
           return False
        else:
            boss_idx = await check_boss(ctx.boss)
            if boss_idx == -1:
                await ctx.send(constants.errors.IS_INVALID_2
                               .format(ctx.author.mention, ctx.boss,
                                       constants.boss.CMD_ARG_TARGET))
                return False
            boss = constants.boss.ALL_BOSSES[boss_idx]

        msg = await process_cmd_query(boss, subcmd)

        await ctx.send('{}\n\n{}'.format(ctx.author.mention, msg))

    @boss.command(name='world', aliases=['w', 'field', 'f', 'demon', 'd', 'dl'])
    async def _type(self, ctx):
        """
        :func:`_type` returns a user-usable list of types of bosses: World, Field, Demon.
        Unlike other boss commands, :func:`query` and :func:`_type` can be used in DMs.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if run successfully, regardless of result
        """
        subcmd = await what_type(ctx.subcommand_passed)

        if ctx.boss != constants.boss.CMD_ARG_TARGET_ALL:
           await ctx.send(constants.errors.IS_INVALID_3
                          .format(ctx.author.mention, ctx.boss,
                                  constants.boss.CMD_ARG_TARGET, subcmd))
           return False

        msg = await get_bosses(subcmd)

        await ctx.send('{}\n\n{}'.format(ctx.author.mention, msg))


def setup(bot):
    bot.add_cog(BossCog(bot))
