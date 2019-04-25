import re
import asyncio
from math import floor
from datetime import timedelta

import discord
from discord.ext import commands
import pendulum

import checks
import vaivora.db
import constants.boss
import constants.offset
import vaivora.utils


async def boss_helper(boss: str, time: str, map_or_channel):
    """Processes for `status` subcommands.

    Args:
        boss (str): the boss to check
        time (str): time when the boss died
        map_or_channel: the map xor channel in which the boss died;
            can be None from origin function

    Returns:
        tuple: (boss_idx: int, time: str, _map: str, channel: int)
        tuple of None: if the arguments were invalid

    """
    channel = 1 # base case
    map_idx = None # don't assume map

    boss_idx = await check_boss(boss)

    if boss_idx == -1: # invalid boss
        return (None,)

    time = await vaivora.utils.validate_time(time)

    if not time: # invalid time
        return (None,None)

    boss = constants.boss.ALL_BOSSES[boss_idx]

    if len(constants.boss.BOSS_MAPS[boss]) == 1:
        map_idx = 0 # it just is

    if map_or_channel and type(map_or_channel) is int:
        if map_or_channel <= 4 or map_or_channel > 1:
            # use user-input channel only if valid
            channel = map_or_channel
    elif (map_or_channel and
          constants.boss.REGEX_OPT_CHANNEL.match(map_or_channel)):
        channel = constants.boss.REGEX_OPT_CHANNEL.match(map_or_channel)
        # channel will always be 1 through 4 inclusive
        channel = int(channel.group(2))
    elif type(map_or_channel) is str and map_idx != 0: # possibly map
        map_idx = await check_maps(boss_idx, map_or_channel)

    if (not map_idx and map_idx != 0) or map_idx == -1:
        _map = ""
    else:
        _map = constants.boss.BOSS_MAPS[boss][map_idx]

    return (boss, time, _map, channel)


async def what_status(status: str):
    """Checks what `status` the input may be.

    `status` subcommands are defined to be `died` and `anchored`.

    Args:
        status (str): the string to check for `status`

    Returns:
        str: the correct "status" if successful
        None: if invalid

    """
    if constants.boss.REGEX_STATUS_DIED.match(status):
        return constants.boss.CMD_ARG_STATUS_DIED
    elif constants.boss.REGEX_STATUS_ANCHORED.match(status):
        return constants.boss.CMD_ARG_STATUS_ANCHORED
    else:
        return None


async def what_entry(entry: str):
    """Checks what `entry` subcommand the input may be.

    `entry` subcommands are defined to be "maps" and "alias".

    Args:
        entry (str): the string to check for `entry`

    Returns:
        str: the correct "entry" if successful
        None: if invalid

    """
    if constants.boss.REGEX_ENTRY_LIST.search(entry):
        return constants.boss.CMD_ARG_ENTRY_LIST
    elif constants.boss.REGEX_ENTRY_ERASE.search(entry):
        return constants.boss.CMD_ARG_ENTRY_ERASE
    else:
        return None


async def what_query(query: str):
    """Checks what `query` subcommand the input may be.

    `query` subcommands are defined to be "maps" and "alias".

    Args:
        query (str): the string to check for `query`

    Returns:
        str: the correct "query" if successful
        None: if invalid

    """
    if constants.boss.REGEX_QUERY_MAPS.match(query):
        return constants.boss.CMD_ARG_QUERY_MAPS
    elif constants.boss.REGEX_QUERY_ALIAS.match(query):
        return constants.boss.CMD_ARG_QUERY_ALIAS
    else:
        return None


async def what_type(_type):
    """Checks what `type` subcommand the input may be.

    `type` subcommands are defined to be "world", "event", "field",
    and "demon".

    Args:
        _type (str): the string to check for `type`

    Returns:
        str: the correct "type" if successful
        None: if invalid

    """
    if constants.boss.REGEX_TYPE_WORLD.search(_type):
        return constants.boss.KW_WORLD
    elif constants.boss.REGEX_TYPE_FIELD.search(_type):
        return constants.boss.KW_FIELD
    elif constants.boss.REGEX_TYPE_DEMON.search(_type):
        return constants.boss.KW_DEMON
    else:
        return None


