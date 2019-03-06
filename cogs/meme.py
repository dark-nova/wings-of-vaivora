import discord
from discord.ext import commands

class MemeCog:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['pls', 'plz', 'ples'])
    async def please(self, ctx):
        """
        :func:`please` is a meme

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        try:
            await ctx.send('{} https://i.imgur.com/kW3o6eC.png'
                           .format(ctx.author.mention))
        except:
            return False

        return True


def setup(bot):
    bot.add_cog(MemeCog(bot))