import asyncio
import logging
import re
from datetime import timedelta
from inspect import cleandoc
from math import floor
from operator import itemgetter

import discord
import pendulum
import yaml
from discord.ext import commands, tasks

import checks
import vaivora.common
import vaivora.db


HELP = []
HELP.append(
    cleandoc(
        """
        ```
        Usage:
            $boss <target> <status> <time> [<channel>] [<map>]
            $boss <target> (<entry> [<channel>] | <query> | <type>)
            $boss help

        Examples:
            $boss cerb died 12:00pm mok
                Means: "Violent Cerberus" died in "Mokusul Chamber" at 12:00PM server time.
                Omit channels for field bosses.

            $boss crab died 14:00 ch2
                Means: "Earth Canceril" died in "Royal Mausoleum Constructors' Chapel" at 2:00PM server time.
                You may omit channel for world bosses.

            $boss all erase
                Means: Erase all records unconditionally.

            $boss nuaele list
                Means: List records with "[Demon Lords: Nuaele, Zaura, Blut]".

            $boss rexipher erase
                Means: Erase records with "[Demon Lords: Mirtis, Rexipher, Helgasercle, Marnox]".

            $boss crab maps
                Means: Show maps where "Earth Canceril" may spawn.

            $boss crab alias
                Means: Show aliases for "Earth Canceril", of which "crab" is an alias
        ```
        """
        )
    )
HELP.append(
    cleandoc(
        """
        ```
        Options:
            <target>
                This can be either "all" or part of the single boss's name. e.g. "cerb" for "Violent Cerberus"
                "all" will always target all valid bosses for the command. The name (or part of it) will only target that boss.
                Some commands do not work with both. Make sure to check which command can accept what <target>.

            <status>
                This <subcommand> refers to specific conditions related to a boss's spawning.
                Options:
                    "died": to refer a known kill
                    "anchored": to refer a process known as anchoring for world bosses
                <target> cannot be "all".

            <entry>
                This <subcommand> allows you to manipulate existing records.
                Options:
                    "list": to list <target> records
                    "erase": to erase <target> records
                <target> can be any valid response.

            <query>
                This <subcommand> supplies info related to a boss.
                Options:
                    "maps": to show where <target> may spawn
                    "alias": to list possible short-hand aliases, e.g. "ml" for "Noisy Mineloader", to use in <target>
                <target> cannot be "all".

            <type>
                This <subcommand> returns a list of bosses assigned to a type.
                Options:
                    "world": bosses that can spawn across all channels in a particular map; they each have a gimmick to spawn
                    "event": bosses/events that can be recorded; usually time gimmick-related
                    "field": bosses that spawn only in CH 1; they spawn without a separate mechanism/gimmick
                    "demon": Demon Lords, which also count as field bosses; they have longer spawn times and the server announces everywhere prior to a spawn
                <target> must be "all".
        ```
        """
        )
    )
HELP.append(
    cleandoc(
        """
        ```
        Options (continued):
            <time>
                This refers only to server time. Remember to report in a format like "10:00".
                12/24H formats OK; AM/PM can be omitted but the time will be treated as 24H.
                <target> cannot be "all". Only valid for <status>.

            [<channel>]
                (optional) This is the channel in which the boss was recorded.
                Remember to report in a format like "ch1".
                Omit for all bosses except world bosses. Field boss (including Demon Lords) spawn only in CH 1.
                <target> cannot be "all". Only valid for <status> & <entry>.

            [<map>]
                (optional) This is the map in which the boss was recorded.
                You may use part of the map's name. If necessary, enclose the map's name with quotations.
                Omit for world bosses and situations in which you do not know the last map.
                <target> cannot be "all". Only valid for <status>.

            help
                Prints this page.
        ```
        """
        )
    )

newline = '\n'
bullet_point = '\n- '

regex_channel = re.compile(r'(ch?)*.?([1-4])$', re.IGNORECASE)
regex_map_floor = re.compile('.*([0-9]).*')

regex_status_died = re.compile(r'(di|kill)(ed)?', re.IGNORECASE)
regex_status_anchored = re.compile(r'anch(or(ed)?)?', re.IGNORECASE)

