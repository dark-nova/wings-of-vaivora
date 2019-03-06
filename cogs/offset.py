import discord
from discord.ext import commands
import pendulum

import checks
import vaivora.db
import constants.settings


server_tz = [
    'America/New_York',
    'America/Sao_Paulo',
    'Europe/Berlin',
    'Asia/Singapore'
    ]


class OffsetCog:

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def offset(self, ctx, hour):
        pass

    @commands.group(name='set')
    async def _set(self, ctx):
        pass

    @commands.group(name='get')
    async def _get(self, ctx):
        pass

    @commands.group(name='list')
    async def _list(self, ctx):
        pass


def setup(bot):
    bot.add_cog(OffsetCog(bot))
