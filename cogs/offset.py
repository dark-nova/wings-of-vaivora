import discord
from discord.ext import commands
import pendulum

import checks
import vaivora.db
import constants.offset
import constants.settings


server_tz = [
    'America/New_York',
    'America/Sao_Paulo',
    'Europe/Berlin',
    'Asia/Singapore'
    ]

numbered_tz = [('[{}] {}'.format(x,y)) for (x, y)
               in zip(range(len(server_tz)), server_tz)]

class OffsetCog(commands.Cog):
    """Interface for the `$offset` commands.

    Note that any changes set here will permanently affect
    the `$boss` command!

    `$offset` is an extension to `$settings`.

    This cog interacts with the `vaivora.db` backend.

    """

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.group()
    async def offset(self, ctx):
        pass

    @offset.command(name='help')
    async def _help(self, ctx):
        """Retrieves help pages for `$offset`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True

        """
        _help = constants.offset.HELP
        for _h in _help:
            await ctx.author.send(_h)
        return True

    @offset.group(name='set')
    async def _set(self, ctx):
        pass

    @_set.command(name='tz', aliases=['timezone', 'timezones'])
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def s_tz(self, ctx, tz):
        """Sets the guild time zone.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            tz: a timezone; could be an index of `server_tz`, or a tzstr

        Returns:
            bool: True if successful; False otherwise

        """
        try:
            tz = server_tz[int(tz)]
        except:
            try:
                tz = pendulum.timezone(tz)
            except:
                await ctx.send('{} {}'
                               .format(ctx.author.mention,
                                       constants.offset.FAIL
                                       .format('time zone')))

        vdb = vaivora.db.Database(ctx.guild.id)
        if await vdb.set_tz(tz):
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.offset.SUCCESS
                                   .format('time zone')))
            return True
        else:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.offset.FAIL_DB))
            return False

    @_set.command(name='offset')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def s_offset(self, ctx, offset: int):
        """Sets the offset from the guild time zone.

        Note that offset is not the same as time zone; rather,
        offset is the actual offset from the guild time zone.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            offset (int): the offset to use; -23 <= offset <= 23

        Returns:
            bool: True if successful; False otherwise

        """
        if offset > 23 or offset < -23:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                               constants.offset.FAIL
                               .format('offset')))
            return False

        vdb = vaivora.db.Database(ctx.guild.id)
        if await vdb.set_offset(offset):
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.offset.SUCCESS
                                   .format('offset')))
            return True
        else:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.offset.FAIL_DB))
            return False

    @offset.group(name='get')
    async def _get(self, ctx):
        pass

    @_get.command(name='tz', aliases=['timezone', 'timezones'])
    @checks.only_in_guild()
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def g_tz(self, ctx):
        """Retrieves the guild time zone.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if successful; False otherwise

        """
        vdb = vaivora.db.Database(ctx.guild.id)
        tz = await vdb.get_tz()

        if tz:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.offset.SUCCESS_GET
                                   .format('time zone', tz)))
            return True
        else:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.offset.FAIL_NONE
                                   .format('time zone')))
            return False

    @_get.command(name='offset')
    @checks.only_in_guild()
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def g_offset(self, ctx):
        """Retrieves the guild's offset from the guild time zone.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if successful; False otherwise

        """
        vdb = vaivora.db.Database(ctx.guild.id)
        offset = await vdb.get_offset()

        if offset:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.offset.SUCCESS_GET
                                   .format('offset', offset)))
            return True
        else:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.offset.FAIL_NONE
                                   .format('offset')))
            return False

    @offset.command(name='list')
    async def _list(self, ctx):
        """Lists the available time zones for servers.

        Note that this is locked to the international version of TOS ("ITOS").

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True always

        """
        await ctx.send('{} {}'
                       .format(ctx.author.mention,
                               constants.offset.LIST
                               .format('\n'.join(numbered_tz))))
        return True


def setup(bot):
    bot.add_cog(OffsetCog(bot))
