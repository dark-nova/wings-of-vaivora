from typing import Callable, List

import discord
from discord.ext import commands

import vaivora.db


class Error(commands.CheckError):
    """Base exception derived from commands.CommandError
    for checks.

    """
    pass


class NoChannelMentionsError(Error):
    """No channel mentions were found."""
    pass


class NotAuthorizedError(Error):
    """User does not have the Wings of Vaivora role
    to call the command.

    """
    pass


class InvalidChannelError(Error):
    """User called the command in a channel not registered
    for that command.

    """
    pass


class InvalidBossError(Error):
    """User chose the wrong boss target for a command.
    "Status", "Query" subcommands: must only use boss
    "Type" subcommands: "all" only

    """
    pass


def check_channel(kind: str) -> Callable[..., bool]:
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
        Callable: the inner check function

    """
    @commands.check
    async def check(ctx):
        """The actual check.

        Returns:
            bool: True if successful; False otherwise
                Note that this means if no channels have registered,
                *all* channels are valid.

        """
        vdb = vaivora.db.Database(ctx.guild.id)
        chs = await vdb.get_channels(kind)

        # Silently ignore wrong channel
        if chs and ctx.channel.id not in chs:
            raise InvalidChannelError(kind)
        # In the case of `None` chs, all channels are valid
        else:
            return True
    return check


def check_role(lesser_role: str = None) -> Callable[..., bool]:
    """Checks whether the user is authorized to run a settings command.

    In the default case (`lesser_role` is None), the author must be
    authorized.

    Args:
        lesser_role (str, optional): use this role instead of
            authorized; defaults to None

    Returns:
        Callable: the inner check function

    """
    @commands.check
    async def check(ctx):
        """The actual check.

        Returns:
            bool: True if the user is authorized

        Raises:
            NotAuthorizedError: if unauthorized

        """
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
            raise NotAuthorizedError(
                f"""{ctx.author.mention}

                You are not authorized to do this!

                Minimum role: authorized
                """
                )

        if await iterate_roles(ctx.author, users):
            return True

        raise NotAuthorizedError(
            f"""{ctx.author.mention}

            You are not authorized to do this!

            Minimum role: member
            """
            )
        return False
    return check


def only_in_guild() -> Callable[..., bool]:
    """Checks whether the command was called in a Discord guild.

    If the command was not sent in a guild, e.g. DM,
    the command is not run.

    Returns:
        Callable: the inner check function

    """
    @commands.check
    async def check(ctx):
        """The actual check.

        Returns:
            bool: True if guild; False otherwise

        """
        if ctx.guild is None: # not a guild
            # await ctx.send(
            #     'This command is not available in Direct Messages.'
            #     )
            return False
        return True
    return check


def has_channel_mentions() -> Callable[..., bool]:
    """Checks whether a command has channel mentions. How creative

    Returns:
        Callable: the inner check function

    """
    @commands.check
    async def check(ctx):
        """The actual check.

        Returns:
            bool: True if message has channel mentions

        Raises:
            NoChannelMentionsError: otherwise

        """
        if not ctx.message.channel_mentions: # not a guild
            raise NoChannelMentionsError(
                f"""{ctx.author.mention}

                Too few or many arguments for `$settings`.

                Usage: """
                '`$settings set channel <type> <#channel> [<#channel> ...]`'
                )
        return True
    return check


def is_boss_valid(all_valid: bool = False) -> Callable[..., bool]:
    """Checks if the boss arg is valid.

    Args:
        all_valid (bool, optional): whether 'all' is valid; defaults to False

    Returns:
        Callable: the inner check function

    """
    @commands.check
    async def check(ctx):
        """The actual check.

        Returns:
            bool: True if valid given `all_valid`

        Raises:
            InvalidBossError: if invalid

        """
        subcommand = ctx.subcommand_passed
        if all_valid:
            if ctx.boss == 'all':
                return True
            else:
                raise InvalidBossError(
                    f"""{ctx.author.mention}

                    **{ctx.boss}** is invalid for the `{subcommand}` subcommand.

                    Only use **all**.
                    """
                    )
        else:
            if ctx.boss != 'all':
                return True
            else:
                raise InvalidBossError(
                    f"""{ctx.author.mention}

                    **{ctx.boss}** is invalid for the `{subcommand}` subcommand.

                    Do not use **all**.
                    """
                    )
    return check


def is_db_valid(guild_id: int, table: str) -> Callable[..., bool]:
    """Checks if the guild's database `table` is valid.

    Returns:
        Callable: the inner check function

    """
    @commands.check
    async def check(ctx):
        """The actual check.

        Returns:
            bool: True if valid

        Raises:
            vaivora.db.InvalidDBError: if invalid

        """
        vdb = vaivora.db.Database(guild_id)
        try:
            await vdb.check_if_valid('boss')
            return True
        except vaivora.db.InvalidDBError as e:
            await vdb.create_db('boss')
            raise e
    return check


# Non-decorator checks
# The following are not to be called as discord.py checks.

async def is_bot_owner(user: discord.User, bot) -> bool:
    """Checks whether `user` owns `bot`.

    Args:
        user (discord.User): the user to check
        bot: the bot itself

    Returns:
        bool: True if the user is the owner; False otherwise

    """
    return user == (await bot.application_info()).owner


# Helper functions

async def iterate_roles(author: discord.Member, users: List[int]) -> bool:
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
            if role.id in users:
                return True
    return False
