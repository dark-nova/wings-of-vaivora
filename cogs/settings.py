import re
import os
import os.path
import json
import asyncio
import aiosqlite
import typing
from itertools import chain

import vaivora.db
from vaivora.secrets import discord_user_id
import constants.settings
#from constants.settings import en_us as lang_settings


def help():
    """
    :func:`help` returns help for this module.

    Returns:
        a list of detailed help messages
    """
    return constants.settings.HELP


async def get_users(guild_id: int, kind: str):
    """
    :func:`get_authorized` returns a list of authorized users.

    Args:
        guild_id (int): the id of the guild to check
        kind (str): the kind of user to get

    Returns:
        list: all users that are of `kind`
        None: if no users were found
    """
    vdb = vaivora.db.Database(guild_id)
    return await vdb.get_users(kind)


async def purge(guild_id: int):
    """
    :func:`purge` is a last-resort subcommand that
    resets the channels table.

    Args:
        guild_id (int): the id of the guild to purge tables

    Returns:
        True if successful; False otherwise
    """
    vdb = vaivora.db.Database(guild_id)
    return await vdb.purge()


async def get_channel(guild_id: int, kind):
    """
    :func:`get_channel` gets a list of channels
    of an associated `kind`.

    Args:
        guild_id (int): the id of the guild to check
        kind (str): the kind of channel to get

    Returns:
        list: all channel id's of `kind`
        None: if no channels were found
    """
    vdb = vaivora.db.Database(guild_id)
    return await vdb.get_channel(kind)


class SettingsCog:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def _help(ctx):
        """
        :func:`_help` retrieves help pages for `$settings`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True
        """
        _help = vaivora.settings.help()
        for _h in _help:
            await ctx.author.send(_h)
        return True


    @commands.command()
    @only_in_guild()
    @check_role()
    async def purge(ctx):
        """
        :func:`purge` is a last-resort subcommand that
        resets the channels table.

        Returns:
            True if successful; False otherwise
        """
        if await vaivora.settings.purge(ctx.guild.id):
            await ctx.send('{} {}'.format(ctx.author.mention,
                                          constants.settings.SUCCESS_PURGED))
            return True
        else:
            await ctx.send('{} {}'.format(ctx.author.mention,
                                          constants.settings.FAIL_PURGED))
            return False


    # $settings set <target> <kind> <discord object>
    @commands.group(name='set')
    @only_in_guild()
    @check_channel(constants.main.ROLE_SETTINGS)
    @check_role()
    async def _set(ctx):
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
    @only_in_guild()
    @check_channel(constants.main.ROLE_SETTINGS)
    @check_role()
    async def __channel(ctx):
        """
        :func:`__channel` sets channels to `kind`s.
        e.g. sets a channel (target) to boss (kind)

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        ctx.channel_kind = ctx.invoked_subcommand.name
        return True


    @__channel.command(name='settings')
    @only_in_guild()
    @check_channel(constants.main.ROLE_SETTINGS)
    @check_role()
    @has_channel_mentions()
    async def ___settings(ctx):
        """
        :func:`___settings` sets channels to `settings`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return await channel_setter(ctx, ctx.channel_kind)


    @__channel.command(name='boss')
    @only_in_guild()
    @check_channel(constants.main.ROLE_SETTINGS)
    @check_role()
    @has_channel_mentions()
    async def ___boss(ctx):
        """
        :func:`___boss` sets channels to `boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return await channel_setter(ctx, ctx.channel_kind)


    @_set.group(name='role')
    @only_in_guild()
    @check_channel(constants.main.ROLE_SETTINGS)
    @check_role()
    async def __role(ctx, kind: str, mentions: commands.Greedy[int]):
        """
        :func:`__role` sets `role`s to `kind`s.
        e.g. sets a channel (target) to boss (kind)

        Args:
            ctx (discord.ext.commands.Context): context of the message
            target (str): the object to set
            kind (str): the kind/type to use

        Returns:
            True if successful; False otherwise
        """
        if (kind != constants.settings.ROLE_BOSS
                and kind != constants.settings.ROLE_MEMBER
                and kind != constants.settings.ROLE_AUTH):
            await ctx.send(constants.errors.IS_INVALID_3
                           .format(ctx.author.mention, kind,
                                   constants.settings.MODULE_NAME,
                                   constants.settings.TARGET_ROLE))
            return False

        _mentions = []

        if ctx.message.mentions:
            for mention in ctx.message.mentions:
                _mentions.append(mention)

        if mentions:
            gids = [member.id for member in (ctx.guild.members
                                             + ctx.guild.roles)]
            rids = [member.id for member in ctx.guild.role]
            if kind == constants.settings.ROLE_BOSS:
                for mention in mentions:
                    if mention in rids: # do not allow regular users for $boss
                        _mention.append(mention)
            else:
                for mention in mentions:
                    if mention in gids:
                        _mentions.append(mention)

        pass

    async def channel_setter(ctx, kind):
        """
        :func:`channel_setter` does the work
        for :func:`___boss` and :func:`___settings`.

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


def setup(bot):
    bot.add_cog(SettingsCog(bot))