regex_entry_list = re.compile(r'(show|li?st?)', re.IGNORECASE)
regex_entry_erase = re.compile(r'(erase|del(ete))?', re.IGNORECASE)

regex_query_maps = re.compile(r'maps?', re.IGNORECASE)
regex_query_alias = re.compile(r'(syn(onym)?s?|alias(es)?)', re.IGNORECASE)

regex_type_world = re.compile(r'w(orld)?', re.IGNORECASE)
regex_type_field = re.compile(r'f(ield)?', re.IGNORECASE)
regex_type_demon = re.compile(r'd(emon)?', re.IGNORECASE)

default_tz = 'America/New_York'

logger = logging.getLogger('vaivora.cogs.boss')
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


with open('boss.yaml', 'r') as f:
    boss_conf = yaml.load(f, Loader = yaml.Loader)
    all_bosses = []
    for kind in boss_conf['bosses']['all']:
        if kind == 'event':
            continue
        else:
            all_bosses.extend(boss_conf['bosses'][kind])

try:
    with open('emoji.yaml', 'r') as f:
        emoji = yaml.load(f, Loader = yaml.Loader)
except FileNotFoundError:
    # Fallback on default
    with open('emoji.yaml.example', 'r') as f:
        emoji = yaml.load(f, Loader = yaml.Loader)


async def boss_helper(boss: str, kill_time: str, map_or_channel):
    """Processes for `status` subcommands.

    Args:
        boss (str): the boss to check
        kill_time (str): time when the boss died
        map_or_channel: the map xor channel in which the boss died;
            can be None from origin function

    Returns:
        tuple: (boss_idx: int, kill_time: str, kill_map: str, channel: int)
        bool: False, if the arguments were invalid

    """
    channel = 1
    map_idx = None

    boss_idx = await check_boss(boss)

    if boss_idx == -1:
        return False

    kill_time = await vaivora.common.validate_time(time)

    if not time:
        return False

    boss = all_bosses[boss_idx]

    if len(boss_conf['maps'][boss]) == 1:
        map_idx = 0

    if map_or_channel and type(map_or_channel) is int:
        if map_or_channel <= 4 or map_or_channel > 1:
            # Use user-input channel only if valid
            channel = map_or_channel
    elif map_or_channel and regex_channel.match(map_or_channel):
        channel = regex_channel.match(map_or_channel)
        # Channel will always be 1 through 4 inclusive
        channel = int(channel.group(2))
    elif type(map_or_channel) is str and map_idx != 0: # possibly map
        map_idx = await check_maps(boss_idx, map_or_channel)

    if (not map_idx and map_idx != 0) or map_idx == -1:
        kill_map = None
    else:
        kill_map = boss_conf['maps'][boss][map_idx]

    return (boss, time, kill_map, channel)


async def what_status(status: str):
    """Checks what `status` the input may be.

    `status` subcommands are defined to be `died` and `anchored`.

    Args:
        status (str): the string to check for `status`

    Returns:
        str: the correct "status" if successful
        None: if invalid

    """
    if regex_status_died.match(status):
        return 'died'
    elif regex_status_anchored.match(status):
        return 'anchored'
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
    if regex_entry_list.search(entry):
        return 'list'
    elif regex_entry_erase.search(entry):
        return 'erase'
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
    if regex_query_maps.match(query):
        return 'maps'
    elif regex_query_alias.match(query):
        return 'alias'
    else:
        return None


async def what_type(kind):
    """Checks what `type` subcommand the input may be.

    `type` subcommands are defined to be "world", "event", "field",
    and "demon".

    Args:
        kind (str): the string to check for `type`

    Returns:
        str: the correct "type" if successful
        None: if invalid

    """
    if regex_type_world.search(kind):
        return 'world'
    elif regex_type_field.search(kind):
        return 'field'
    elif regex_type_demon.search(kind):
        return 'demon'
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

    for boss in boss_conf['aliases']:
        for boss_syn in boss_conf['aliases'][boss]:
            if entry == boss_syn:
                # synonyms are unique and exact match only
                return all_bosses.index(boss)

    for boss in all_bosses:
        if re.search(entry, boss, re.IGNORECASE):
            if not match:
                match = boss
            else:
                # duplicate or too ambiguous
                return -1

    if not match:
        return -1

    return all_bosses.index(match)


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
    map_floor = regex_map_floor.search(maps)
    boss = all_bosses[boss_idx]

    if map_floor:
        map_floor = map_floor.group(1)
        maps = re.sub(map_floor, '', maps).strip()

    for boss_map in boss_conf['maps'][boss]:
        if re.search(maps, boss_map, re.IGNORECASE):
            if map_floor and not re.search(map_floor, boss_map, re.IGNORECASE):
                # similar name; wrong number
                continue
            elif map_idx != -1:
                # multiple matched; invalid
                return -1
            else:
                map_idx = boss_conf['maps'][boss].index(boss_map)

    return map_idx


