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
        """Sends a meme image.

        Args:

        Returns:
            bool: True if successful; False otherwise

        """
        try:
            await ctx.send(
                f'{ctx.author.mention} https://i.imgur.com/kW3o6eC.png'
                )
        except Exception as e:
            LOGGER.error(
                f'Caught {e} in cogs.meme: please; '
                f'guild: {ctx.guild.id}; '
                f'channel: {ctx.channel.id}; '
                f'user: {ctx.author.id}'
                )
            return False

        return True


def setup(bot):
    bot.add_cog(MemeCog(bot))