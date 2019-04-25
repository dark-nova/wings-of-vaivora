import asyncio

import discord
from discord.ext import commands


_cogs = ['cogs.settings',
         'cogs.boss',
         'cogs.meme',
         'cogs.gems',
         'cogs.offset',
         'cogs.events'
         ]


class AdminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def admin(self, ctx):
        pass

    @admin.command()
    async def reload(self, ctx, *cogs):
        return await self.reloader(ctx, cogs)

    @admin.command(aliases=['reloadAll', 'reloadall'])
    async def reload_all(self, ctx):
        return await self.reloader(ctx, _cogs)

    async def reloader(self, ctx, cogs):
        failed = []
        for cog in cogs:
            try:
                if cog == 'cogs.admin':
                    raise Exception
                self.bot.unload_extension(cog)
                self.bot.load_extension(cog)
            except Exception as e:
                failed.append('{}: {}'.format(cog, e))
        if not failed:
            await ctx.message.add_reaction('✅')
            return True
        else:
            await ctx.message.add_reaction('❌')
            try:
                await ctx.author.send(
                    'Could not reload the following cogs:\n\n- {}'
                    .format('\n- '.join(failed)))
            except Exception as e:
                await ctx.author.send(
                    'Exception: {}'.format(e))
            return False

    @admin.command(aliases=['getIDs', 'getID', 'get_id'])
    async def get_ids(self, ctx):
        try:
            members = ['{}\t\t\t{}'.format(member, member.id)
                       for member in ctx.guild.members]
            while len(members) > 20:
                await ctx.author.send('```{}```'.format(
                    '\n'.join(members[0:20])))
                members = members[20:]
            if len(members) > 0:
                await ctx.author.send('```{}```'.format(
                    '\n'.join(members)))
            await ctx.message.add_reaction('✅')
            return True
        except Exception as e:
            await ctx.message.add_reaction('❌')
            await ctx.author.send(e)
            return False

    async def cog_check(self, ctx):
        return ctx.author == (await self.bot.application_info()).owner


def setup(bot):
    bot.add_cog(AdminCog(bot))