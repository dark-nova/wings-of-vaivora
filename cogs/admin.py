import asyncio

import discord
from discord.ext import commands


_cogs = ['cogs.settings',
         'cogs.boss',
         'cogs.meme',
         'cogs.gems',
         'cogs.offset']


class AdminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def admin(self, ctx):
        pass

    @admin.command()
    async def reload(ctx):
        failed = []
        for _cog in _cogs:
            try:
                bot.load_extension(_cog)
            except Exception as e:
                failed.append(_cog)
        if not failed:
            await ctx.message.add_reaction('✅')
            return True
        else:
            await ctx.message.add_reaction('❌')
            await ctx.author.send('Could not reload the following cogs:\n\n- {}'
                                  .format('\n- '.join(failed)))
            return False

    @admin.command(aliases=['getIDs', 'getID', 'get_id'])
    async def get_ids(ctx):
        try:
            members = ['{}\t\t{}'.format(member, member.id)
                       for member in ctx.guild.members]
            while len(members) > 20:
                await ctx.author.send('\n'.join(members[0:20]))
                members = members[20:]
            if len(members) > 0:
                await ctx.author.send('\n'.join(members))
            await ctx.message.add_reaction('✅')
            return True
        except Exception as e:
            await ctx.message.add_reaction('❌')
            await ctx.author.send(e)
            return False

    async def cog_check(self, ctx):
        return ctx.author == (await bot.application_info()).owner


def setup(bot):
    bot.add_cog(AdminCog(bot))