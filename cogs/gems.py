import discord
from discord.ext import commands

import checks


class GemsCog:

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def gems(self, ctx)
        pass

def setup(bot):
    bot.add_cog(GemsCog(bot))
