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


async def get_ids(ctx, mentions):
        """
        :func:`get_ids` filters out nonsense ints with actual id's.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions: mentions to test for id's.

        Returns:
            list: of valid discord id's
        """
        if type(mentions) is int:
            mentions = [mentions]

        _mention = []
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

        return _mention


async def channel_getter(ctx, kind):
        """
        :func:`channel_getter` does the work
        for :func:`gc_boss` and :func:`gc_settings`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            kind (str): the kind/type to use, i.e. subcommand invoked

        Returns:
            True always
        """
        vdb = vaivora.db.Database(ctx.guild.id)
        channels = await vdb.get_channel(kind)

        if not channels:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings.FAIL_NO_CHANNELS
                                   .format(kind)))
        else:
            channels = '\n'.join([str(ctx.guild.get_channel(channel))
                                  for channel in channels])
            channels = [ctx.guildchannel for channel in channels]
            await ctx.send('{}\n\n{}'
                           .format(ctx.author.mention,
                                   constants.settings.SUCCESS_CHANNELS
                                   .format(kind, channels)))
        return True


async def channel_setter(ctx, kind):
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
        vdb = vaivora.db.Database(ctx.guild.id)
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


async def role_getter(ctx, mentions=None):
        """
        :func:`role_getter` handles the backend for
        :func:`gr_member`, :func:`gr_auth`, and :func:`gr_boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions: (default: None) optional mentions that are only id's

        Returns:
            True if successful; False otherwise
        """
        _mentions = []

        if ctx.message.role_mentions:
            for mention in ctx.message.role_mentions:
                _mentions.append(mention.id)

        # do not allow regular users for $boss
        if ctx.role_kind != constants.settings.ROLE_BOSS:
            if ctx.message.mentions:
                for mention in ctx.message.mentions:
                    _mentions.append(mention.id)

        else:
            if not ctx.message.role_mentions and ctx.message.mentions:
                await ctx.send('{} {}'
                               .format(ctx.author.mention,
                                       constants.settings.FAIL_NO_USER_BOSS))
                return False

        # uid mode; parse if they're actually id's and not nonsense
        if mentions:
            _mentions.append(await get_ids(ctx, mentions))

        vdb = vaivora.db.Database(ctx.guild.id)
        users = await vdb.get_users(ctx.role_kind, _mentions)

        if users:
            if _mentions:
                users = [user for user in users if user in _mentions]
            users = '\n'.join([str(ctx.guild.get_member(user))
                               for user in users])
            users = '```\n{}```'.format(users)
            await ctx.send('{}\n\n{}'.format(
                    ctx.author.mention,
                    constants.settings.SUCCESS_ROLES.format(
                        ctx.role_kind, users),
                    constants.settings.NOTICE_ROLE))
            return True
        else:
            await ctx.send('{} {}'.format(
                    ctx.author.mention,
                    constants.settings.FAIL_NO_ROLES.format(
                        ctx.role_kind)))
            return False


