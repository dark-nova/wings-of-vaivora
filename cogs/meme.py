import discord
from discord.ext import commands

from vaivora.config import MEME_LOGGER as LOGGER


class MemeCog(commands.Cog):
    """Sends memes."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=[
            'ples',
            'pls',
            'plz',
            ]
        )
    async def please(self, ctx):
        """Sends a meme image."""
        await ctx.send(
            f'{ctx.author.mention} https://i.imgur.com/kW3o6eC.png'
            )


def setup(bot):
    bot.add_cog(MemeCog(bot))