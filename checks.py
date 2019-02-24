import discord
from discord.ext import commands

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
        chs = await vdbs[ctx.guild.id].get_channel(kind)

        if chs and ctx.channel.id not in chs:
            return False # silently ignore wrong channel
        else: # in the case of `None` chs, all channels are valid
            return True
    return check


def check_role():
    """
    :func:`check_role` sees whether the user is authorized
    to run a settings command.

    Returns:
        True if the user is authorized; False otherwise
    """
    @commands.check
    async def check(ctx):
        users = await vdbs[ctx.guild.id].get_users(
                    constants.settings.ROLE_SUPER_AUTH)

        if users and str(ctx.author.id) in users:
            return True
        else:
            users = await vdbs[ctx.guild.id].get_users(
                        constants.settings.ROLE_AUTH)

        if users and str(ctx.author.id) in users:
            return True
        else:
            await ctx.send('{} {}'
                            .format(ctx.author.mention,
                                    constants.settings.FAIL_NOT_AUTH))
            return False
    return check


def only_in_guild():
    """
    :func:`only_in_guild` checks whether a command can run.

    Returns:
        True if guild; False otherwise
    """
    @commands.check
    async def check(ctx):
        if ctx.guild == None: # not a guild
            await ctx.send(constants.errors.CANT_DM.format(constants.boss.COMMAND))
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
            await ctx.send(constants.errors.TOO_FEW_ARGS.format(
                ctx.author.mention, constants.main.ROLE_SETTINGS,
                constants.settings.USAGE_SET_CHANNELS))
            return False
        return True
    return check