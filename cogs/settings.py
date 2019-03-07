import re
import os
import os.path
import asyncio
from itertools import chain
from operator import itemgetter
from typing import Optional
from math import floor

import discord
from discord.ext import commands

import checks
import vaivora.db
import constants.settings


async def get_mention_ids(ctx, mentions):
    """
    :func:`get_mention_ids` filters out nonsense ints with actual id's.

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
    rids = [member.id for member in ctx.guild.roles]
    try:
        if ctx.role_kind == constants.settings.ROLE_BOSS:
            for mention in mentions:
                # do not allow regular users for $boss
                if mention in rids:
                    _mention.append(mention)
    except:
        pass

    for mention in mentions:
        if mention in gids:
            _mention.append(mention)

    return _mention


async def combine_mention_ids(ctx, mentions=None):
    """
    :func:`combine_mention_ids` combines all mentions and valid id's.
    Used in :func:`role_setter`, :func:`role_getter`,
    and :func:`role_deleter`.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        mentions: (default: None) optional mentions that are only id's
        boss (bool): (default: False) whether to ignore user id's or not

    Returns:
        list: of mention id's
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
    elif ctx.role_kind == constants.settings.ROLE_BOSS:
        if ctx.message.mentions:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings.FAIL_NO_USER_BOSS))

    print(_mentions)
    # uid mode; parse if they're actually id's and not nonsense
    if mentions:
        _mentions.extend(await get_mention_ids(ctx, mentions))

    return _mentions


async def combine_channel_ids(ctx):
    """
    :func:`combine_channel_ids` combines all channel id's.
    Used in :func:`channel_setter` and :func:`channel_deleter`.

    Args:
        ctx (discord.ext.commands.Context): context of the message

    Returns:
        list: of channel id's
    """
    channels = []
    if not ctx.message.channels_mentions:
        channels.append(ctx.channel.id)
    else:
        for channel_mention in ctx.message.channel_mentions:
            channels.append(str(channel_mention.id))
    return channels


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
        existing_channels = []
        for channel in channels:
            if not ctx.guild.get_channel(channel):
                await vdb.remove_channel(kind, channel)
            else:
                existing_channels.append(
                    str(ctx.guild.get_channel(channel).mention))

        channels = '\n'.join(existing_channels)
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
    channels = await combine_channel_ids(ctx)

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
        errs = [str(err) for err in errs]
        await ctx.send(constants.settings.PARTIAL_SUCCESS
                       .format(constants.settings.TABLE_CHANNEL,
                            '\n'.join(errs)))
    return True


async def channel_deleter(ctx, kind):
    """
    :func:`channel_setter` does the work
    for :func:`sc_boss` and :func:`sc_settings`.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        kind (str): the kind/type to use, i.e. subcommand invoked

    Returns:
        True if successful; False otherwise
    """
    channels = await combine_channel_ids(ctx)

    vdb = vaivora.db.Database(ctx.guild.id)
    errs = []

    for _channel in channels:
        try:
            await vdb.remove_channel(kind, _channel)
        except:
            errs.append(_channel)

    await ctx.send(constants.settings.SUCCESS_CHANNELS_RM
                   .format(constants.settings.TABLE_CHANNEL,
                        kind))

    if errs:
        errs = [str(err) for err in errs]
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
    _mentions = await combine_mention_ids(ctx, mentions)

    # uid mode; parse if they're actually id's and not nonsense
    if mentions:
        _mentions.extend(await get_mention_ids(ctx, mentions))

    vdb = vaivora.db.Database(ctx.guild.id)
    users = await vdb.get_users(ctx.role_kind, _mentions)

    if users:
        if _mentions:
            users = [user for user in users if user in _mentions]
        _users = []
        to_remove = []
        for user in users:
            member = ctx.guild.get_member(user)
            # if "user" is actually a role
            if not member:
                member = ctx.guild.get_role(user)

            # if "user" is still not defined, it's most likely invalid
            if not member:
                to_remove.append(user)
                continue

            _users.append(member)

        if to_remove:
            await vdb.remove_users(ctx.role_kind, to_remove)

        _users = '\n'.join(['{:<15}\t{:>10}'.format(
                             str(user.id),
                             str(user))
                            for user in _users])
        users = '```\n{}```'.format(_users)
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
    _mentions = await combine_mention_ids(ctx, mentions)

    if not _mentions:
        await ctx.send('{} {}'
                       .format(ctx.author.mention,
                               constants.settings.FAIL_NO_MENTIONS))
        return False

    vdb = vaivora.db.Database(ctx.guild.id)
    errs = await vdb.set_users(ctx.role_kind, _mentions)

    await ctx.send('{} {}'
                   .format(ctx.author.mention,
                           constants.settings.SUCCESS_ROLES_UP.format(
                                ctx.role_kind)))

    if errs:
        errs = [str(err) for err in errs]
        await ctx.send('{} {}'
                       .format(ctx.author.mention,
                               constants.settings.PARTIAL_SUCCESS.format(
                                    constants.settings.SETTING_SET,
                                    '\n'.join(errs))))

    return True


