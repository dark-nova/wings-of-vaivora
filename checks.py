import discord
from discord.ext import commands

import vaivora.db
import constants.boss
import constants.settings


def check_channel(kind):
    """
    :func:`check_channel` checks whether a channel is allowed
    to interact with Wings of Vaivora.

    Args:
        kind (str): the type (name) of the channel

    Returns:
        True if successful; False otherwise
            Note that this means if no channels have registered,
            *all* channels are valid.
    """
    @commands.check
    async def check(ctx):
        vdb = vaivora.db.Database(str(ctx.guild.id))
        chs = await vdb.get_channel(kind)

        if chs and ctx.channel.id not in chs:
            return False # silently ignore wrong channel
        else: # in the case of `None` chs, all channels are valid
            return True
    return check


def check_role(lesser_role=None):
    """
    :func:`check_role` sees whether the user is authorized
    to run a settings command.

    Args:
        lesser_role: (default: None) an optional role to check

    Returns:
        True if the user is authorized; False otherwise
    """
    @commands.check
    async def check(ctx):
        vdb = vaivora.db.Database(str(ctx.guild.id))
        users = await vdb.get_users(
                    constants.settings.ROLE_SUPER_AUTH)

        if await iterate_roles(ctx.author, users):
            return True

        users = await vdb.get_users(
                    constants.settings.ROLE_AUTH)

        if await iterate_roles(ctx.author, users):
            return True

        # for now, just use the default member role
        if lesser_role:
            users = await vdb.get_users(
                        constants.settings.ROLE_MEMBER)
        else:
            await ctx.send('{} {}'
                        .format(ctx.author.mention,
                                constants.settings.FAIL_NOT_AUTH))
            return False

        if await iterate_roles(ctx.author, users):
            return True

        await ctx.send('{} {}'
                        .format(ctx.author.mention,
                                constants.settings.FAIL_NOT_AUTH))
        return False
    return check


async def iterate_roles(author, users):
    """
    :func:`iterate_roles` is a helper function for :func:`check_roles`.

    Args:
        author (discord.Member): the command user
        users (list): users to iterate through

    Returns:
        True if author is authorized; False otherwise
    """
    if users and author.id in users:
        return True
    elif author.roles:
        for role in author.roles:
            try:
                if role.id in users:
                    return True
            except:
                pass
    return False


def only_in_guild():
    """
    :func:`only_in_guild` checks whether a command can run.

    Returns:
        True if guild; False otherwise
    """
    @commands.check
    async def check(ctx):
        if ctx.guild == None: # not a guild
            await ctx.send(constants.main.FAIL_CANT_DM.format(constants.boss.COMMAND))
            return False
        return True
    return check


def has_channel_mentions():
    """
    :func:`has_channel_mentions` checks whether
    a command has channel mentions. How creative

    Returns:
        True if message has channel mentions; False otherwise
    """
    @commands.check
    async def check(ctx):
        if not ctx.message.channel_mentions: # not a guild
            await ctx.send(constants.main.FAIL_TOO_FEW_ARGS.format(
                ctx.author.mention, constants.settings.MODULE_NAME,
                constants.settings.USAGE_SET_CHANNELS))
            return False
        return True
    return check