async def check_boss(entry):
    """Checks whether an input is a valid boss.

    Args:
        entry (str): the string to check for valid boss

    Returns:
        int: the boss index if valid and matching just one;
        otherwise, -1 for invalid input

    """
    match = None

    for boss in constants.boss.BOSS_SYNONYMS:
        for boss_syn in constants.boss.BOSS_SYNONYMS[boss]:
            if entry == boss_syn:
                # synonyms are unique and exact match only
                return constants.boss.ALL_BOSSES.index(boss)

    for boss in constants.boss.ALL_BOSSES:
        if re.search(entry, boss, re.IGNORECASE):
            if not match:
                match = boss
            else:
                # duplicate or too ambiguous
                return -1

    if not match:
        return -1

    return constants.boss.ALL_BOSSES.index(match)


async def check_maps(boss_idx, maps):
    """Checks whether an input refers to a valid map.

    Args:
        boss_idx (int): the valid boss index to check
        maps (str): the string to check for valid map

    Returns:
        int: the map index if valid and matching just one;
        otherwise, -1 for invalind input

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
                # similar name; wrong number
                continue
            elif map_idx != -1:
                # multiple matched; invalid
                return -1
            else:
                map_idx = constants.boss.BOSS_MAPS[boss].index(boss_map)

    return map_idx


async def get_syns(boss):
    """Retrieves the synonyms of a valid boss.

    Args:
        boss (str): the string to get the boss's synonyms

    Returns:
        str: a formatted message with synonyms

    """
    return ("**{}** can be called using the following aliases:\n\n- {}"
            .format(boss, '\n- '.join(constants.boss.BOSS_SYNONYMS[boss])))


async def get_maps(boss):
    """Retrieves the maps of a valid boss.

    Also retrieves the maps with the nearest warps.

    Args:
        boss (str): the valid boss to get maps

    Returns:
        str: a formatted message with maps for a boss

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


async def get_bosses(kind):
    """Retrieves the bosses of a certain boss `kind`, or type.

    Args:
        kind (str): the type of the boss

    Returns:
        str: a formatted message with bosses of the specified type

    """
    return (constants.boss.GET_BOSSES
            .format(kind, '\n- '.join(constants.boss.BOSSES[kind])))


async def process_cmd_status(guild_id: int, txt_channel: str, boss: str,
    status: str, time: str, options: dict):
    """Processes boss `status` subcommand.

    Args:
        guild_id (int): the id of the Discord guild of the originating message
        txt_channel (str): the id of the channel of the originating message,
            belonging to Discord guild of `guild_id`
        boss (str): the boss in question
        status (str): the boss's status, or the status subcommand
        time (str): time represented for the associated event
        options (dict): a dict containing optional parameters,
            with possible default values

    Returns:
        str: an appropriate message for success or fail of command,
        e.g. boss data recorded

    """
    offset = 0
    target = {}

    target['name'] = boss
    target['text_channel'] = txt_channel
    target['channel'] = options['channel']
    target['map'] = options['map']
    target['status'] = status

    time_offset = await vaivora.utils.get_boss_offset(boss, status)

    hours, minutes = [int(t) for t in time.split(':')]

    record = {}

    vdb = vaivora.db.Database(guild_id)

    tz = await vdb.get_tz()
    if not tz:
        tz = constants.offset.DEFAULT

    offset = await vdb.get_offset()
    if not offset:
        offset = 0

    local = pendulum.now() + timedelta(hours=offset)
    server_date = local.in_tz(tz)

    if hours > int(server_date.hour):
        # adjust to one day before,
        # e.g. record on 23:59, July 31st but recorded on August 1st
        server_date += timedelta(days=-1)

    # dates handled like above example,
    # e.g. record on 23:59, December 31st but recorded on New Years Day
    record['year'] = int(server_date.year)
    record['month'] = int(server_date.month)
    record['day'] = int(server_date.day)
    record['hour'] = hours
    record['minute'] = minutes

    # reconstruct boss kill time
    record_date = pendulum.datetime(*record.values(), tz=tz)
    record_date += time_offset

    # reassign to target data
    target['year'] = int(record_date.year)
    target['month'] = int(record_date.month)
    target['day'] = int(record_date.day)
    target['hour'] = int(record_date.hour)
    target['minute'] = int(record_date.minute)

    if not await vdb.check_if_valid(constants.boss.MODULE_NAME):
        await vdb.create_db('boss')

    if await vdb.update_db_boss(target):
        return (constants.boss.SUCCESS_STATUS
                .format(constants.boss.ACKNOWLEDGED,
                        boss, status, time,
                        constants.boss.EMOJI_LOC,
                        options['map'],
                        options['channel']))
    else:
        return (constants.boss.FAIL_TEMPLATE
                .format(constants.boss.FAIL_STATUS, constants.boss.MSG_HELP))


