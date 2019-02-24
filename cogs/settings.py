import re
import os
import os.path
import json
import asyncio
import aiosqlite
import typing
from itertools import chain
from typing import Optional

import discord
from discord.ext import commands

import checks
import vaivora.db
from secrets import discord_user_id
import constants.settings


class SettingsCog:

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.group()
    async def settings(self, ctx):
        pass

    @settings.command(name='help')
    async def _help(self, ctx):
        """
        :func:`_help` retrieves help pages for `$settings`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True
        """
        _help = constants.settings.HELP
        for _h in _help:
            await ctx.author.send(_h)
        return True

    @settings.command()
    @checks.only_in_guild()
    @checks.check_role()
    async def purge(self, ctx):
        """
        :func:`purge` is a last-resort subcommand that
        resets the channels table.

        Returns:
            True if successful; False otherwise
        """
        vdb = vaivora.db.Database(ctx.guild.id)
        success = await vdb.purge()
        if success:
            await ctx.send('{} {}'.format(ctx.author.mention,
                                          constants.settings.SUCCESS_PURGED))
            return True
        else:
            await ctx.send('{} {}'.format(ctx.author.mention,
                                          constants.settings.FAIL_PURGED))
            return False

    # $settings set <target> <kind> <discord object>
    @settings.group(name='set')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def _set(self, ctx):
        """
        :func:`set` sets `target`s to `kind`s.
        e.g. sets a channel (target) to boss (kind)

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return True

    @_set.group(name='channel')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def s_channel(self, ctx):
        """
        :func:`s_channel` sets channels to `kind`s.
        e.g. sets a channel (target) to boss (kind)

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True always
        """
        ctx.channel_kind = ctx.invoked_subcommand.name
        return True

    @s_channel.command(name='settings')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    @checks.has_channel_mentions()
    async def sc_settings(self, ctx):
        """
        :func:`sc_settings` sets channels to `settings`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return await self.channel_setter(ctx, ctx.channel_kind)

    @s_channel.command(name='boss')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    @checks.has_channel_mentions()
    async def sc_boss(self, ctx):
        """
        :func:`sc_boss` sets channels to `boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return await self.channel_setter(ctx, ctx.channel_kind)

    async def channel_setter(self, ctx, kind):
        """
        :func:`channel_setter` does the work
        for :func:`sc_boss` and :func:`sc_settings`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            kind (str): the kind/type to use, i.e. subcommand invoked

        Returns:
            True if successful; False otherwise
        """
        channels = []
        for channel_mention in ctx.message.channel_mentions:
            channels.append(str(channel_mention.id))
        vdb = vaivora.db.Database(self, ctx.guild.id)
        errs = []

        for _channel in channels:
            try:
                await vdb.set_channel(kind, _channel)
            except:
                errs.append(_channel)

        if not errs:
            await ctx.send(constants.settings.SUCCESS
                           .format(constants.settings.TABLE_CHANNEL,
                                kind))
        else:
            await ctx.send(constants.settings.PARTIAL_SUCCESS
                           .format(constants.settings.TABLE_CHANNEL,
                                '\n'.join(errs)))
        return True

    @_set.group(name='role')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def s_role(self, ctx):
        """
        :func:`s_role` sets `role`s to `kind`s.
        e.g. sets a channel (target) to boss (kind)

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True always
        """
        ctx.role_kind = ctx.invoked_subcommand.name
        return True

    @s_role.group(name='member')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def sr_member(self, ctx, mentions: Optional[int] = None):
        """
        :func:`sr_member` sets roles of members.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise      
        """
        return await self.role_setter(ctx, mentions)

    @s_role.group(name='authorized')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def sr_auth(self, ctx, mentions: Optional[int] = None):
        """
        :func:`sr_member` sets roles of members.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise      
        """
        return await self.role_setter(ctx, mentions)

    @s_role.group(name='boss')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def sr_boss(self, ctx, mentions: Optional[int] = None):
        """
        :func:`sr_member` sets roles of members.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise      
        """
        return await self.role_setter(ctx, mentions)

    async def role_setter(self, ctx, mentions=None):
        """
        :func:`role_setter` handles the backend for
        :func:`sr_member`, :func:`sr_auth`, and :func:`sr_boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions: (default: None) optional mentions that are only id's

        Returns:
            True if successful; False otherwise
        """
        _mentions = []

        if ctx.message.mentions:
            for mention in ctx.message.mentions:
                _mentions.append(mention)

        # uid mode; parse if they're actually id's and not nonsense
        if mentions:
            gids = [member.id for member in (ctx.guild.members
                                             + ctx.guild.roles)]
            rids = [member.id for member in ctx.guild.role]
            if ctx.role_kind == constants.settings.ROLE_BOSS:
                for mention in mentions:
                     # do not allow regular users for $boss
                    if mention in rids:
                        _mention.append(mention)
            else:
                for mention in mentions:
                    if mention in gids:
                        _mentions.append(mention)

        if not _mentions:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings.FAIL_NO_MENTIONS))

        print(mentions)

def setup(bot):
    bot.add_cog(SettingsCog(bot))