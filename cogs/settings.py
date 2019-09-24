import asyncio
import logging
import re
from inspect import cleandoc
from math import floor

import discord
import yaml
from discord.ext import commands

import checks
import vaivora.db


HELP = []
HELP.append(
    cleandoc(
        """
        ```
        Usage:
            $settings <setting> talt <talt-value> [<talt-unit>] ([<@mention>] | guild)
            $settings <setting> <obj> (<role> [<@mention>] | <channel> [<#channel>])
            $settings help

        Examples:
            $settings add talt 12
                Means: Add 12 Talt to your guild record.

            $settings set talt 12
                Means: Sets your guild record of Talt to 12. Not the same as adding.

            $settings add talt 240 points
                Means: The same as `$settings add talt 12`, with optional unit.

            $settings add talt 12 @person
                Means: Add 12 Talt to @person's guild record.
                You must be "Authorized" to do this.

            $settings set channel settings #settings
                Means: Sets this channel to "Settings".
                Note: this disables Settings in all channels not marked as "Settings".

            $settings set role authorized @person
                Means: Sets @person to be "Authorized".
                You must be "Authorized" to do this.
                Note: guild owners are considered "Super-Authorized" and must set this up first.

        ```
        """
        )
    )
HELP.append(
    cleandoc(
        """
        ```
        Options:
            <setting>
                This can be "add", "set", "remove", or "get". Manipulates records.
                Options:
                    "add" can only be used for Talt-related subcommands. Increments relative to user's base.
                    "set" can be used for all associated subcommands. Sets Talt, Role, and Channel.
                    "remove" can be used for all associated subcommands. Removes Talt contribution, Roles from users mentioned, etc.
                    "get" can be used for all associated subcommands. Retrieves Talt contribution, highest Role from users mentioned, etc.
                Note: "Super-Authorized" will only be shown as "Authorized".

            <obj>
                This is the object to modify. For users, "roles". For channels, "channels".

            <channel>
                This can be "settings" or "boss". Sets channels (and restricts others).
                Options:
                    "settings": Adds a channel to allow all settings commands. 'get'ters will still be unrestricted.
                    "boss": Adds a channel to accept boss record manipulation.
                Once a channel is set (and none were, before), many commands are no longer read outside the allowed channels.
        ```
        """
        )
    )
HELP.append(
    cleandoc(
        """
        ```
        Options (continued):
            <contribution>
                This can be "points", "talt", or "contributions".
                Options:
                    "points": shown in the guild UI in-game
                    "talt": defined to be the item; 1 talt = 20 points
                    "contributions": the same as "points"
                Allows manipulation of Talt guild records.

            <contribution-value>
                A number. The amount to use for `talt`. 20 points = 1 talt

            guild
                A special subcommand target for <setting> `talt`. Cannot use "add" or "remove".
                <setting> "get" prints how many points (and Talt) the guild has.
                <setting> "set" allows you to set the current points.
                Missing points (unlisted contributions) will be stored in a hidden variable, for consistency.

            <@mention>
                (optional) A Discord member or role.
                Preferably, you should use the mention format for this. You may use ID's if necessary.
                If omitted in the <setting> command, the command user will be assumed.

            [<#channel>]
                (optional) A Discord channel.
                You must use the channel link format for this.
                Both you and Wings of Vaivora must be able to see the channel.
                If omitted in the <setting> command, the current channel will be assumed.

            help
                Prints this page.


        * Discord roles are different from Wings of Vaivora's Roles.
        ```
        """
        )
    )

newline = '\n'
bullet_point = '\n- '

aliases_delete = [
    'del',
    'remove',
    'rm',
    ]
aliases_channel = [
    'ch',
    'chs',
    'chan',
    'chans',
    'channels',
    ]
aliases_role = [
    'roles',
    'user',
    'users',
    ]
aliases_authorized = [
    'auth',
    ]
aliases_points = [
    'points',
    'pt',
    'pts',
    'contrib',
    'contribs',
    'contribution',
    ]