async def process_cmd_entry(guild_id: int, txt_channel: str, bosses: list,
    entry: str, channel=None):
    """Processes boss `entry` subcommand.

    Args:
        guild_id (int): the id of the Discord guild of the originating message
        txt_channel (str): the id of the channel of the originating message,
            belonging to Discord guild of `guild_id`
        bosses (list): a list of bosses to check
        entry (str): the entry subcommand (`list`, `erase`)
        channel (int, optional): the channel for the record;
            defaults to None

    Returns:
        list(str): an appropriate message for success or fail of command,
        e.g. confirmation or list of entries

    """
    if type(bosses) is str:
        bosses = [bosses]

    vdb = vaivora.db.Database(guild_id)
    if not await vdb.check_if_valid(constants.boss.MODULE_NAME):
        await vdb.create_db('boss')
        return [constants.boss.FAIL_BAD_DB,]

    # $boss <target> erase ...
    if entry == constants.boss.CMD_ARG_ENTRY_ERASE:
        if channel and bosses in constants.boss.BOSSES[constants.boss.KW_WORLD]:
            records = await vdb.rm_entry_db_boss(bosses=bosses, channel=channel)
        else:
            records = await vdb.rm_entry_db_boss(bosses=bosses)

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

        now = pendulum.now()

        diff_h, diff_m = await vaivora.utils.get_time_diff(guild_id)
        full_diff = timedelta(hours=diff_h, minutes=diff_m)

        for boss_record in boss_records:
            boss_name = boss_record[0]
            boss_channel = str(floor(boss_record[1]))
            boss_prev_map = boss_record[2]
            boss_status = boss_record[3]

            # year, month, day, hour, minutes
            record_date = pendulum.datetime(
                *[int(rec) for rec in boss_record[5:10]],
                tz=now.timezone_name
                )

            time_diff = record_date - (now + full_diff)

            if int(time_diff.minutes) < 0:
                spawn_msg = constants.boss.TIME_SPAWN_MISSED
            else:
                spawn_msg = constants.boss.TIME_SPAWN_ONTIME

            diff_minutes = abs(floor(time_diff.seconds/60))

            # absolute date and time for spawn
            # e.g. 2017/07/06 "14:47"
            spawn_time = record_date.strftime("%Y/%m/%d %H:%M")

            # print day or days conditionally
            days = None

            diff_days = abs(time_diff.days)

            if diff_days == 1:
                days = '1 day'
            elif diff_days > 1:
                days = '{} days'.format(diff_days)

            # print hour or hours conditionally
            hours = None

            if diff_minutes > 119:
                hours = '{} hours'.format(floor((diff_minutes % 86400)/60))
            elif diff_minutes > 59:
                hours = '1 hour'

            # print minutes unconditionally
            # e.g.              0 minutes from now
            # e.g.              59 minutes ago
            minutes = '{} minutes'.format(floor(diff_minutes % 60))
            when = 'from now' if int(time_diff.seconds) >= 0 else 'ago'

            if days is None and hours is None:
                time_since = '{} {}'.format(minutes, when)
            elif days is None:
                time_since = '{}, {} {}'.format(hours, minutes, when)
            elif hours is None:
                time_since = '{}, {} {}'.format(days, minutes, when)
            else:
                time_since = '{}, {}, {} {}'.format(days, hours, minutes, when)

            last_map = 'last known map: {} {}'.format(
                constants.boss.EMOJI_LOC, boss_prev_map
                )

            message = ('**{}**\n- {} **{}** ({})\n- {} CH {}'
                       .format(boss_name, spawn_msg, spawn_time,
                               time_since, last_map, boss_channel))

            valid_boss_records.append(message)

        #valid_boss_records.append("```\n")
        return valid_boss_records #'\n'.join(valid_boss_records)


async def process_cmd_query(boss: str, query: str):
    """Processes a `query` subcommand relating to bosses.

    Args:
        boss (str): the boss to query
        query (str): the query (`synonyms`, `maps`)

    Returns:
        str: an appropriate message for success or fail of command,
        i.e. maps or aliases

    """
    # $boss <target> syns
    if query == constants.boss.CMD_ARG_QUERY_ALIAS:
        return await get_syns(boss)
    # $boss <target> maps
    else:
        return await get_maps(boss)


