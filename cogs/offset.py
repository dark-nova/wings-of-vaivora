import discord
from discord.ext import commands
import pendulum

import checks
import vaivora.db
import constants.offset


server_tz = [
    'America/New_York',
    'America/Sao_Paulo',
    'Europe/Berlin',
    'Asia/Singapore'
    ]

numbered_tz = [('[{}] {}'.format(x,y)) for (x, y)
               in zip(range(len(server_tz)), server_tz)]

class OffsetCog:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def offset(self, ctx, hour):
        pass

    @commands.group(name='set')
    async def _set(self, ctx):
        pass

    @_set.command(name='server')
    async def s_server(self, ctx, server):
        try:
            server = server_tz[int(server)]
        except:
            try:
                server = pendulum.timezone(server)
            except:
                await ctx.send('{} {}'
                               .format(ctx.author.mention,
                                       constants.offset.FAIL
                                       .format('server')))
        vdb = vaivora.db.Database(ctx.guild.id)
        channels = await vdb.set_gtz(kind)

    @commands.group(name='get')
    async def _get(self, ctx):
        pass

    @commands.command(name='list')
    async def _list(self, ctx):
        """
        :func:`_list` lists the available time zones for servers.
        Note that this is locked to the international version of TOS ("ITOS").

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True always
        """
        await ctx.send('{} {}'
                       .format(ctx.author.mention,
                               constants.offset.LIST
                               .format('\n'.join(numbered_tz))))
        return True


def setup(bot):
    bot.add_cog(OffsetCog(bot))