async def role_setter(ctx, mentions=None):
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

        if ctx.message.role_mentions:
            for mention in ctx.message.role_mentions:
                _mentions.append(mention.id)

        # do not allow regular users for $boss
        if ctx.role_kind != constants.settings.ROLE_BOSS:
            if ctx.message.mentions:
                for mention in ctx.message.mentions:
                    _mentions.append(mention.id)

        # uid mode; parse if they're actually id's and not nonsense
        if mentions:
            _mentions.append(await get_ids(ctx, mentions))

        if not _mentions:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings.FAIL_NO_MENTIONS))
            return False

        vdb = vaivora.db.Database(ctx.guild.id)
        errs = await vdb.set_users(ctx.role_kind, _mentions)

        if errs:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings.PARTIAL_SUCCESS.format(
                                        constants.settings.SETTING_SET,
                                        '\n'.join(errs))))
        else:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings.SUCCESS_ROLES_UP.format(
                                        ctx.role_kind)))

        return True


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

    @_set.group(name='channel', aliases=['ch', 'chs', 'chan',
                                         'chans', 'channels'])
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
        return await channel_setter(ctx, ctx.channel_kind)

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
        return await channel_setter(ctx, ctx.channel_kind)

    @_set.group(name='role', aliases=['roles', 'user', 'users'])
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def s_role(self, ctx):
        """
        :func:`s_role` sets `role`s to `kind`s.
        e.g. sets a member (target) to role boss (kind)

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
        return await role_setter(ctx, mentions)

    @s_role.group(name='authorized', aliases=['auth'])
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
        return await role_setter(ctx, mentions)

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
        return await role_setter(ctx, mentions)

    @_set.group(name='talt', aliases=['points', 'pt', 'pts',
                                      'contrib', 'contribs',
                                      'contribution'])
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def s_talt(self, ctx, points: int,
                     unit=constants.settings.CMD_ARG_SETTING_TALT_POINTS,
                     member=None):
        """
        :func:`s_talt` sets contribution points.
        Optionally, if a member is mentioned, then the member's record
        will be modified instead.
        If using the `member` variable, take care to fill in all arguments.
        e.g. $settings set talt 20 talt @someone

        Args:
            ctx (discord.ext.commands.Context): context of the message
            points (int): the points to add; i.e. 1 talt = 20 points, etc
            unit: (default: constants.settings.CMD_ARG_SETTING_TALT_UNIT)
                unit to pick
            member: (default: None) the optional member's record to modify

        Returns:
            True if successful; False otherwise
        """
        mention = 0
        if (constants.settings
            .REGEX_CONTRIBUTION_POINTS.search(unit)):
            if points % 20 != 0:
                await ctx.send('{} {}'
                               .format(ctx.author.mention,
                                       constants.settings
                                       .FAIL_INVALID_POINTS))
                return False
        # just assume it's talt
        else:
            points *= 20

        if ctx.message.mentions:
            if len(ctx.message.mentions) > 1:
                await ctx.send('{} {}'
                               .format(ctx.author.mention,
                                       constants.settings
                                       .FAIL_TOO_MANY_MENTIONS))
                return False
            else:
                mention = ctx.message.mentions[0]

        if member and mention:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings
                                   .FAIL_TOO_MANY_MENTIONS))
            return False
        elif member:
            mention = (await get_ids(ctx, member))[0]

        if not member:
            member = ctx.author.id

        vdb = vaivora.db.Database(ctx.guild.id)
        return await vdb.set_contribution(member, points)

    # $settings get <target> <kind> <discord object>
    @settings.group(name='get')
    @checks.only_in_guild()
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def _get(self, ctx):
        """
        :func:`_get` gets `target`s to `kind`s.
        e.g. sets a channel (target) to boss (kind)

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return True

    @_get.group(name='channel', aliases=['ch', 'chs', 'chan',
                                         'chans', 'channels'])
    @checks.only_in_guild()
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def g_channel(self, ctx):
        """
        :func:`g_channel` gets channels of `kind`.
        e.g. gets a channel (target) of boss (kind)

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True always
        """
        ctx.channel_kind = ctx.invoked_subcommand.name
        return True

    @g_channel.command(name='settings')
    @checks.only_in_guild()
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def gc_settings(self, ctx):
        """
        :func:`gc_settings` gets channels that are `settings`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True always
        """
        return await channel_getter(ctx, ctx.channel_kind)

    @g_channel.command(name='boss')
    @checks.only_in_guild()
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def gc_boss(self, ctx):
        """
        :func:`gc_boss` gets channels that are `boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True always
        """
        return await channel_getter(ctx, ctx.channel_kind)

    @_get.group(name='role', aliases=['roles', 'user', 'users'])
    @checks.only_in_guild()
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def g_role(self, ctx):
        """
        :func:`g_role` gets `role`s of `kind`.
        e.g. gets a member (target) of role boss (kind)

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True always
        """
        ctx.role_kind = ctx.invoked_subcommand.name
        return True

    @g_role.group(name='member')
    @checks.only_in_guild()
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def gr_member(self, ctx, mentions: Optional[int] = None):
        """
        :func:`gr_member` gets members of role `member`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return await role_getter(ctx, mentions)

    @g_role.group(name='authorized', aliases=['auth'])
    @checks.only_in_guild()
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def gr_auth(self, ctx, mentions: Optional[int] = None):
        """
        :func:`gr_auth` gets members of role `authorized`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return await role_getter(ctx, mentions)

    @g_role.group(name='boss')
    @checks.only_in_guild()
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def gr_boss(self, ctx, mentions: Optional[int] = None):
        """
        :func:`gr_boss` gets members of role `boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return await role_getter(ctx, mentions)

    @_get.group(name='talt', aliases=['points', 'pt', 'pts',
                                      'contrib', 'contribs',
                                      'contribution'])
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def g_talt(self, ctx, mentions: Optional[int] = None):
        pass

    

def setup(bot):
    bot.add_cog(SettingsCog(bot))