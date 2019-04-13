import discord
from discord.ext import commands

import checks

class EventsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases=['event', 'alerts', 'alert'])
    async def events(self, ctx):
        pass

def setup(bot):
    bot.add_cog(EventsCog(bot))
