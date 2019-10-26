import logging

import discord
from discord.ext import commands


logger = logging.getLogger('vaivora.cogs.meme')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('vaivora.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


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
            logger.error(
                f'Caught {e} in cogs.meme: please; '
                f'guild: {ctx.guild.id}; '
                f'channel: {ctx.channel.id}; '
                f'user: {ctx.author.id}'
                )
            return False

        return True


def setup(bot):
    bot.add_cog(MemeCog(bot))