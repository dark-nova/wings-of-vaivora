from inspect import cleandoc

import discord
import pendulum
from discord.ext import commands

import checks
import vaivora.db


HELP = []
HELP.append(
    cleandoc(
        """
        ```
        Usage:
            $offset set (tz <tz>|offset <offset>)
            $offset get (tz|offset)
            $offset list

        Examples:
            $offset set tz 1
                Means: Set the offset of this guild to 1.
            $offset get tz
                Means: Shows list of tzs.
            $offset list
                Means: List all tz time zones to choose.
        ```
        """
        )
    )

HELP.append(
    cleandoc(
        """
        ```
        Options:
            set
                Sets the next parameter.

            get
                Gets the next parameter.

            tz
                Not to be confused with <tz>.
                The parameter name for time zone.

            <tz>
                The tz to use. Can be a given integer from the list, where:
                    [0] America/New_York    [NA]    Klaipeda      default
                    [1] America/Sao_Paulo   [SA]    Silute
                    [2] Europe/Berlin       [EU]    Fedimian
                    [3] Asia/Singapore      [SEA]   Telsiai
                You are also allowed to enter your own time zone if desired. See below.
                Custom tzs must be listed as *canonical* in the Wikipedia table.

            offset
                Not to be confused with <offset>.
                The parameter name for offset.

            <offset>
                The offset from server time.
                For instance, if you are 1 hour behind your chosen server, use offset `-1`.

            list
                Lists the available <tz>s to pick.
        ```
        Time zones: <https://en.wikipedia.org/wiki/List_of_tz_database_time_zones>
        """
        )
    )

server_tz = [
    'America/New_York',
    'America/Sao_Paulo',
    'Europe/Berlin',
    'Asia/Singapore'
    ]

numbered_tz = [
    f'[{n}] {tz}'
    for n, tz
    in enumerate(server_tz)
    ]

bullet_point = '\n- '


class OffsetCog(commands.Cog):
    """Interface for the `$offset` commands.

    Note that any changes set here will permanently affect
    the `$boss` command!

    `$offset` is an extension to `$settings`.

    This cog interacts with the `vaivora.db` backend.

    """

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.group()
    async def offset(self, ctx):
        pass

    @offset.command(
        name='help',
        )
    async def _help(self, ctx):
        """Retrieves help pages for `$offset`.

        Args:

        Returns:
            bool: True

        """
        for _h in HELP:
            await ctx.author.send(_h)
        return True

    @offset.group(
        name='set',
        )
    @checks.only_in_guild()
    @checks.check_channel('settings')
    @checks.check_role()
    async def _set(self, ctx):
        pass

    @_set.command(
        name='tz',
        aliases=[
            'timezone',
            'timezones',
            ],
        )
    async def s_tz(self, ctx, tz):
        """Sets the guild time zone.

        Args:
            tz: a timezone; could be an index of `server_tz`, or a tzstr

        Returns:
            bool: True if successful; False otherwise

        """
        try:
            tz = server_tz[int(tz)]
        except (IndexError, TypeError):
            try:
                tz = pendulum.timezone(tz)
            except pendulum.tz.zoneinfo.exceptions.InvalidTimezone:
                await ctx.send(
                    cleandoc(
                        f"""{ctx.author.mention}

                        You have entered an invalid time zone value!
                        """
                        )
                    )

        vdb = vaivora.db.Database(ctx.guild.id)
        if await vdb.set_tz(tz):
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You have successfully modified the guild time zone.
                    """
                    )
                )
            return True
        else:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Couldn't save to database. Check file permissions.
                    """
                    )
                )
            return False

    @_set.command(
        name='offset',
        )
    async def s_offset(self, ctx, offset: int):
        """Sets the offset from the guild time zone.

        Note that offset is not the same as time zone; rather,
        offset is the actual offset from the guild time zone.

        Args:
            offset (int): the offset to use; -23 <= offset <= 23

        Returns:
            bool: True if successful; False otherwise

        """
        if offset > 23 or offset < -23:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You have entered an invalid offset value!
                    """
                    )
                )
            return False

        vdb = vaivora.db.Database(ctx.guild.id)
        if await vdb.set_offset(offset):
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You have successfully modified the guild offset.
                    """
                    )
                )
            return True
        else:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Couldn't save to database. Check file permissions.
                    """
                    )
                )
            return False

    @offset.group(
        name='get',
        )
    @checks.only_in_guild()
    @checks.check_role('member')
    async def _get(self, ctx):
        pass

    @_get.command(
        name='tz',
        aliases=[
            'timezone',
            'timezones',
            ],
        )
    async def g_tz(self, ctx):
        """Retrieves the guild time zone.

        Args:

        Returns:
            bool: True if successful; False otherwise

        """
        vdb = vaivora.db.Database(ctx.guild.id)
        tz = await vdb.get_tz()

        if tz:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Your guild's time zone is {tz}.
                    """
                    )
                )
            return True
        else:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Your guild doesn't appear to have a time zone set.
                    """
                    )
                )
            return False

    @_get.command(
        name='offset',
        )
    async def g_offset(self, ctx):
        """Retrieves the guild's offset from the guild time zone.

        Args:

        Returns:
            bool: True if successful; False otherwise

        """
        vdb = vaivora.db.Database(ctx.guild.id)
        offset = await vdb.get_offset()

        if offset:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Your guild's time zone is {offset}.
                    """
                    )
                )
            return True
        else:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Your guild doesn't appear to have an offset set.
                    """
                    )
                )
            return False

    @offset.command(
        name='list',
        )
    async def _list(self, ctx):
        """Lists the available time zones for servers.

        Note that this is locked to the international version of TOS ("ITOS").

        Args:

        Returns:
            bool: True always

        """
        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                Here are the tz time zones available:

                - {bullet_point.join(numbered_tz)}
                """
                )
            )
        return True


def setup(bot):
    bot.add_cog(OffsetCog(bot))
