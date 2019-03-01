import discord
from discord.ext import commands

import checks


abrasives = [0, 0, 300, 1200, 3900, 14700, 57900, 230700, 1094700, 5414700]


class GemsCog:

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def gems(self, ctx)
        pass

    @gems.command()
    async def exp(self, ctx, abrasives: commands.Greedy[str]):
        """
        :func:`exp` calculates the exp obtained from abrasives.
        """
        pass

def setup(bot):
    bot.add_cog(GemsCog(bot))
