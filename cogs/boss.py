import asyncio
import re
from datetime import timedelta
from inspect import cleandoc
from math import floor
from operator import itemgetter

import discord
import pendulum
from discord.ext import commands, tasks

import checks
import vaivora.boss
import vaivora.common
import vaivora.db
from vaivora.config import BOSS, EMOJI


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

default_tz = 'America/New_York'


async def invalid_boss(ctx, error: str):
    """An exception was detected; check if it was an invalid boss.

    Not to be confused with `TypeError`.

    Args:
        error (str): the error message

    """
    if isinstance(error, checks.InvalidBossError):
        await ctx.send(
            cleandoc(
                f"""
                {ctx.author.mention}

                {error}
                """
                )
            )


async def what_status(status: str):
    """Checks what `status` the input may be.

    `status` subcommands are defined to be `died` and `anchored`.

    Args:
        status (str): the string to check for `status`

    Returns:
        str: the correct "status"

    """
    if status.startswith('d'):
        return 'died'
    else:
        return 'anchored'


async def what_entry(entry: str):
    """Checks what `entry` subcommand the input may be.

    `entry` subcommands are defined to be "maps" and "alias".

    Args:
        entry (str): the string to check for `entry`

    Returns:
        str: the correct "entry"

    """
    if entry.startswith('l'):
        return 'list'
    else:
        return 'erase'


async def get_bosses_by_type(ctx, kind):
    """Retrieves the bosses of a certain boss `kind`, or type.

    Args:
        kind (str): the type of the boss

    Returns:
        str: a formatted message with bosses of the specified type

    """
    return cleandoc(
        f"""{ctx.author.mention}

        The following bosses are considered "**{kind}**" bosses:

        - {bullet_point.join(BOSS['bosses'][kind])}
        """
        )


