import discord
from discord.ext import commands

import vaivora.db


def check_channel(kind: str):
    """Checks whether a channel is allowed to
    interact with Wings of Vaivora.

    Once a channel type has even one channel set,
    commands will fail if run outside those channels.

    If the guild is in a state where no channel can be used,
    whether because the old channel was deleted, etc.,
    the guild's `authorized` can run `$settings purge` to
    reset the channel table anew.

    Args:
        kind (str): the type (name) of the channel

    Returns:
        bool: True if successful; False otherwise
        Note that this means if no channels have registered,
        *all* channels are valid.

    """
    @commands.check
    async def check(ctx):
        vdb = vaivora.db.Database(ctx.guild.id)
        chs = await vdb.get_channels(kind)

        if chs and ctx.channel.id not in chs:
            return False # silently ignore wrong channel
        else: # in the case of `None` chs, all channels are valid
            return True
    return check


def check_role(lesser_role = None):
    """Checks whether the user is authorized to run a settings command.

    In the default case (`lesser_role` is None), the author must be
    authorized.

    Args:
        lesser_role (str, optional): use this role instead of authorized;
            defaults to None

    Returns:
        bool: True if the user is authorized; False otherwise

    """
    @commands.check
    async def check(ctx):
        vdb = vaivora.db.Database(ctx.guild.id)
        users = await vdb.get_users('s-authorized')

        if await iterate_roles(ctx.author, users):
            return True

        users = await vdb.get_users('authorized')

        if await iterate_roles(ctx.author, users):
            return True

        # for now, just use the default member role
        if lesser_role:
            users = await vdb.get_users('member')
        else:
            # await ctx.send(
            #     f"""{ctx.author.mention}

            #     You are not authorized to do this!
            #     """
            #     )
            return False

        if await iterate_roles(ctx.author, users):
            return True

        # await ctx.send(
        #     f"""{ctx.author.mention}

        #     You are not authorized to do this!
        #     """
        #     )
        return False
    return check


async def iterate_roles(author, users: list):
    """Iterates through the author's Discord roles.

    Checks whether any of the author's Discord roles or
    the author's id itself are in a list of
    authorized `users`.

    Called by `check_roles`.

    Args:
        author (discord.Member): the command user
        users (list): users to iterate through

    Returns:
        bool: True if author is authorized; False otherwise

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
    """Checks whether the command was called in a Discord guild.

    If the command was not sent in a guild, e.g. DM,
    the command is not run.

    Returns:
        bool: True if guild; False otherwise

    """
    @commands.check
    async def check(ctx):
        if ctx.guild is None: # not a guild
            # await ctx.send(
            #     'This command is not available in Direct Messages.'
            #     )
            return False
        return True
    return check


def has_channel_mentions():
    """Checks whether a command has channel mentions. How creative

    Returns:
        bool: True if message has channel mentions; False otherwise

    """
    @commands.check
    async def check(ctx):
        if not ctx.message.channel_mentions: # not a guild
            # await ctx.send(
            #     f"""{ctx.author.mention}

            #     Too few or many arguments for `$settings`.

            #     Usage: """
            #     '`$settings set channel <type> <#channel> [<#channel> ...]`'
            #     )
            return False
        return True
    return check


async def is_bot_owner(user: discord.User, bot):
    """NOT A DECORATOR CHECK! Checks whether `user` owns `bot`.

    Args:
        user (discord.User): the user to check
        bot: the bot itself

    Returns:
        bool: True if the user is the owner; False otherwise

    """
    return user == (await bot.application_info()).owner
