from typing import Optional
from datetime import timedelta

import discord
from discord.ext import commands
import pendulum

import checks
import vaivora.db
import vaivora.utils
import constants.events


class EventsCog(commands.Cog):
    """Interface for `$events` commands.

    `$events` is an extension to `$settings`.

    This cog interacts with the `vaivora.db` backend.

    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['event', 'alerts', 'alert'])
    async def events(self, ctx):
        pass

    async def name_checker(self, ctx, name):
        """Checks that an event name is valid.

        Called by `add` and `update`.

        The only times a name may not be valid is if it's empty space or
        the name overlaps with a permanent event.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            name (str): name of the custom event

        Returns:
            str: if valid
            bool: False otherwise

        """
        name = await vaivora.utils.sanitize_nonalnum(name)
        if name in vaivora.db.permanent_events:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.events.FAIL_EVENT_NAME))
            return False
        elif not name:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.events.FAIL_EVENT_NAME_INVALID))
            return False
        return name

    async def add_handler(self, ctx, name: str, date: str, time: Optional[str] = None):
        """Adds a custom event for a Discord guild.

        Called by `add` and `update`.

        Note that the command will fail if
        an event exists with the same name.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            name (str): name of the custom event
            date (str): the ending date, in the format of YYYY/MM/DD
            time (Optional[str]): the ending time;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        date = await vaivora.utils.validate_date(date)
        if date is None:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.events.FAIL_INVALID_DATE))
            return False

        if time:
            time = await vaivora.utils.validate_time(time)

        if time is None:
            time = '0:00'

        hour, minutes = [int(x) for x in time.split(':')]
        time = {
            'hour': hour,
            'minutes': minutes
        }

        vdb = vaivora.db.Database(ctx.guild.id)
        if not await vdb.add_custom_event(name, date, time):
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.events.FAIL_EVENT_ADD))
            return False
        else:
            if not await vdb.check_events_channel():
                await ctx.send(constants.events.NO_CHANNELS)
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.events.SUCCESS_EVENT_ADD
                                   .format(name,
                                           '/'.join(str(v) for v in
                                                    date.values()))))
            return True

    @events.command()
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def add(self, ctx, name: str, date: str, time: Optional[str] = None):
        """Adds a custom event for a Discord guild.

        See `add_handler`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
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
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def update(self, ctx, name: str, date: str,
        time: Optional[str] = None):
        """Updates a custom event for a Discord guild.

        See `add_handler`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
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
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.events.FAIL_EVENT_UPDATE))
            return False
        return await self.add_handler(ctx, name, date, time)

    @events.command(aliases=['del', 'rm'])
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def delete(self, ctx, name: str):
        """Deletes a custom event for a Discord guild.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            name (str): the name of the custom event

        Returns:
            bool: True if successful; False otherwise

        """
        name = await self.name_checker(ctx, name)
        if not name:
            return False
        vdb = vaivora.db.Database(ctx.guild.id)
        if not await vdb.del_custom_event(name):
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.events.FAIL_EVENT_UPDATE))
            return False
        else:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.events.SUCCESS_EVENT_DEL
                                   .format(name)))
            return False

    @events.command(name='list', aliases=['ls'])
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def _list(self, ctx):
        """Lists all events for a Discord guild.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            name (str): the name of the custom event

        Returns:
            bool: True if successful; False otherwise

        """
        vdb = vaivora.db.Database(ctx.guild.id)
        results = await vdb.list_all_events()
        if not results:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.events.FAIL_NO_EVENTS))
            return False

        output = []

        diff_h, diff_m = await vaivora.utils.get_time_diff(ctx.guild.id)
        full_diff = timedelta(hours=diff_h, minutes=diff_m)

        now = pendulum.now()

        for result in results:
            status = result[-1]
            name = result[0]
            time = result[1:-1]
            entry_time = pendulum.datetime(
                *time, tz=now.timezone_name
                )
            time_diff = entry_time - (now + full_diff)

            diff_days = abs(time_diff.days)
            diff_minutes = abs(floor(time_diff.seconds/60))

            if diff_days == 1:
                days = '1 day'
            elif diff_days > 1:
                days = '{} days'.format(diff_days)

            if diff_minutes > 119:
                hours = '{} hours'.format(floor((diff_minutes % 86400)/60))
            elif diff_minutes > 59:
                hours = '1 hour'
            else:
                hours = ''

            # print minutes unconditionally
            # e.g. 0 minutes from now
            # e.g. 59 minutes ago
            diff_minutes = floor(diff_minutes % 60)
            if diff_minutes == 1:
                minutes = '{} minute'.format(diff_minutes)
            else:
                minutes = '{} minutes'.format(diff_minutes)

            when = 'from now' if int(time_diff.seconds) >= 0 else 'ago'

            time_since = '{} {}'.format(minutes, when)
            if hours:
                time_since = '{}, {}'.format(hours, time_since)
            # use diff_days since days may not be instantiated
            if diff_days:
                time_since = '{}, {}'.format(days, time_since)

            ending = 'ending at' if int(time_diff.seconds) >= 0 else 'ended at'

            end_date = entry_time.strftime("%Y/%m/%d %H:%M")

            message = ('**{}**\n- {} at **{}** ({})'
                       .format(name, ending, end_date,
                               time_since))

            output.append(message)
            





def setup(bot):
    bot.add_cog(EventsCog(bot))
