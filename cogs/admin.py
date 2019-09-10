import asyncio
from inspect import cleandoc

import discord
from discord.ext import commands


reload_cogs = [
    'cogs.settings',
    'cogs.boss',
    'cogs.meme',
    'cogs.gems',
    'cogs.offset',
    'cogs.events'
    ]

newline = '\n'
bullet_point = '\n- '


class AdminCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def admin(self, ctx):
        pass

    @admin.command()
    async def reload(self, ctx, *cogs):
        return await self.reloader(ctx, cogs)

    @admin.command(
        aliases = [
            'reloadall',
            'reloadAll',
            ]
        )
    async def reload_all(self, ctx):
        return await self.reloader(ctx, reload_cogs)

    async def reloader(self, ctx, cogs):
        failed = []
        for cog in cogs:
            try:
                if cog == 'cogs.admin':
                    raise Exception
                self.bot.unload_extension(cog)
                self.bot.load_extension(cog)
            except Exception as e:
                failed.append(f'{cog}: {e}')
        if not failed:
            await ctx.message.add_reaction('✅')
            return True
        else:
            await ctx.message.add_reaction('❌')
            try:
                await ctx.author.send(
                    cleandoc(
                        f"""Could not reload the following cogs:

                        - {bullet_point.join(failed)}
                        """
                        )
                    )
            except Exception as e:
                await ctx.author.send(
                    f'Exception: {e}'
                    )
            return False

    @admin.command(
        aliases = [
            'getID',
            'getIDs',
            'get_id'
            ]
        )
    async def get_ids(self, ctx):
        try:
            members = [
                f'{member}\t\t\t{member.id}'
                for member
                in ctx.guild.members
                ]
            while len(members) > 20:
                await ctx.author.send(
                    cleandoc(
                        f"""```
                        {newline.join(members[0:20])}
                        ```
                        """
                        )
                    )
                members = members[20:]
            if len(members) > 0:
                await ctx.author.send(
                    cleandoc(
                        f"""```
                        {newline.join(members)}
                        ```
                        """
                        )
                    )
            await ctx.message.add_reaction('✅')
            return True
        except Exception as e:
            await ctx.message.add_reaction('❌')
            await ctx.author.send(
                f'Exception: {e}'
                )
            return False

    async def cog_check(self, ctx):
        return ctx.author == (await self.bot.application_info()).owner


def setup(bot):
    bot.add_cog(AdminCog(bot))