logger = logging.getLogger('vaivora.cogs.settings')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('vaivora.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


with open('guild.yaml', 'r') as f:
    guild_conf = yaml.safe_load(f, Loader = yaml.Loader)


async def get_mention_ids(ctx, mentions):
    """Converts meaningful int input/arguments to mentions.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        mentions: mentions to test for IDs

    Returns:
        list: of valid Discord IDs

    """
    if type(mentions) is int:
        mentions = [mentions]

    valid_mentions = []
    gids = [
        member.id for member in (ctx.guild.members + ctx.guild.roles)
        ]
    rids = [member.id for member in ctx.guild.roles]
    try:
        if ctx.role_type == 'boss' or ctx.role_type == 'events':
            for mention in mentions:
                # Do not allow regular users for `$boss`
                if mention in rids:
                    valid_mentions.append(mention)
    except Exception as e:
        logger.error(
            f'Caught {e} in cogs.settings: get_mention_ids; '
            f'guild: {ctx.guild.id}; '
            f'user: {ctx.author.id}; '
            f'command: {ctx.command}'
            )

    for mention in mentions:
        if mention in gids:
            valid_mentions.append(mention)

    return valid_mentions


async def combine_mention_ids(ctx, mentions = None):
    """Combines all mentions and valid IDs.

    Called by `role_setter`, `role_getter`, and `role_deleter`.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        mentions (optional): optional mentions that are only IDs;
            defaults to None

    Returns:
        list of str: of mention IDs

    """
    valid_mentions = []

    if ctx.message.role_mentions:
        for mention in ctx.message.role_mentions:
            valid_mentions.append(mention.id)

    # do not allow regular users for $boss
    if (ctx.role_type == 'boss'
        or ctx.role_type == 'events'):
        if ctx.message.mentions:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Members can't be set as the {ctx.role_type} role!"""
                    )
                )
    else:
        if ctx.message.mentions:
            for mention in ctx.message.mentions:
                valid_mentions.append(mention.id)

    # uid mode; parse if they're actually IDs and not nonsense
    if mentions:
        valid_mentions.extend(await get_mention_ids(ctx, mentions))

    return valid_mentions


async def combine_channel_ids(ctx):
    """Combines all channel IDs.

    Called by `channel_setter` and `channel_deleter`.

    Args:
        ctx (discord.ext.commands.Context): context of the message

    Returns:
        list of int: of Discord channel IDs

    """
    channels = []
    if not ctx.message.channel_mentions:
        channels.append(ctx.channel.id)
    else:
        for channel_mention in ctx.message.channel_mentions:
            channels.append(str(channel_mention.id))
    return channels


async def channel_getter(ctx, kind):
    """Gets channels of a given `kind`.

    Called by `gc_settings`, `gc_boss`, and `gc_events`.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        kind (str): the kind/type to use, i.e. subcommand invoked

    Returns:
        bool: True always

    """
    vdb = vaivora.db.Database(ctx.guild.id)
    all_channels = await vdb.get_channels(kind)

    if not channels:
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                No channels were found associated with the {kind} type.
                """
                )
            )
    else:
        channels = []
        for channel in all_channels:
            if not ctx.guild.get_channel(channel):
                await vdb.remove_channel(kind, channel)
            else:
                channels.append(
                    str(ctx.guild.get_channel(channel).mention)
                    )

        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                Here are channels of {kind} type:

                - {bullet_point.join(channels)}
                """
                )
            )
    return True