async def role_deleter(ctx, mentions=None):
    """
    :func:`role_deleter` handles the backend for
    :func:`dr_member`, :func:`dr_auth`, and :func:`dr_boss`.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        mentions: (default: None) optional mentions that are only id's

    Returns:
        True if successful; False otherwise
    """
    _mentions = await combine_mention_ids(ctx, mentions)

    if not _mentions:
        await ctx.send('{} {}'
                       .format(ctx.author.mention,
                               constants.settings.FAIL_NO_MENTIONS))
        return False

    vdb = vaivora.db.Database(ctx.guild.id)
    errs = await vdb.remove_users(ctx.role_kind, _mentions)

    await ctx.send('{} {}'
                   .format(ctx.author.mention,
                           constants.settings.SUCCESS_ROLES_RM.format(
                                ctx.role_kind)))

    if errs:
        errs = [str(err) for err in errs]
        await ctx.send('{} {}'
                       .format(ctx.author.mention,
                               constants.settings.PARTIAL_SUCCESS.format(
                                    constants.settings.SETTING_SET,
                                    '\n'.join(errs))))

    return True


async def contribution_setter(ctx, points, member=None, append=False):
    """
    :func:`contribution_setter` handles the backend work for
    :func:`s_talt` and :func:`s_point`.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        points (int): the points to set
        member: (default: None) an optional member to modify
        append (bool): (default: False) whether to add or not

    Returns:
        True if successful; False otherwise
    """
    mention = 0

    if ctx.message.mentions:
        if len(ctx.message.mentions) > 1:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings
                                   .FAIL_TOO_MANY_MENTIONS))
            return False
        else:
            mention = ctx.message.mentions[0].id

    if member and mention:
        await ctx.send('{} {}'
                       .format(ctx.author.mention,
                               constants.settings
                               .FAIL_TOO_MANY_MENTIONS))
        return False
    elif member:
        try:
            mention = (await get_mention_ids(ctx, member))[0]
        except:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings
                                   .FAIL_INVALID_MENTION))
            return False
    else:
        member = mention

    if not member:
        member = ctx.author.id

    vdb = vaivora.db.Database(ctx.guild.id)
    if await vdb.set_contribution(member, points, append):
        row = '```\n{:<40}{:>5} points {:>10} Talt```'.format(
                    str(ctx.guild.get_member(member)),
                    points,
                    int(points/20))
        await ctx.send('{} {}'
                       .format(ctx.author.mention,
                               constants.settings
                               .SUCCESS_CONTRIBUTIONS
                               .format(row)))
        return True
    else:
        await ctx.send('{} {}'
                       .format(ctx.author.mention,
                               constants.settings
                               .FAIL_CONTRIBUTIONS))
        return False


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

    @s_role.command(name='member')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def sr_member(self, ctx, mentions: commands.Greedy[int] = None):
        """
        :func:`sr_member` sets roles of members.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions: an optional mention as a raw id

        Returns:
            True if successful; False otherwise      
        """
        return await role_setter(ctx, mentions)

    @s_role.command(name='authorized', aliases=['auth'])
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def sr_auth(self, ctx, mentions: commands.Greedy[int] = None):
        """
        :func:`sr_member` sets roles of members.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions: an optional mention as a raw id

        Returns:
            True if successful; False otherwise      
        """
        return await role_setter(ctx, mentions)

    @s_role.command(name='boss')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def sr_boss(self, ctx, mentions: commands.Greedy[int] = None):
        """
        :func:`sr_member` sets roles of members.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions: an optional mention as a raw id

        Returns:
            True if successful; False otherwise      
        """
        return await role_setter(ctx, mentions)

    @_set.group(name='talt')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def s_talt(self, ctx, points: int, member: commands.Greedy[int] = None):
        """
        :func:`s_talt` sets contribution points.
        Optionally, if a member is mentioned, then the member's record
        will be modified instead.
        If using the `member` variable, take care to fill in all arguments.
        e.g. $settings set talt 20 @someone

        Args:
            ctx (discord.ext.commands.Context): context of the message
            points (int): the points to add; i.e. 1 talt = 20 points, etc
            member: (default: None) the optional member's record to modify

        Returns:
            True if successful; False otherwise
        """
        if points < 1:
            return False
        points *= 20

        return await contribution_setter(ctx, points, member)

    @_set.group(name='point', aliases=['points', 'pt', 'pts',
                                       'contrib', 'contribs',
                                       'contribution'])
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def s_point(self, ctx, points: int, member: commands.Greedy[int] = None):
        """
        :func:`s_point` sets contribution points.
        Optionally, if a member is mentioned, then the member's record
        will be modified instead.
        If using the `member` variable, take care to fill in all arguments.
        e.g. $settings set point 20 @someone

        Args:
            ctx (discord.ext.commands.Context): context of the message
            points (int): the points to add; i.e. 1 talt = 20 points, etc
            member: (default: None) the optional member's record to modify

        Returns:
            True if successful; False otherwise
        """
        if points < 1:
            return False
        if points % 20 != 0:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings
                                   .FAIL_INVALID_POINTS))
            return False

        return await contribution_setter(ctx, points, member)

    @_set.command(name='guild')
    @checks.only_in_guild()
    @checks.check_role()
    async def s_guild(self, ctx, points: int):
        """
        :func:`s_guild` sets guild to level and points.
        Any extraneous points are allocated to a sentinel value.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            points (int): the current guild points

        Returns:
            True if successful; False otherwise
        """
        vdb = vaivora.db.Database(ctx.guild.id)
        if not await vdb.set_guild_points(points):
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings.FAIL_SET_GUILD))
            return False
        else:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings.SUCCESS_SET_GUILD))
            return True

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

    @g_role.command(name='member')
    @checks.only_in_guild()
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def gr_member(self, ctx, mentions: commands.Greedy[int] = None):
        """
        :func:`gr_member` gets members of role `member`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions: an optional mention as a raw id

        Returns:
            True if successful; False otherwise
        """
        return await role_getter(ctx, mentions)

    @g_role.command(name='authorized', aliases=['auth'])
    @checks.only_in_guild()
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def gr_auth(self, ctx, mentions: commands.Greedy[int] = None):
        """
        :func:`gr_auth` gets members of role `authorized`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions: an optional mention as a raw id

        Returns:
            True if successful; False otherwise
        """
        return await role_getter(ctx, mentions)

    @g_role.command(name='boss')
    @checks.only_in_guild()
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def gr_boss(self, ctx, mentions: commands.Greedy[int] = None):
        """
        :func:`gr_boss` gets members of role `boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions: an optional mention as a raw id

        Returns:
            True if successful; False otherwise
        """
        return await role_getter(ctx, mentions)

    @_get.command(name='talt', aliases=['points', 'pt', 'pts',
                                        'contrib', 'contribs',
                                        'contribution'])
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def g_talt(self, ctx, mentions: commands.Greedy[int] = None):
        """
        :func:`g_talt` gets contribution record.
        Ignores the 'remainder' (uncreditable) amount.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions: an optional mention as a raw id

        Returns:
            True if successful; False otherwise
        """
        _mentions = []

        if ctx.message.mentions:
            for mention in ctx.message.mentions:
                _mentions.append(mention.id)

        # uid mode; parse if they're actually id's and not nonsense
        if mentions:
            _mentions.extend(await get_mention_ids(ctx, mentions))

        vdb = vaivora.db.Database(ctx.guild.id)
        users = await vdb.get_contribution(_mentions)
        users = [user for user in users if user is not None]

        if users:
            output = []
            users = sorted(users, key=lambda usr: usr[1], reverse=True)
            for user in users:
                member = user[0]
                points = user[1]
                output.append('\n{:<40}{:>5} points {:>10} Talt'
                              .format(
                                    str(ctx.guild.get_member(member)),
                                    points,
                                    int(points/20)))
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings.SUCCESS_GET_CONTRIBS))
            while(len(output) > 15):
                await ctx.send('```\n{}```'.format('\n'.join(output[0:15])))
                output = output[15:]

            if len(output) > 0:
                await ctx.send('```\n{}```'.format('\n'.join(output)))

            return True
        else:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings.FAIL_NO_CONTRIBS))
            return False

    @_get.command(name='guild')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def g_guild(self, ctx):
        """
        :func:`g_guild` gets guild level and points.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        vdb = vaivora.db.Database(ctx.guild.id)
        try:
            level, points = await vdb.get_guild_info()
        except:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings.FAIL_NO_CONTRIBS))
            return False

        bars_level = '[{}{}]'.format('|'*level,
                                     ' '*(20-level))
        points_progress = floor(points*10/constants.settings.G_LEVEL[level+1])*4
        bars_points = '[{}{}]'.format('|'*points_progress,
                                      ' '*(40-points_progress))
        await ctx.send('{} {}'
                       .format(ctx.author.mention,
                               constants.settings.SUCCESS_GET_GUILD
                               .format(level, points,
                                       bars_level, bars_points)))
        return True

    @settings.group(name='add')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def add(self, ctx):
        """
        :func:`add` is only to be used for contributions.
        Instead of :func:`set` which directly sets the value,
        :func:`add` increments.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True always
        """
        return True

    @add.command(name='talt')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def a_talt(self, ctx, points: int, member: commands.Greedy[int] = None):
        """
        :func:`a_talt` adds contribution points,
        appending to the existing record.
        Optionally, if a member is mentioned, then the member's record
        will be modified instead.
        If using the `member` variable, take care to fill in all arguments.
        e.g. $settings add talt 20 @someone

        Args:
            ctx (discord.ext.commands.Context): context of the message
            points (int): the points to add; i.e. 1 talt = 20 points, etc
            member: (default: None) the optional member's record to modify

        Returns:
            True if successful; False otherwise
        """
        if points < 1:
            return False
        points *= 20

        return await contribution_setter(ctx, points, member, append=True)

    @add.command(name='point', aliases=['points', 'pt', 'pts',
                                       'contrib', 'contribs',
                                       'contribution'])
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role(constants.settings.ROLE_MEMBER)
    async def a_point(self, ctx, points: int, member: commands.Greedy[int] = None):
        """
        :func:`s_point` adds contribution points,
        appending to the existing record.
        Optionally, if a member is mentioned, then the member's record
        will be modified instead.
        If using the `member` variable, take care to fill in all arguments.
        e.g. $settings set point 20 @someone

        Args:
            ctx (discord.ext.commands.Context): context of the message
            points (int): the points to add; i.e. 1 talt = 20 points, etc
            member: (default: None) the optional member's record to modify

        Returns:
            True if successful; False otherwise
        """
        if points < 1:
            return False
        if points % 20 != 0:
            await ctx.send('{} {}'
                           .format(ctx.author.mention,
                                   constants.settings
                                   .FAIL_INVALID_POINTS))
            return False

        return await contribution_setter(ctx, points, member, append=True)

    @settings.group(name='delete', aliases=['rm', 'remove', 'del'])
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def delete(self, ctx):
        """
        :func:`delete` is the prototype for deletion subcommands.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True always
        """
        return True

    @delete.group(name='role')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def d_role(self, ctx):
        """
        :func:`d_role` deletes roles.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True always
        """
        ctx.role_kind = ctx.invoked_subcommand.name
        return True

    @d_role.command(name='member')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def dr_member(self, ctx, mentions: commands.Greedy[int] = None):
        """
        :func:`dr_member` deletes members from `member`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return await role_deleter(ctx, mentions)

    @d_role.command(name='authorized', aliases=['auth'])
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def dr_auth(self, ctx, mentions: commands.Greedy[int] = None):
        """
        :func:`dr_auth` deletes members from `authorized`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return await role_deleter(ctx, mentions)

    @d_role.command(name='boss')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def dr_boss(self, ctx, mentions: commands.Greedy[int] = None):
        """
        :func:`dr_boss` deletes members from `boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return await role_deleter(ctx, mentions)

    @delete.group(name='channel')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def d_channel(self, ctx):
        """
        :func:`d_channel` deletes channels.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True always
        """
        ctx.channel_kind = ctx.invoked_subcommand.name
        pass

    @d_channel.command(name='settings')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def dc_settings(self, ctx):
        """
        :func:`dc_settings` deletes channels from `settings`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return await channel_deleter(ctx, ctx.channel_kind)

    @d_channel.command(name='boss')
    @checks.only_in_guild()
    @checks.check_channel(constants.settings.MODULE_NAME)
    @checks.check_role()
    async def dc_boss(self, ctx):
        """
        :func:`dc_boss` deletes channels from `boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return await channel_deleter(ctx, ctx.channel_kind)


def setup(bot):
    bot.add_cog(SettingsCog(bot))
