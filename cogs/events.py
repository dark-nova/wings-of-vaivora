import asyncio
from datetime import timedelta
from inspect import cleandoc
from math import floor
from typing import Optional

import discord
import pendulum
from discord.ext import commands, tasks

import checks
import vaivora.common
import vaivora.db
from vaivora.config import EMOJI, EVENTS_LOGGER as LOGGER


class EventsCog(commands.Cog):
    """Interface for `$events` commands.

    `$events` is an extension to `$settings`.

    This cog interacts with the `vaivora.db` backend.

    """

    def __init__(self, bot):
        self.bot = bot
        self.event_timer_check.start()

    @commands.group(
        aliases=[
            'alert',
            'alerts',
            'event',
            ],
        )
    @checks.only_in_guild()
    @checks.check_channel('settings')
    @checks.check_role()
    async def events(self, ctx):
        pass

    async def name_checker(self, ctx, name):
        """Checks that an event name is valid.

        Called by `add` and `update`.

        The only times a name may not be valid is if it's empty space or
        the name overlaps with a permanent event.

        Args:
            name (str): name of the custom event

        Returns:
            str: if valid
            bool: False otherwise

        """
        name = await vaivora.common.sanitize_nonalnum(name)
        if name in vaivora.db.permanent_events:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You cannot add this event as it has the same name as a permanent event.
                    """
                    )
                )
            return False
        elif not name:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Your custom event name is invalid.
                    """
                    )
                )
            return False
        return name

    async def silent_name_checker(self, name):
        """Checks that a permanent event was matched.

        Called by `enable` and `disable`.

        Serves as the opposite as `name_checker`.

        Args:
            name (str): permanent event name

        Returns:
            str: the matched name
            bool: False if unmatched

        """
        if name in vaivora.db.permanent_events:
            names = vaivora.db.permanent_events
            return names[names.index(name)]

        for event, regex in vaivora.db.aliases.items():
            if regex.search(name):
                return event

        return False

    async def add_handler(self, ctx, name: str, date: str,
        time: Optional[str] = None):
        """Adds a custom event for a Discord guild.

        Called by `add` and `update`.

        Note that the command will fail if
        an event exists with the same name.

        Args:
            name (str): name of the custom event
            date (str): the ending date, in the format of YYYY/MM/DD
            time (Optional[str]): the ending time;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        date = await vaivora.common.validate_date(date)
        if date is None:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Your date was invalid.
                    """
                    )
                )
            return False

        if time:
            time = await vaivora.common.validate_time(time)

        if time is None:
            time = '0:00'

        hour, minutes = [int(x) for x in time.split(':')]
        time = {
            'hour': hour,
            'minutes': minutes
            }

        vdb = vaivora.db.Database(ctx.guild.id)
        if not await vdb.add_custom_event(name, date, time):
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    'Your custom event could not be added.

                    Verify if it already exists.
                    You may also be at the limit of 15 events.
                    """
                    )
                )
            return False
        else:
            if not await vdb.check_events_channel():
                await ctx.send(
                    'Please ensure you add at least 1 channel marked '
                    'as "events". Otherwise, alerts will not show.'
                    )
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    'Your custom event **{name}** was added with an ending date """
                    f"""of **{date['year']}/{date['month']}/{date['day']}**.
                    """
                    )
                )
            return True

    @events.command()
    async def add(self, ctx, name: str, date: str, time: Optional[str] = None):
        """Adds a custom event for a Discord guild.

        See `add_handler`.

        Args:
            name (str): name of the custom event
            date (str): the ending date, in the format of YYYY/MM/DD
            time (Optional[str]): the ending time;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        name = await self.name_checker(ctx, name)
        if not name:
            return False
        return await self.add_handler(ctx, name, date, time)

    @events.command()
    async def update(self, ctx, name: str, date: str,
        time: Optional[str] = None):
        """Updates a custom event for a Discord guild.

        See `add_handler`.

        Args:
            name (str): name of the custom event
            date (str): the ending date, in the format of YYYY/MM/DD
            time (Optional[str]): the ending time;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        name = await self.name_checker(ctx, name)
        if not name:
            return False
        vdb = vaivora.db.Database(ctx.guild.id)
        if not await vdb.verify_existing_custom_event(name):
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You cannot update nonexistent events.
                    """
                    )
                )
            return False
        return await self.add_handler(ctx, name, date, time)

    @events.command(
        aliases=[
            'del',
            'rm',
            ],
        )
    async def delete(self, ctx, name: str):
        """Deletes a custom event for a Discord guild.

        Args:
            name (str): the name of the custom event

        Returns:
            bool: True if successful; False otherwise

        """
        name = await self.name_checker(ctx, name)
        if not name:
            return False
        vdb = vaivora.db.Database(ctx.guild.id)
        if not await vdb.del_custom_event(name):
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You cannot update nonexistent events.
                    """
                    )
                )
            return False
        else:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Your custom event **{name}** has been successfully deleted.
                    """
                    )
                )
            return False

    @events.command(
        name='list',
        aliases=[
            'ls',
            ],
        )
    async def _list(self, ctx):
        """Lists all events for a Discord guild.

        Args:
            name (str): the name of the custom event

        Returns:
            bool: True if successful; False otherwise

        """
        vdb = vaivora.db.Database(ctx.guild.id)
        results = await vdb.list_all_events()
        if not results:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    No events were found. Verify file permissions.
                    """
                    )
                )
            return False

        output = []

        diff_h, diff_m = await vaivora.common.get_time_diff(ctx.guild.id)
        full_diff = timedelta(hours=diff_h, minutes=diff_m)

        now = pendulum.now()

        for result in results:
            status = ''
            name = result[0]
            time = result[1:-1]

            if name in vaivora.db.permanent_events:
                today = pendulum.today()
                to_add = (vaivora.db.event_days[name] - today.day_of_week) % 7
                next_day = today + timedelta(days=to_add)
                time = [
                    next_day.year,
                    next_day.month,
                    next_day.day,
                    *vaivora.db.event_times[name]
                    ]
                status = '✅' if result[-1] == 1 else '❌'
                name = f'{name} ({status})'

            try:
                entry_time = pendulum.datetime(
                    *time, tz=now.timezone_name
                    )
            except ValueError as e:
                LOGGER.error(
                    f'Caught {e} in cogs.events: _list; '
                    f'guild: {ctx.guild.id}; '
                    f'user: {ctx.author.id}; '
                    f'command: {ctx.command}'
                    )
                continue

            time_diff = entry_time - (now + full_diff)
            diff_days = abs(time_diff.days)

            time_as_text = []

            # Print days conditionally
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
                time_since = f"""{', '.join(time_since)}, {time_since}"""

            ending = 'ending' if int(time_diff.seconds) >= 0 else 'ended'

            if status:
                ending = 'resets'

            end_date = entry_time.strftime("%Y/%m/%d %H:%M")

            message = cleandoc(
                f"""**{name}**
                - {ending} at **{end_date}** ({time_since})
                """
                )
            output.append(message)

        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                Records:
                """
                )
            )
        for message in await vaivora.common.chunk_messages(output, 5):
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.send(message)

        return True

    @events.command(
        aliases=[
            'en',
            ],
        )
    async def enable(self, ctx, name: str):
        """Enables a permanent event.

        Args:
            name (str): the name of the permanent event

        Returns:
            bool: True if successful; False otherwise

        """
        name = await self.silent_name_checker(name)
        if not name:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You entered an invalid permanent event name.
                    """
                    )
                )
        vdb = vaivora.db.Database(ctx.guild.id)
        if not await vdb.enable_event(name):
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Your command could not be processed.
                    The **{name}**'s state could not be enabled.
                    """
                    )
                )
            return False
        else:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You have successfully enabled the **{name}** permanent event.
                    """
                    )
                )
            return True

    @events.command(
        aliases=[
            'dis',
            ],
        )
    async def disable(self, ctx, name: str):
        """Disables a permanent event.

        Args:
            name (str): the name of the permanent event

        Returns:
            bool: True if successful; False otherwise

        """
        name = await self.silent_name_checker(name)
        if not name:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You entered an invalid permanent event name.
                    """
                    )
                )
        vdb = vaivora.db.Database(ctx.guild.id)
        if not await vdb.disable_event(name):
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Your command could not be processed.
                    The **{name}**'s state could not be disabled.
                    """
                    )
                )
            return False
        else:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You have successfully disabled the **{name}** permanent event.
                    """
                    )
                )
            return True

    @tasks.loop(minutes=1)
    async def event_timer_check(self):
        loop_time = pendulum.now()
        for rec_hash, rec_time in self.records.items():
            rec_diff = loop_time - rec_time
            if rec_diff.hours < 1 or (
                rec_diff.hours == 1
                and rec_diff.minutes < 1
                ):
                continue
            else:
                del self.records[rec_hash]

        for guild_id, guild_db in self.guilds.items():
            messages = []

            results = await guild_db.list_all_events()
            if not results:
                continue

            channels = await guild_db.get_channels(
                'events'
                )
            if not channels:
                continue

            diff_h, diff_m = await vaivora.common.get_time_diff(guild_id)
            full_diff = timedelta(hours=diff_h, minutes=diff_m)

            # Sort by time - year, month, day, hour, minute
            results.sort(key=itemgetter(5,6,7,8,9))

            for result in results:
                try:
                    entry_time = pendulum.datetime(
                        *[int(t) for t in result[1:-1]],
                        tz=loop_time.timezone_name
                        )
                except ValueError as e:
                    LOGGER.error(
                        f'Caught {e} in cogs.events: event_timer_check; '
                        f'guild: {guild_id}; '
                        f'user: {ctx.author.id}; '
                        f'command: {ctx.command}'
                        )
                    continue

                end_date = entry_time.strftime("%Y/%m/%d %H:%M")

                time_diff = entry_time - (loop_time + full_diff)
                # Record is in the past if any of the below conditions match
                if (time_diff.hours < 0
                    or time_diff.minutes < 0
                    or time_diff.days != 0
                    ):
                    continue

                mins = f'{time_diff.minutes} minute'
                if time_diff.minutes != 1:
                    mins = f'{mins}s'

                name = result[0]
                if name in vaivora.db.permanent_events:
                    # If a permanent event is disabled, simply skip it
                    if result[-1] == 0:
                        continue
                    today = pendulum.today()
                    to_add = (
                        vaivora.db.event_days[name]
                        - today.day_of_week
                        + 7
                        ) % 7
                    next_occurrence = today + timedelta(days=to_add)
                    time = [
                        next_occurrence.year,
                        next_occurrence.month,
                        next_occurrence.day,
                        *vaivora.db.event_times[name]
                        ]
                    name = f"""{name} {EMOJI['alert']}"""

                record = cleandoc(
                    f"""**{name}**
                    - {ending} at **{end_date}** ({mins})"""
                    )
                hashed_record = await vaivora.common.hash_object(
                    channels,
                    name,
                    entry_time
                    )

                if hashed_record in self.records:
                    continue

                # Record is within 1 hour behind the loop time
                if time_diff.seconds <= 3600 and time_diff.seconds > 0:
                    for channel in channels:
                        messages.append(
                            {
                                'record': record,
                                'discord_channel': channel
                                }
                            )
                        self.records[hashed_record] = entry_time

            if not messages:
                continue
            else:
                await vaivora.common.send_messages(
                    self.bot.get_guild(guild_id),
                    messages,
                    'events'
                    )

    @event_timer_check.before_loop
    async def before_event_timer_check(self):
        self.records = {}
        await self.bot.wait_until_ready()
        print('Checking guilds for event background check...')
        self.guilds = {
            guild.id: vaivora.db.Database(guild.id)
            for guild
            in self.bot.guilds
            if not guild.unavailable
            }
        for guild_id, guild_db in self.guilds.items():
            if not await guild_db.init_events():
                print(
                    cleandoc(
                        f"""...event check failed!
                        Removing guild with ID {guild_id} from loop"""
                        )
                    )
                del self.guilds[guild_id]
        print(f'Added {len(self.guilds)} guilds to event background check!')

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        """Add a new guild to background processing.

        Args:
            guild_id (int): the Discord guild's ID

        """
        self.guilds[guild.id] = vaivora.db.Database(guild.id)


def setup(bot):
    bot.add_cog(EventsCog(bot))