async def channel_setter(ctx, kind):
    """Sets a channel to a given `kind`.

    Called by `sc_settings`, `sc_boss`, and `sc_events`.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        kind (str): the kind/type to use, i.e. subcommand invoked

    Returns:
        bool: True if successful; False otherwise

    """
    channels = await combine_channel_ids(ctx)

    vdb = vaivora.db.Database(ctx.guild.id)
    errs = []

    for channel in channels:
        try:
            await vdb.set_channel(kind, channel)
        except:
            errs.append(channel)

    if not errs:
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                Your channels have been registered as `{kind}` channels.
                """
                )
            )
    else:
        errs = [str(err) for err in errs]
        await ctx.send(
            f"""{ctx.author.mention}

            All or some of your channels could not be registered. Errors:

            - {bullet_point.join(errs)}
            """
            )
    return True


async def channel_deleter(ctx, kind):
    """Deletes a channel from `kind`.

    Called by `dc_settings`, `dc_boss`, and `dc_events`.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        kind (str): the kind/type to use, i.e. subcommand invoked

    Returns:
        bool: True if successful; False otherwise

    """
    channels = await combinechannel_ids(ctx)

    vdb = vaivora.db.Database(ctx.guild.id)
    errs = []

    for channel in channels:
        try:
            await vdb.removechannel(kind, channel)
        except:
            errs.append(channel)

    if not errs:
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                You have successfully unregistered channels as {kind} channels.
                """
                )
            )
    else:
        errs = [str(err) for err in errs]
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                All or some of your channels could not be unregistered. Errors:

                - {bullet_point.join(errs)}
                """
                )
            )
    return True


async def role_getter(ctx, mentions = None):
    """Gets Discord members/roles of a given Vaivora role.

    Called by `gr_member`, `gr_auth`, `gr_boss`, and `gr_events`.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        mentions (optional): optional mentions that are only IDs;
            defaults to None

    Returns:
        bool: True if successful; False otherwise

    """
    all_mentions = await combine_mention_ids(ctx, mentions)

    # UID mode; parse if they're actually IDs and not nonsense
    if mentions:
        all_mentions.extend(await get_mention_ids(ctx, mentions))

    vdb = vaivora.db.Database(ctx.guild.id)
    users = await vdb.get_users(ctx.role_type, all_mentions)

    if users:
        if all_mentions:
            users = [user for user in users if user in all_mentions]
        valid_users = []
        to_remove = []
        for user in users:
            member = ctx.guild.get_member(user)
            # `user` is actually a role; replace with role.
            if not member:
                member = ctx.guild.get_role(user)

            # If `user` is still not defined, it's most likely invalid.
            if not member:
                to_remove.append(user)
                continue

            valid_users.append(member)

        if to_remove:
            await vdb.remove_users(ctx.role_type, to_remove)

        valid_users = [
            f'{user.id:<15}\t{user:>10}'
            for user
            in valid_users
            ]
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                Here are users of the `{ctx.role_type}` role:

                ```
                {newline.join(valid_users)}
                ```
                """
                )
            )
        return True
    else:
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                No users were found associated with the `{ctx.role_type}` role.
                """
                )
            )
        return False


async def role_setter(ctx, mentions = None):
    """Sets Discord members/roles with a given Vaivora role.

    Called by `sr_member`, `sr_auth`, `sr_boss`, and `sr_events`.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        mentions (optional): optional mentions that are only IDs;
            defaults to None

    Returns:
        bool: True if successful; False otherwise

    """
    all_mentions = await combine_mention_ids(ctx, mentions)

    if not all_mentions:
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                No mentions were added.
                """
                )
            )
        return False

    vdb = vaivora.db.Database(ctx.guild.id)
    errs = await vdb.set_users(ctx.role_type, all_mentions)

    if not errs:
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                You have successfully registered users """
                f"""as the `{ctx.role_type}` role.
                """
                )
            )
        return True
    else:
        errs = [str(err) for err in errs]
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                All or some of your users could not be registered. Errors:

                - {bullet_point.join(errs)}
                """
                )
            )
        return False