async def process_cmd_status(guild_id: int, text_channel: str, status: str,
    boss: vaivora.boss.Boss
    ):
    """Processes boss `status` subcommand.

    Args:
        guild_id (int): the ID of the Discord guild of the originating message
        text_channel (str): the ID of the channel of the originating message,
            belonging to Discord guild of `guild_id`
        status (str): the boss's status, or the status subcommand
        boss (vaivora.boss.Boss): the boss in question

    Returns:
        str: an appropriate message for success or fail of command,
        e.g. boss data recorded

    """
    target = {
        'name': boss.boss,
        'text_channel': text_channel,
        'channel': boss.channel,
        'map': boss.map,
        'status': status
        }

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
    record_date += boss.offset

    # reassign to target data
    target = {
        'year': int(record_date.year),
        'month': int(record_date.month),
        'day': int(record_date.day),
        'hour': int(record_date.hour),
        'minute': int(record_date.minute)
        }

    try:
        await vdb.check_if_valid('boss')
    except vaivora.db.InvalidDBError as e:
        await vdb.create_db('boss')

    if await vdb.update_db_boss(target):
        return cleandoc(
            f"""Thank you! Your command has been acknowledged and recorded.

            **{boss}**
            - {status} at **{time}**
            - {EMOJI['location']} {kill_map} CH {channel}
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

    if channel and bosses in BOSS['bosses']['world']:
        records = await vdb.rm_entry_db_boss(bosses=bosses, channel=channel)
    else:
        records = await vdb.rm_entry_db_boss(bosses=bosses)

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

    records = await vdb.check_db_boss(bosses=bosses, channel=channel_filter)

    if not records:
        return 'No results found! Try a different boss.'


    valid_records = []

    now = pendulum.now()

    diff_h, diff_m = await vaivora.common.get_time_diff(guild_id)
    full_diff = timedelta(hours=diff_h, minutes=diff_m)

    for record in records:
        name, channel, prev_map = [str(field) for field in record[:3]]

        record_date = pendulum.datetime(
            *[int(rec) for rec in record[5:10]],
            tz=now.timezone_name
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
            - last known map: {EMOJI['location']} {prev_map} CH {channel}
            """
            )

        valid_records.append(message)

    return valid_records


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
        name='died',
        aliases=[
            'die',
            'dead',
            'anch',
            'anchor',
            'anchored',
            ],
        )
    @checks.only_in_guild()
    @checks.check_channel('boss')
    @checks.is_boss_valid()
    async def status(self, ctx, time: str, map_or_channel: str = None):
        """Stores valid data into a database about a boss kill.

        Possible `status` subcommands: `died`, `anchored`

        Args:
            time (str): time when the boss died
            map_or_channel: the map xor channel in which the boss died;
                can be None from origin function

        """
        subcommand = await what_status(ctx.subcommand_passed)

        boss = vaivora.boss.Boss(ctx.boss)
        await boss.populate()

        kill_time = await vaivora.common.validate_time(time)
        e = await boss.parse_map_or_channel(map_or_channel)
        if e:
            await ctx.send(e)
 
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

    @status.error
    async def status_error(ctx, error):
        await invalid_boss(ctx, error)

    @boss.command(
        name='list',
        aliases=[
            'ls',
            'erase',
            'del',
            'delete',
            'rm',
            ],
        )
    @checks.only_in_guild()
    @checks.check_channel('boss')
    @checks.is_db_valid(ctx.guild.id, 'boss')
    async def entry(self, ctx, channel = None):
        """Manipulates boss table records.

        Possible `entry` subcommands: `list`, `erase`

        Args:
            channel: the channel to show, if supplied;
                defaults to None

        Returns:
            bool: True if run successfully, regardless of result;
            False, if the DB was corrupt and subsequently rebuilt

        """
        if ctx.boss != 'all':
            boss = vaivora.boss.Boss(ctx.boss)
            await boss.populate()
        else:
            boss = ALL_BOSSES

        try:
            channel = await vaivora.boss.ext_validate_channel(channel)
        except InvalidChannelError as e:
            await ctx.send(e)

        subcommand = await what_entry(ctx.subcommand_passed)

        vdb = vaivora.db.Database(ctx.guild.id)

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

    @entry.error
    async def entry_error(ctx, error):
        await invalid_boss(ctx, error)

    @boss.command(
        aliases=[
            'map',
            ],
        )
    @checks.is_boss_valid()
    async def maps(self, ctx):
        """Supplies information about bosses.

        Possible `query` subcommands: `maps`, `aliases`

        `query` can be used in DMs.

        """

        boss = vaivora.boss.Boss(ctx.boss)
        await boss.populate()

        message = await boss.get_maps()

        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                {message}
                """
                )
            )

    # @maps.error
    # async def maps_error(ctx, error):
    #     await invalid_boss(ctx, error)

    @boss.command(
        aliases=[
            'alias',
            ],
        )
    @checks.is_boss_valid()
    async def aliases(self, ctx):
        """Supplies information about bosses.

        Possible `query` subcommands: `maps`, `aliases`

        `query` can be used in DMs.

        """

        boss = vaivora.boss.Boss(ctx.boss)
        await boss.populate()

        message = await boss.get_synonyms()

        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                {message}
                """
                )
            )

    # @aliases.error
    # async def aliases_error(ctx, error):
    #     await invalid_boss(ctx, error)

    # Let's see if decorating stacking works
    @aliases.error
    @query.error
    async def query_error(ctx, error):
        await invalid_boss(ctx, error)

    @boss.command(
        aliases=[
            'w',
            ],
        )
    @checks.if_boss_valid(all_valid=True)
    async def world(self, ctx):
        """Prints a message with all World Bosses.

        Possible `type` subcommands: `world`, `field`, `demon`

        All `type` commands can be used in DMs.

        """
        await get_bosses_by_type('world')

    # @world.error
    # async def world_error(ctx, error):
    #     await invalid_boss(ctx, error)

    @boss.command(
        aliases=[
            'f',
            ],
        )
    @checks.if_boss_valid(all_valid=True)
    async def field(self, ctx):
        """Prints a message with all Field Bosses.

        Possible `type` subcommands: `world`, `field`, `demon`

        All `type` commands can be used in DMs.

        """
        await get_bosses_by_type('field')

    # @field.error
    # async def field_error(ctx, error):
    #     await invalid_boss(ctx, error)

    @boss.command(
        aliases=[
            'd',
            'dl',
            ],
        )
    @checks.if_boss_valid(all_valid=True)
    async def demon(self, ctx):
        """Prints a message with all Demon Lord Bosses.

        Possible `type` subcommands: `world`, `field`, `demon`

        All `type` commands can be used in DMs.

        """
        await get_bosses_by_type('demon')

    # @demon.error
    # async def demon_error(ctx, error):
    #     await invalid_boss(ctx, error)

    # I have no idea if decorator stacking is even valid
    # with .error. TIAS!
    @world.error
    @field.error
    @demon.error
    async def boss_type_error(ctx, error):
        await invalid_boss(ctx, error)

    @tasks.loop(minutes=1)
    async def boss_timer_check(self):
        loop_time = pendulum.now()
        for rec_hash, rec_time in self.records.items():
            rec_diff = loop_time - rec_time
            if rec_diff.minutes > 15:
                del self.records[rec_hash]

        for guild_id, guild_db in self.guilds.items():
            messages = []

            results = await guild_db.check_db_boss()
            if not results:
                continue

            diff_h, diff_m = await vaivora.common.get_time_diff(guild_id)
            full_diff = timedelta(hours=diff_h, minutes=diff_m)

            # Sort by time - year, month, day, hour, minute
            results.sort(key=itemgetter(5,6,7,8,9))

            for result in results:
                discord_channel = result[4]
                boss, channel, kill_map, status = [str(r) for r in result[0:4]]

                try:
                    entry_time = pendulum.datetime(
                        *[int(t) for t in result[5:10]],
                        tz=loop_time.timezone_name
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
        for guild in self.guilds.items():
            try:
                await guild_db.check_if_valid('boss')
            except vaivora.db.InvalidDBError as e:
                await guild_db.create_db('boss')

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Add a new guild to background processing.

        Args:
            guild_id (int): the Discord guild's ID

        """
        self.guilds[guild.id] = vaivora.db.Database(guild.id)


def setup(bot):
    bot.add_cog(BossCog(bot))