class BossCog(commands.Cog):
    """Interface for the `$boss` commands.

    This cog interacts with the `vaivora.db` backend.

    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def boss(self, ctx, arg: str):
        """Handles `$boss` commands.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            arg (str): the boss to check

        Returns:
            bool: True if successful; False otherwise

        """
        if constants.boss.HELP == arg:
            _help = constants.boss.HELP
            for _h in _help:
                await ctx.author.send(_h)
            return True

        ctx.boss = arg

        return True

    # $boss <boss> <status> <time> [channel]
    @boss.command(name='died', aliases=['die', 'dead', 'anch', 'anchor', 'anchored'])
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.ROLE_BOSS)
    async def status(self, ctx, time: str, map_or_channel = None):
        """Stores valid data into a database about a boss kill.

        Possible `status` subcommands: `died`, `anchored`

        Args:
            ctx (discord.ext.commands.Context): context of the message
            time (str): time when the boss died
            map_or_channel: the map xor channel in which the boss died;
                can be None from origin function

        Returns:
            bool: True if run successfully, regardless of result

        """
        subcmd = await what_status(ctx.subcommand_passed)

        if ctx.boss == constants.boss.CMD_ARG_TARGET_ALL:
           await ctx.send(constants.boss.FAIL_INVALID_3
                          .format(ctx.author.mention, ctx.boss,
                                  constants.boss.CMD_ARG_TARGET, subcmd))
           return False

        try:
            _boss, _time, _map, _channel = await boss_helper(
                ctx.boss, time, map_or_channel)
        except:
            which_fail = await boss_helper(ctx.boss, time, map_or_channel)
            if len(which_fail) == 1:
                await ctx.send(constants.boss.FAIL_INVALID_2
                               .format(ctx.author.mention, ctx.boss,
                                       constants.boss.CMD_ARG_TARGET))
            elif len(which_fail) == 2:
                await ctx.send(constants.boss.FAIL_INVALID_3
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
    @checks.check_channel(constants.settings.ROLE_BOSS)
    async def entry(self, ctx, channel=None):
        """Manipulates boss table records.

        Possible `entry` subcommands: `list`, `erase`

        Args:
            ctx (discord.ext.commands.Context): context of the message
            channel: the channel to show, if supplied;
                defaults to None

        Returns:
            bool: True if run successfully, regardless of result

        """
        if ctx.boss != constants.boss.CMD_ARG_TARGET_ALL:
            boss_idx = await check_boss(ctx.boss)
            if boss_idx == -1:
                await ctx.send(constants.boss.FAIL_INVALID_2
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
        """Supplies information about bosses.

        Possible `query` subcommands: `maps`, `aliases`
.
        `query` can be used in DMs.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if run successfully, regardless of result

        """
        subcmd = await what_query(ctx.subcommand_passed)

        if ctx.boss == constants.boss.CMD_ARG_TARGET_ALL:
           await ctx.send(constants.boss.FAIL_INVALID_3
                          .format(ctx.author.mention, ctx.boss,
                                  constants.boss.CMD_ARG_TARGET, subcmd))
           return False
        else:
            boss_idx = await check_boss(ctx.boss)
            if boss_idx == -1:
                await ctx.send(constants.boss.FAIL_INVALID_2
                               .format(ctx.author.mention, ctx.boss,
                                       constants.boss.CMD_ARG_TARGET))
                return False
            boss = constants.boss.ALL_BOSSES[boss_idx]

        msg = await process_cmd_query(boss, subcmd)

        await ctx.send('{}\n\n{}'.format(ctx.author.mention, msg))

    @boss.command(name='world', aliases=['w', 'field', 'f', 'demon', 'd', 'dl'])
    async def _type(self, ctx):
        """Supplies a list of bosses given a kind.

        Possible `type` subcommands: `world`, `field`, `demon`

        `_type` can be used in DMs.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if run successfully, regardless of result

        """
        subcmd = await what_type(ctx.subcommand_passed)

        if ctx.boss != constants.boss.CMD_ARG_TARGET_ALL:
           await ctx.send(constants.boss.FAIL_INVALID_3
                          .format(ctx.author.mention, ctx.boss,
                                  constants.boss.CMD_ARG_TARGET, subcmd))
           return False

        msg = await get_bosses(subcmd)

        await ctx.send('{}\n\n{}'.format(ctx.author.mention, msg))


def setup(bot):
    bot.add_cog(BossCog(bot))