async def role_deleter(ctx, mentions = None):
    """Deletes Discord members/roles from a given Vaivora role.

    Called by `dr_member`, `dr_auth`, `dr_boss`, and `dr_events`.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        mentions: optional mentions that are only IDs;
            defaults to None

    Returns:
        bool: True if successful; False otherwise

    """
    all_mentions = await combine_mention_ids(ctx, mentions)

    if not all_mentions:
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                No mentions were added.
                """
                )
            )
        return False

    vdb = vaivora.db.Database(ctx.guild.id)
    errs = await vdb.remove_users(ctx.role_type, all_mentions)

    if not errs:
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                You have successfully unregistered users """
                f"""from the `{ctx.role_type}` role.
                """
                )
            )
        return True
    else:
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                All or some of your users could not be unregistered. Errors:

                - {bullet_point.join(errs)}
                """
                )
            )
        return False


async def contribution_setter(ctx, points: int, member = None, append = False):
    """Sets contribution for a Discord member.

    Cannot be used on Discord roles.

    Called by `s_talt` and `s_point`.

    Args:
        ctx (discord.ext.commands.Context): context of the message
        points (int): the points to set
        member (optional): an optional member to modify;
            defaults to None
        append (bool, optional): whether to add instead of set;
            defaults to False

    Returns:
        bool: True if successful; False otherwise

    """
    mention = 0

    if ctx.message.mentions:
        if len(ctx.message.mentions) > 1:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You mentioned too many users!
                    (Maximum: 1; you entered {len(ctx.message.mentions)})
                    """
                    )
                )
            return False
        else:
            mention = ctx.message.mentions[0].id

    if (member and mention) or (member and len(member) > 1):
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                You mentioned too many users!
                (Maximum: 1; you entered {len(member)})
                """
                )
            )
        return False
    elif member:
        try:
            mention = (await get_mention_ids(ctx, member))[0]
        except:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You typed an invalid mention!
                    """
                    )
                )
            return False

    if not mention:
        mention = ctx.author.id

    vdb = vaivora.db.Database(ctx.guild.id)
    if await vdb.set_contribution(mention, points, append):
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                Guild contribution records have been successfully updated.

                ```
                {ctx.guild.get_member(mention):<40}{points:>5} points """
                f"""{points/20:>10} Talt
                ```
                """
                )
            )
        return True
    else:
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                Guild contribution records could not be updated.
                """
                )
            )
        return False