async def get_syns(boss):
    """Retrieves the synonyms of a valid boss.

    Args:
        boss (str): the string to get the boss's synonyms

    Returns:
        str: a formatted message with synonyms

    """
    return cleandoc(
        f"""**{boss}** can be called using the following aliases:

        - {bullet_point.join(boss_conf['aliases'][boss])}
        """
        )


async def get_maps(boss):
    """Retrieves the maps of a valid boss.

    Also retrieves the maps with the nearest warps.

    Args:
        boss (str): the valid boss to get maps

    Returns:
        str: a formatted message with maps for a boss

    """
    line_join = f"""\n{emoji['location']} """
    all_maps = cleandoc(
        f"""**{boss}** can be found in the following maps:

        {emoji['location']} {line_join.join(boss_conf['maps'][boss])}
        """
        )
    warps = boss_conf['nearest_warps'][boss]
    all_warps = []
    for (warp_map, distance) in warps:
        if distance == 0:
            away = 'same map'
        else:
            away = (
                f'{distance} maps away'
                if distance > 1
                else f'{distance} map away'
                )
        all_warps.append(
            f"""{emoji['location']} **{warp_map}** ({away})"""
            )
    return cleandoc(
        f"""Nearest map(s) with Vakarine statue:

        {newline.join(all_warps)}
        """
        )


async def get_bosses(kind):
    """Retrieves the bosses of a certain boss `kind`, or type.

    Args:
        kind (str): the type of the boss

    Returns:
        str: a formatted message with bosses of the specified type

    """
    return cleandoc(
        f"""The following bosses are considered "**{kind}**" bosses:

        - {bullet_point.join(boss_conf['bosses'][kind])}
        """
        )


async def process_cmd_status(guild_id: int, text_channel: str, boss: str,
    status: str, time: str, kill_map: str, channel: int):
    """Processes boss `status` subcommand.

    Args:
        guild_id (int): the ID of the Discord guild of the originating message
        text_channel (str): the ID of the channel of the originating message,
            belonging to Discord guild of `guild_id`
        boss (str): the boss in question
        status (str): the boss's status, or the status subcommand
        time (str): time represented for the associated event
        kill_map (str): where the boss was killed
        channel (int): the channel in which the boss was killed

    Returns:
        str: an appropriate message for success or fail of command,
        e.g. boss data recorded

    """
    offset = 0
    target = {
        'name': boss,
        'text_channel': text_channel,
        'channel': channel,
        'map': kill_map,
        'status': status
        }

    time_offset = await vaivora.common.get_boss_offset(boss, status)

    hours, minutes = [int(t) for t in time.split(':')]

    vdb = vaivora.db.Database(guild_id)

    tz = await vdb.get_tz()
    if not tz:
        tz = default_tz

    offset = await vdb.get_offset()
    if not offset:
        offset = 0

    local = pendulum.now() + timedelta(hours = offset)
    server_date = local.in_tz(tz)

    if hours > int(server_date.hour):
        # Adjust to one day before,
        # e.g. record on 23:59, July 31st but recorded on August 1st
        server_date += timedelta(days = -1)

    # dates handled like above example,
    # e.g. record on 23:59, December 31st but recorded on New Years Day

    record = {
        'year': int(server_date.year),
        'month': int(server_date.month),
        'day': int(server_date.day),
        'hour': hours,
        'minute': minutes
        }

    # Reconstruct boss kill time
    record_date = pendulum.datetime(*record.values(), tz = tz)
    record_date += time_offset

    # reassign to target data
    target = {
        'year': int(record_date.year),
        'month': int(record_date.month),
        'day': int(record_date.day),
        'hour': int(record_date.hour),
        'minute': int(record_date.minute)
        }

    if not await vdb.check_if_valid('boss'):
        await vdb.create_db('boss')

    if await vdb.update_db_boss(target):
        return cleandoc(
            f"""Thank you! Your command has been acknowledged and recorded.

            **{boss}**
            - {status} at **{time}**
            - {emoji['location']} {kill_map} CH {channel}
            """
            )
    else:
        return cleandoc(
            f"""Your command could not be processed.
            It appears this record overlaps too closely with another.
            """
            )


