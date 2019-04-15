from typing import Optional

import discord
from discord.ext import commands

import checks
import vaivora.db
import vaivora.utils
import constants.events


class EventsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['event', 'alerts', 'alert'])
    async def events(self, ctx):
        pass

    async def name_checker(self, ctx, name):
        """
        :func:`name_checker` makes sure a name is valid.
        The only times a name may not be valid is if it's empty space or
        the name overlaps with a permanent event.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            name (str): name of the custom event

        Returns:
            str: if valid
            False otherwise
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
        """
        :func:`add` adds a custom event for a Discord guild, with
        an ending `date` and an optional ending `time` on that date.
        Note that the command will fail if an event exists with the same name.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            name (str): name of the custom event
            date (str): the ending date, in the format of YYYY/MM/DD
            time (Optional[str]): (default: None) the ending time

        Returns:
            True if successful; False otherwise
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
        """
        :func:`add` adds a custom event for a Discord guild, with
        an ending `date` and an optional ending `time` on that date.
        Note that the command will fail if an event exists with the same name.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            name (str): name of the custom event
            date (str): the ending date, in the format of YYYY/MM/DD
            time (Optional[str]): (default: None) the ending time

        Returns:
            True if successful; False otherwise
        """
        name = await self.name_checker(ctx, name)
        if not name:
            return False
        return await self.add_handler(ctx, name, date, time)

    @events.command()
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def update(self, ctx, name: str, date: str, time: Optional[str] = None):
        """
        :func:`update` updates a custom event for a Discord guild, with
        an ending `date` and an optional ending `time` on that date.
        Note that if no event exists with the given name, the command will fail.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            name (str): name of the custom event
            date (str): the ending date, in the format of YYYY/MM/DD
            time (Optional[str]): (default: None) the ending time

        Returns:
            True if successful; False otherwise
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


def setup(bot):
    bot.add_cog(EventsCog(bot))