class SettingsCog(commands.Cog):
    """Interface for the `$settings` commands.

    This cog interacts with the `vaivora.db` backend.

    """

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.group()
    async def settings(self, ctx):
        pass

    @settings.command(
        name = 'help'
        )
    async def _help(self, ctx):
        """Retrieves help pages for `$settings`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True

        """
        for _h in HELP:
            await ctx.author.send(_h)
        return True

    @settings.command()
    @checks.only_in_guild()
    @checks.check_role()
    async def purge(self, ctx):
        """Resets the channels table as a last resort.

        Returns:
            bool: True if successful; False otherwise

        """
        vdb = vaivora.db.Database(ctx.guild.id)
        success = await vdb.purge()
        if success:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Your channel records were purged successfully.
                    """
                    )
                )
            return True
        else:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Your channel records could not be purged.
                    """
                    )
                )
            return False

    # $settings set <target> <kind> <discord object>
    @settings.group(
        name = 'set'
        )
    @checks.only_in_guild()
    @checks.check_channel('settings')
    async def _set(self, ctx):
        """Sets configuration, for  `set` subcommands.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if successful; False otherwise

        """
        return True

    @_set.group(
        name = 'channel',
        aliases = aliases_channel
        )
    @checks.check_role()
    @checks.has_channel_mentions()
    async def s_channel(self, ctx):
        """Sets Discord channels to a given kind/type.

        e.g. sets a channel (target) to boss (kind)

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True always

        """
        try:
            ctx.channel_kind = ctx.invoked_subcommand.name
        except AttributeError:
            return False
        return True

    @s_channel.command(
        name = 'settings'
        )
    async def sc_settings(self, ctx):
        """Sets Discord channels to `settings`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True if successful; False otherwise
        """
        return await channel_setter(ctx, ctx.channel_kind)

    @s_channel.command(
        name = 'boss'
        )
    async def sc_boss(self, ctx):
        """Sets Discord channels to `boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if successful; False otherwise

        """
        return await channel_setter(ctx, ctx.channel_kind)

    @s_channel.command(
        name = 'events'
        )
    async def sc_events(self, ctx):
        """Sets Discord channels to `events`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if successful; False otherwise

        """
        return await channel_setter(ctx, ctx.channel_kind)

    @_set.group(
        name = 'role',
        aliases = aliases_role
        )
    @checks.check_role()
    async def s_role(self, ctx):
        """Sets Discord members/roles to a given Vaivora role.

        e.g. sets a member (target) to role boss (Vaivora role)

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True always
        """
        try:
            ctx.role_type = ctx.invoked_subcommand.name
        except AttributeError:
            return False
        return True

    @s_role.command(
        name = 'member'
        )
    async def sr_member(self, ctx, mentions: commands.Greedy[int] = None):
        """Sets Discord members/roles to `member`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        return await role_setter(ctx, mentions)

    @s_role.command(
        name = 'authorized',
        aliases = aliases_authorized
        )
    async def sr_auth(self, ctx, mentions: commands.Greedy[int] = None):
        """Sets Discord members/roles to `authorized`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise
        """
        return await role_setter(ctx, mentions)

    @s_role.command(
        name = 'boss'
        )
    async def sr_boss(self, ctx, mentions: commands.Greedy[int] = None):
        """Sets Discord members/roles to `boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            True if successful; False otherwise
        """
        return await role_setter(ctx, mentions)

    @s_role.command(
        name = 'events'
        )
    async def sr_events(self, ctx, mentions: commands.Greedy[int] = None):
        """Sets Discord members/roles to `events`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        return await role_setter(ctx, mentions)

    @_set.group(
        name = 'talt'
        )
    @checks.check_role('member')
    async def s_talt(self, ctx, points: int,
        member: commands.Greedy[int] = None):
        """Sets contribution points, using Talt as the unit.

        Optionally, if a member is mentioned, then the member's record
        will be modified instead.

        e.g. $settings set talt 20 @someone

        Args:
            ctx (discord.ext.commands.Context): context of the message
            points (int): the points to add; i.e. 1 talt = 20 points, etc
            member (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        if points < 1:
            return False
        points *= 20

        return await contribution_setter(ctx, points, member)

    @_set.group(
        name = 'point',
        aliases = aliases_points
        )
    @checks.check_role('member')
    async def s_point(self, ctx, points: int,
        member: commands.Greedy[int] = None):
        """Sets contribution points.

        Optionally, if a member is mentioned, then the member's record
        will be modified instead.

        e.g. $settings set point 20 @someone

        Args:
            ctx (discord.ext.commands.Context): context of the message
            points (int): the points to add; i.e. 1 talt = 20 points, etc
            member (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        if points < 1:
            return False
        if points % 20 != 0:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You entered an invalid amount of points!
                    Check unit or value (divisible by 20).
                    """
                    )
                )
            return False

        return await contribution_setter(ctx, points, member)

    @_set.command(
        name = 'guild'
        )
    async def s_guild(self, ctx, points: int):
        """Sets guild points.

        Also increments guild level to correct amount based on `points`.

        Used only after setting all users first.

        Any extraneous points are allocated to a sentinel value.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            points (int): the current guild points

        Returns:
            bool: True if successful; False otherwise

        """
        vdb = vaivora.db.Database(ctx.guild.id)
        if not await vdb.set_guild_points(points):
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Something went wrong. Your guild points were not updated.
                    """
                    )
                )
            return False
        else:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Guild records have been successfully updated.
                    """
                    )
                )
            return True

    # $settings get <target> <kind> <discord object>
    @settings.group(
        name = 'get'
        )
    @checks.only_in_guild()
    @checks.check_channel('settings')
    @checks.check_role('member')
    async def _get(self, ctx):
        """Gets configurations, for `get` subcommands.

        e.g. gets channels (target) listed as boss channels (kind)

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if successful; False otherwise

        """
        return True

    @_get.group(
        name = 'channel',
        aliases = aliases_channel
        )
    async def g_channel(self, ctx):
        """Gets Discord channels of a kind/type.

        e.g. gets a channel (target) of boss (kind)

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True always

        """
        try:
            ctx.channel_kind = ctx.invoked_subcommand.name
        except AttributeError:
            return False
        return True

    @g_channel.command(
        name = 'settings'
        )
    async def gc_settings(self, ctx):
        """Gets Discord channels that are `settings` channels.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True always

        """
        return await channel_getter(ctx, ctx.channel_kind)

    @g_channel.command(
        name = 'boss'
        )
    async def gc_boss(self, ctx):
        """Gets Discord channels that are `boss` channels.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True always

        """
        return await channel_getter(ctx, ctx.channel_kind)

    @g_channel.command(
        name = 'events'
        )
    async def gc_events(self, ctx):
        """Gets Discord channels that are `events` channels.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True always

        """
        return await channel_getter(ctx, ctx.channel_kind)

    @_get.group(
        name = 'role',
        aliases = aliases_role
        )
    async def g_role(self, ctx):
        """Gets Discord members/roles of a given Vaivora role.

        e.g. gets a member (target) of role boss (kind)

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True always

        """
        try:
            ctx.role_type = ctx.invoked_subcommand.name
        except AttributeError:
            return False
        return True

    @g_role.command(
        name = 'member'
        )
    async def gr_member(self, ctx, mentions: commands.Greedy[int] = None):
        """Gets Discord members/roles marked `member`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        return await role_getter(ctx, mentions)

    @g_role.command(
        name = 'authorized',
        aliases = aliases_authorized
        )
    async def gr_auth(self, ctx, mentions: commands.Greedy[int] = None):
        """Gets Discord members/roles marked `authorized`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        return await role_getter(ctx, mentions)

    @g_role.command(
        name = 'boss'
        )
    async def gr_boss(self, ctx, mentions: commands.Greedy[int] = None):
        """Gets Discord members/roles marked `boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        return await role_getter(ctx, mentions)

    @g_role.command(
        name = 'events'
        )
    async def gr_events(self, ctx, mentions: commands.Greedy[int] = None):
        """Gets Discord members/roles marked `events`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        return await role_getter(ctx, mentions)

    @_get.command(
        name = 'talt',
        aliases = aliases_points
        )
    async def g_talt(self, ctx, mentions: commands.Greedy[int] = None,
                     record_range = None):
        """Gets contribution record.

        Ignores the 'remainder' (unattributable) amount.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None
            record_range: a range to slice the results;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        first = 0
        last = 0
        if record_range:
            try:
                first, last = record_range.split('-')
                if not (first or last):
                    raise Exception

                if first:
                    first = int(first)
                else:
                    first = 1

                if last:
                    last = int(last)
                else:
                    last = None

                if (first and last) and first >= last:
                    raise Exception
            except Exception:
                # Discard invalid ranges silently
                pass

        all_mentions = []

        if ctx.message.mentions:
            for mention in ctx.message.mentions:
                all_mentions.append(mention.id)

        # UID mode; parse if they're actually IDs and not nonsense
        if mentions:
            all_mentions.extend(await get_mention_ids(ctx, mentions))

        vdb = vaivora.db.Database(ctx.guild.id)
        records = await vdb.get_contribution(all_mentions)
        records = [record for record in records if record is not None]

        if records:
            output = []
            records = sorted(
                records, key = lambda record: record[1], reverse = True
                )
            if first and last:
                records = records[first-1:last]
            for record in records:
                member = ctx.guild.get_member(record[0])
                points = record[1]
                output.append(
                    f"""{str(member): <40}"""
                    f"""{points: >5} points """
                    f"""{points//20:>10} Talt"""
                    )

            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Here are the guild\'s contribution records:
                    """
                    )
                )

            for message in await vaivora.common.chunk_messages(
                output, 15, newlines = 1
                ):
                async with ctx.typing():
                    await asyncio.sleep(1)
                    await ctx.send(
                        cleandoc(
                            f"""```{message}```"""
                            )
                        )
            return True
        else:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    No contributions were found.
                    """
                    )
                )
            return False

    @_get.command(
        name = 'guild'
        )
    async def g_guild(self, ctx):
        """Gets guild level and points.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if successful; False otherwise

        """
        vdb = vaivora.db.Database(ctx.guild.id)
        try:
            level, points = await vdb.get_guild_info()
        except ValueError:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    No contributions were found.
                    """
                    )
                )
            return False

        bars_level = f"""[{'|' * level}{' ' * (20 - level)}]"""
        percent = floor(points*100/guild_conf['exp_per_level'][level+1])
        points_progress = floor(percent*0.4)
        bars_points = (
            f"""[ {percent:02}%"""
            f"""{'|' * (points_progress - 5)}"""
            f"""{' '*(40 - points_progress)}]"""
            )
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                This guild is currently level {level} with {points} points.
                ```
                {bars_level} {bars_points}
                ```
                """
                )
            )
        return True

    @settings.group(
        name = 'add'
        )
    async def add(self, ctx):
        """Adds to contributions.

        Instead of `set` which directly sets the value,
        `add` increments.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True always

        """
        return True

    @add.command(
        name = 'talt'
        )
    async def a_talt(self, ctx, points: int,
        member: commands.Greedy[int] = None):
        """Adds contribution points, using Talt as the unit.

        Optionally, if a member is mentioned, then that member's record
        will be modified instead.

        e.g. $settings add talt 20 @someone

        Args:
            ctx (discord.ext.commands.Context): context of the message
            points (int): the points to add; i.e. 1 talt = 20 points, etc
            member (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        if points < 1:
            return False
        points *= 20

        return await contribution_setter(ctx, points, member, append = True)

    @add.command(
        name = 'point',
        aliases = aliases_points
        )
    async def a_point(self, ctx, points: int,
        member: commands.Greedy[int] = None):
        """Adds contribution points.

        Optionally, if a member is mentioned, then that member's record
        will be modified instead.

        e.g. $settings add point 20 @someone

        Args:
            ctx (discord.ext.commands.Context): context of the message
            points (int): the points to add; i.e. 1 talt = 20 points, etc
            member (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        if points < 1:
            return False
        if points % 20 != 0:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You entered an invalid amount of points!
                    Check unit or value (divisible by 20).
                    """
                    )
                )
            return False

        return await contribution_setter(ctx, points, member, append = True)

    @settings.group(
        name = 'delete',
        aliases = aliases_delete
        )
    @checks.only_in_guild()
    @checks.check_channel('settings')
    @checks.check_role()
    async def delete(self, ctx):
        """Deletes configurations, for `set` subcommands.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True always

        """
        return True

    @delete.group(
        name = 'role'
        )
    async def d_role(self, ctx):
        """Deletes Discord members/roles from Vaivora roles.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True always

        """
        try:
            ctx.role_type = ctx.invoked_subcommand.name
        except AttributeError:
            return False
        return True

    @d_role.command(
        name = 'member'
        )
    async def dr_member(self, ctx, mentions: commands.Greedy[int] = None):
        """Deletes Discord members/roles from `member`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if successful; False otherwise

        """
        return await role_deleter(ctx, mentions)

    @d_role.command(
        name = 'authorized',
        aliases = aliases_authorized
        )
    async def dr_auth(self, ctx, mentions: commands.Greedy[int] = None):
        """Deletes Discord members/roles from `authorized`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        return await role_deleter(ctx, mentions)

    @d_role.command(
        name = 'boss'
        )
    async def dr_boss(self, ctx, mentions: commands.Greedy[int] = None):
        """Deletes Discord members/roles from `boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        return await role_deleter(ctx, mentions)

    @d_role.command(
        name = 'events'
        )
    async def dr_events(self, ctx, mentions: commands.Greedy[int] = None):
        """Deletes Discord members/roles from `events`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            mentions (commands.Greedy[int], optional): a mention as a raw id;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """
        return await role_deleter(ctx, mentions)

    @delete.group(
        name = 'channel'
        )
    async def d_channel(self, ctx):
        """Deletes Discord channels from a given kind/type.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True always

        """
        try:
            ctx.channel_kind = ctx.invoked_subcommand.name
        except AttributeError:
            return False
        return True

    @d_channel.command(
        name = 'settings'
        )
    async def dc_settings(self, ctx):
        """Deletes Discord channels from `settings`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if successful; False otherwise

        """
        return await channel_deleter(ctx, ctx.channel_kind)

    @d_channel.command(
        name = 'boss'
        )
    async def dc_boss(self, ctx):
        """Deletes Discord channels from `boss`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if successful; False otherwise

        """
        return await channel_deleter(ctx, ctx.channel_kind)

    @d_channel.command(
        name = 'events'
        )
    async def dc_events(self, ctx):
        """Deletes Discord channels from `events`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            bool: True if successful; False otherwise

        """
        return await channel_deleter(ctx, ctx.channel_kind)


def setup(bot):
    bot.add_cog(SettingsCog(bot))