async def process_cmd_entry_erase(guild_id: int, txt_channel: str, bosses: list,
    channel = None):
    """Processes boss `entry` `erase` subcommand.

    Args:
        guild_id (int): the id of the Discord guild of the originating message
        txt_channel (str): the id of the channel of the originating message,
            belonging to Discord guild of `guild_id`
        bosses (list): a list of bosses to check
        channel (int, optional): the channel for the record;
            defaults to None

    Returns:
        str: an appropriate message for success or fail of command,
            e.g. confirmation or list of entries

    """
    if type(bosses) is str:
        bosses = [bosses]

    vdb = vaivora.db.Database(guild_id)

    if channel and bosses in boss_conf['bosses']['world']:
        records = await vdb.rm_entry_db_boss(bosses = bosses, channel = channel)
    else:
        records = await vdb.rm_entry_db_boss(bosses = bosses)

    if records:
        records = [f'**{record}**' for record in records]
        return cleandoc(
            f"""Your queried records ({len(records)}) have been """
            f"""successfully erased.

            - {bullet_point.join(records)}
            """
            )
    else:
        return '*(But **nothing** happened...)*'


async def process_cmd_entry_list(guild_id: int, txt_channel: str, bosses: list,
    channel_filter: int = 0):
    """Processes boss `entry` `list` subcommand.

    Args:
        guild_id (int): the ID of the Discord guild of the originating message
        txt_channel (str): the ID of the channel of the originating message,
            belonging to Discord guild with ID `guild_id`
        bosses (list): a list of bosses to check
        channel_filter (int, optional): the channel to filter for the record;
            defaults to 0

    Returns:
        list(str): an appropriate message for success of command,
            e.g. confirmation or list of entries
        str: error message

    """
    if type(bosses) is str:
        bosses = [bosses]

    vdb = vaivora.db.Database(guild_id)

    records = await vdb.check_db_boss(bosses = bosses, channel = channel_filter)

    if not records:
        return 'No results found! Try a different boss.'


    valid_records = []

    now = pendulum.now()

    diff_h, diff_m = await vaivora.common.get_time_diff(guild_id)
    full_diff = timedelta(hours = diff_h, minutes = diff_m)

    for record in records:
        name, channel, prev_map = [str(field) for field in record[:3]]

        record_date = pendulum.datetime(
            *[int(rec) for rec in record[5:10]],
            tz = now.timezone_name
            )

        time_diff = record_date - (now + full_diff)
        diff_minutes = abs(floor(time_diff.seconds/60))

        if int(time_diff.minutes) < 0:
            spawn_message = 'should have spawned at'
        else:
            spawn_message = 'will spawn around'

        # absolute date and time for spawn
        # e.g. 2017/07/06 "14:47"
        spawn_time = record_date.strftime("%Y/%m/%d %H:%M")

        time_as_text = []

        # Print day or days conditionally
        diff_days = abs(time_diff.days)
        if diff_days == 1:
            time_as_text.append('1 day')
        elif diff_days > 1:
            time_as_text.append(f'{diff_days} days')

        # Print hours conditionally
        diff_minutes = abs(floor(time_diff.seconds/60))
        if diff_minutes > 119:
            time_as_text.append(f'{floor((diff_minutes % 86400)/60)} hours')
        elif diff_minutes > 59:
            time_as_text.append('1 hour')

        # Print minutes unconditionally
        # e.g. 0 minutes from now
        # e.g. 59 minutes ago
        diff_minutes = floor(diff_minutes % 60)
        minutes = f'{diff_minutes} minute'
        if diff_minutes != 1:
            minutes = f'{minutes}s'

        when = 'from now' if int(time_diff.seconds) >= 0 else 'ago'

        time_since = f'{minutes} {when}'
        if time_as_text:
            time_since = f"""{', '.join(time_as_text)}, {time_since}"""

        message = cleandoc(
            f"""**{name}**
            - {spawn_message} **{spawn_time}** ({time_since})
            - last known map: {emoji['location']} {prev_map} CH {channel}
            """
            )

        valid_records.append(message)

    return valid_records


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
    if query == 'alias':
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
        self.boss_timer_check.start()

    @commands.group()
    async def boss(self, ctx, arg: str):
        """Handles `$boss` commands.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            arg (str): the boss to check

        Returns:
            bool: True if successful; False otherwise

        """
        if arg == 'help':
            for _h in HELP:
                await ctx.author.send(_h)
            return True
        else:
            ctx.boss = arg
            return True

    # $boss <boss> <status> <time> [channel]
    @boss.command(
        name = 'died',
        aliases = [
            'die',
            'dead',
            'anch',
            'anchor',
            'anchored',
            ]
        )
    @checks.only_in_guild()
    @checks.check_channel('boss')
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
        subcommand = await what_status(ctx.subcommand_passed)

        if ctx.boss == 'all':
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    **{ctx.boss}** is invalid for the `{subcommand}` subcommand.
                    """
                    )
                )
            return False

        try:
            boss, kill_time, kill_map, channel = await boss_helper(
                ctx.boss, time, map_or_channel
                )
        except ValueError:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Your command could not be parsed. Please check for errors.
                    """
                    )
                )
            return False

        message = await process_cmd_status(
            ctx.guild.id, ctx.channel.id, boss, subcommand, kill_time,
            kill_map, channel
            )
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                {message}
                """
                )
            )
        return True

    @boss.command(
        name = 'list',
        aliases = [
            'ls',
            'erase',
            'del',
            'delete',
            'rm',
            ]
        )
    @checks.only_in_guild()
    @checks.check_channel('boss')
    async def entry(self, ctx, channel = None):
        """Manipulates boss table records.

        Possible `entry` subcommands: `list`, `erase`

        Args:
            ctx (discord.ext.commands.Context): context of the message
            channel: the channel to show, if supplied;
                defaults to None

        Returns:
            bool: True if run successfully, regardless of result;
            False, if the DB was corrupt and subsequently rebuilt

        """
        if ctx.boss != 'all':
            boss_idx = await check_boss(ctx.boss)
            if boss_idx == -1:
                await ctx.send(
                    cleandoc(
                        f"""{ctx.author.mention}

                        **{ctx.boss}** is an invalid boss.
                        """
                        )
                    )
                return False
            boss = all_bosses[boss_idx]
        else:
            boss = all_bosses

        if channel is not None:
            channel = regex_channel.match(channel)
            channel = int(channel.group(2))

        subcommand = await what_entry(ctx.subcommand_passed)

        vdb = vaivora.db.Database(ctx.guild.id)
        if not await vdb.check_if_valid('boss'):
            await vdb.create_db('boss')
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    The boss database was corrupt and subsequently rebuilt.
                    """
                    )
                )
            return False

        function = (
            process_cmd_entry_erase
            if subcommand == 'erase'
            else process_cmd_entry_list
            )

        messages = await function(
            ctx.guild.id, ctx.channel.id, boss, channel
            )

        if type(messages) is str:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    {messages}
                    """
                    )
                )
            return False
        else:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Records:
                    """
                    )
                )
            for message in await vaivora.common.chunk_messages(messages, 5):
                async with ctx.typing():
                    await asyncio.sleep(1)
                    await ctx.send(message)

            return True

    @boss.command(
        name = 'maps',
        aliases = [
            'map',
            'alias',
            'aliases',
            ]
        )
    async def query(self, ctx):
        """Supplies information about bosses.

        Possible `query` subcommands: `maps`, `aliases`

        `query` can be used in DMs.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if successful; False otherwise

        """
        subcommand = await what_query(ctx.subcommand_passed)

        if ctx.boss == 'all':
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    **{ctx.boss}** is invalid for the `{subcommand}` subcommand.
                    """
                    )
                )
            return False
        else:
            boss_idx = await check_boss(ctx.boss)
            if boss_idx == -1:
                await ctx.send(
                    cleandoc(
                        f"""{ctx.author.mention}

                        **{ctx.boss}** is an invalid boss.
                        """
                        )
                    )
                return False
            boss = all_bosses[boss_idx]

        message = await process_cmd_query(boss, subcommand)

        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                {message}
                """
                )
            )
        return True

    @boss.command(
        name = 'world',
        aliases = [
            'w',
            'demon',
            'd',
            'dl',
            'field',
            'f',
            ]
        )
    async def _type(self, ctx):
        """Supplies a list of bosses given a kind.

        Possible `type` subcommands: `world`, `field`, `demon`

        `_type` can be used in DMs.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if success; False otherwise

        """
        subcmd = await what_type(ctx.subcommand_passed)

        if ctx.boss != 'all':
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    **{ctx.boss}** is invalid for the `subcomamand` subcommand.
                    """
                    )
                )
            return False

        message = await get_bosses(subcmd)

        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                {message}
                """
                )
            )

    @tasks.loop(minutes = 1)
    async def boss_timer_check(self):
        loop_time = pendulum.now()
        for rec_hash, rec_time in self.records.items():
            rec_diff = loop_time - rec_time
            if rec_diff.minutes > 15:
                del self.records[rec_hash]

        for guild_id, guild_db in self.guilds.items():
            messages = []
            if not await guild_db.check_if_valid('boss'):
                await guild_db.create_db('boss')
                continue

            results = await guild_db.check_db_boss()
            if not results:
                continue

            diff_h, diff_m = await vaivora.common.get_time_diff(guild_id)
            full_diff = timedelta(hours = diff_h, minutes = diff_m)

            # Sort by time - year, month, day, hour, minute
            results.sort(key = itemgetter(5,6,7,8,9))

            for result in results:
                discord_channel = result[4]
                boss, channel, kill_map, status = [str(r) for r in result[0:4]]

                try:
                    entry_time = pendulum.datetime(
                        *[int(t) for t in result[5:10]],
                        tz = loop_time.timezone_name
                        )
                except ValueError as e:
                    logger.error(
                        f'Caught {e} in cogs.boss: boss_timer_check; '
                        f'guild: {guild_id}'
                        )
                    continue

                time_diff = entry_time - (loop_time + full_diff)

                # Record is in the past
                if time_diff.seconds < 0:
                    continue

                record = await vaivora.common.process_boss_record(
                    boss,
                    status,
                    entry_time,
                    time_diff,
                    kill_map,
                    channel,
                    guild_id
                    )
                hashed_record = await vaivora.common.hash_object(
                    discord_channel,
                    boss,
                    entry_time,
                    channel
                    )

                if hashed_record in self.records:
                    continue

                # Record is within 15 minutes behind the loop time
                if time_diff.seconds <= 900 and time_diff.seconds > 0:
                    messages.append(
                        {
                            'record': record,
                            'discord_channel': discord_channel
                            }
                        )
                    self.records[hashed_record] = entry_time

            if not messages:
                continue
            else:
                await vaivora.common.send_messages(
                    self.bot.get_guild(guild_id),
                    messages,
                    'boss'
                    )

    @boss_timer_check.before_loop
    async def before_boss_timer_check(self):
        self.records = {}
        await self.bot.wait_until_ready()
        print('Checking guilds for boss background check...')
        self.guilds = {
            guild.id: vaivora.db.Database(guild.id)
            for guild
            in self.bot.guilds
            if not guild.unavailable
            }
        print(f'Added {len(self.guilds)} guilds to boss background check!')

    async def add_new_guild(self, guild_id: int):
        """Add a new guild to background processing.

        Args:
            guild_id (int): the Discord guild's ID

        Returns:
            bool: True

        """
        self.guilds[guild_id] = vaivora.db.Database(guild_id)


def setup(bot):
    bot.add_cog(BossCog(bot))
