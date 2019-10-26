import asyncio
from inspect import cleandoc

import discord
from discord.ext import commands

from vaivora.common import chunk_messages, COG_LOAD_ERRORS


reload_cogs = [
    'cogs.settings',
    'cogs.boss',
    'cogs.meme',
    'cogs.gems',
    'cogs.offset',
    'cogs.events',
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
        aliases=[
            'reloadall',
            'reloadAll',
            ],
        )
    async def reload_all(self, ctx):
        return await self.reloader(ctx, reload_cogs)

    async def reloader(self, ctx, cogs: list) -> bool:
        failed = []
        for cog in cogs:
            if cog == 'cogs.admin':
                failed.append(f'Cannot reload admin cog.')
            else:
                try:
                    self.bot.unload_extension(cog)
                except commands.ExtensionNotLoaded:
                    pass # It's not loaded, so ignore.

                try:
                    self.bot.load_extension(cog)
                except COG_LOAD_ERRORS as e:
                    failed.append(f'{cog}: {e}')
                except commands.ExtensionAlreadyLoaded:
                    pass # It's already loaded. Ignore.

        if not failed:
            await ctx.message.add_reaction('✅')
            return True
        else:
            await ctx.message.add_reaction('❌')
            await ctx.author.send(
                cleandoc(
                    f"""Could not reload the following cogs:

                    - {bullet_point.join(failed)}
                    """
                    )
                )
            return False

    @admin.command(
        aliases=[
            'getID',
            'getIDs',
            'get_id'
            ],
        )
    async def get_ids(self, ctx) -> None:
        members = [
            f'{member}\t\t\t{member.id}'
            for member
            in ctx.guild.members
            ]
        for chunk in await chunk_messages(members, 20, newlines=1):
            async with ctx.typing():
                await asyncio.sleep(1)
                await ctx.author.send(
                    cleandoc(
                        f'```{message}```'
                        )
                    )
        await ctx.message.add_reaction('✅')

    async def cog_check(self, ctx):
        return ctx.author == (await self.bot.application_info()).owner


def setup(bot):
    bot.add_cog(AdminCog(bot))