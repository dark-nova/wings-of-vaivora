import asyncio
import logging
import re
from math import ceil
from inspect import cleandoc
from typing import Optional

import discord
from discord.ext import commands

import checks


HELP = []
HELP.append(
    cleandoc(
        """
        ```
        Usage:
            $gems exp (<abrasive> ...)
            $gems level <gem-level> <gem-exp> <final-level>
            $gems values <color> [<equip>]
            $gems efficiency <color> [<equip>]
            $gems help

        Examples:
            $gems exp 2x2 3x4
                Means: Calculate total gem experience using 2 level 2 and 3 level 4 gem abrasives.
            $gems level 1 0 5
                Means: Calculate gem experience needed to level a level 1, 0 experience gem to a level 5.
            $gems values red top
                Means: Show the stat values for Red Gems in Top/Bottom equipment.
            $gems efficiency blue
                Means: Show all equipment stat-to-experience efficiency for Blue Gems
        ```
        """
        )
    )
HELP.append(
    cleandoc(
        """
        ```
        Options:
            exp
                The command to calculate how much gem experience you can get from any number of abrasives.
                Aliases: `experience`, `abrasives`, `abrasive`

            <abrasive>
                A format like QTY.LV, where QTY is quantity and LV is level of the abrasive.
                You must include either '.' or 'x' to separate the two numbers.
                `$gems exp` accepts 1 or more of this argument.

            level
                The command to show much gem experience you need to level a gem from its current level to a desired level.
                Aliases: `lv`, `lvl`

            <gem-level>
                The current gem level. Ranges from 1 to 9, for the purpose of this program.

            <gem-exp>
                The current gem experience listed in the gem's UI. Ranges from 0 to 1 below its current maximum.

            <final-level>
                The final level to achieve. Must be higher than <gem-level> and between 2 to 9.

            values
                The command to show what stat values a gem gives at all levels.
                Aliases: `value`, `val`

            efficiency
                The command to show efficiency of values per experience, shown in percent.
                Aliases: `eff`

            <color>
                The color gem to specify.

            [<equip>]
                An optional argument for `values` and `efficiency`.
                Filters equipment to use. If invalid or omitted, all equipment will be shown instead.

            help
                Prints this page.
        ```
        """
        )
    )

newline = '\n'

gems = [0,
# Level 1    2     3     4      5      6       7        8        9       10
        0, 300, 1200, 3900, 14700, 57900, 230700, 1094700, 5414700, 9734700]
abrasives = gems[:-1]

colors = {}
colors['Red'] = re.compile(r're?d?', re.IGNORECASE)
colors['Blue'] = re.compile(r'b(lu?e?)?', re.IGNORECASE)
colors['Yellow'] = re.compile(r'y(e?ll?o?w?)', re.IGNORECASE)
colors['Green'] = re.compile(r'g(r?e+)?n?', re.IGNORECASE)
colors['White'] = re.compile(r'w(hi?t)?e?', re.IGNORECASE)

equips = {}
equips['Top/Bottom'] = re.compile(r'(t(o?p)?|b(ottom)?)', re.IGNORECASE)
equips['Weapons'] = re.compile(r'((sub)?w(ea?po?n?)?|shi.*)', re.IGNORECASE)
equips['Glove/Shoe'] = re.compile(r'(g(love)?|s(hoe)?|boot)', re.IGNORECASE)

values = {}
values['Red'] = {}
values['Red']['Top/Bottom'] = {}
values['Red']['Top/Bottom']['Block'] = [
    0, 15, 23, 31, 39, 46, 54, 62, 70, 78, 85
    ]
values['Red']['Top/Bottom']['Accuracy'] = [
    0, -3, -5, -7, -9, -11, -13, -15, -17, -19, -21
    ]
values['Red']['Weapons'] = {}
values['Red']['Weapons']['Physical Attack'] = [
    0, 72, 105, 138, 172, 207, 240, 273, 307, 342, 375
    ]
values['Red']['Weapons']['Critical Rate'] = [
    0, -3, -5, -7, -9, -11, -13, -15, -17, -19, -21
    ]
values['Red']['Glove/Shoe'] = {}
values['Red']['Glove/Shoe']['Accuracy'] = [
    0, 15, 23, 31, 39, 46, 54, 62, 70, 78, 85
    ]
values['Red']['Glove/Shoe']['Physical Critical Attack'] = [
    0, -32, -46, -61, -76, -92, -106, -121, -136, -152, -166
    ]

values['Blue'] = {}
values['Blue']['Top/Bottom'] = {}
values['Blue']['Top/Bottom']['Magic Defense'] = [
    0, 360, 525, 690, 860, 1035, 1200, 1365, 1535, 1710, 1875
    ]
values['Blue']['Top/Bottom']['Physical Defense'] = [
    0, -90, -131, -172, -215, -258, -300, -341, -383, -427, -468
    ]
values['Blue']['Weapons'] = {}
values['Blue']['Weapons']['Magic Attack'] = [
    0, 72, 105, 138, 172, 207, 240, 273, 307, 342, 375
    ]
values['Blue']['Weapons']['Critical Rate'] = [
    0, -3, -5, -7, -9, -11, -13, -15, -17, -19, -21
    ]
values['Blue']['Glove/Shoe'] = {}
values['Blue']['Glove/Shoe']['Critical Resistance'] = [
    0,  15, 23, 31, 39, 46, 54, 62, 70, 78, 85
    ]
values['Blue']['Glove/Shoe']['Maximum Attack'] = [
    0, -40, -58, -77, -96, -115, -133, -152, -171, -190, -208
    ]

values['Yellow'] = {}
values['Yellow']['Top/Bottom'] = {}
values['Yellow']['Top/Bottom']['Physical Defense'] = [
    0, 360, 525, 690, 860, 1035, 1200, 1365, 1535, 1710, 1875
    ]
values['Yellow']['Top/Bottom']['Magic Defense'] = [
    0, -90, -131, -172, -215, -258, -300, -341, -383, -427, -468
    ]
values['Yellow']['Weapons'] = {}
values['Yellow']['Weapons']['Physical Critical Attack'] = [
    0, 128, 187, 246, 307, 368, 427, 486, 547, 608, 667
    ]
values['Yellow']['Weapons']['Maximum Attack'] = [
    0, -3, -5, -7, -9, -11, -13, -15, -17, -19, -21
    ]
values['Yellow']['Glove/Shoe'] = {}
values['Yellow']['Glove/Shoe']['Block Penetration'] = [
    0, 15, 23, 31, 39, 46, 54, 62, 70, 78, 85
    ]
values['Yellow']['Glove/Shoe']['Critical Rate'] = [
    0, -3, -5, -7, -9, -11, -13, -15, -17, -19, -21
    ]

values['Green'] = {}
values['Green']['Top/Bottom'] = {}
values['Green']['Top/Bottom']['Evasion'] = [
    0, 15, 23, 31, 39, 46, 54, 62, 70, 78, 85
    ]
values['Green']['Top/Bottom']['Maximum Attack'] = [
    0, -40, -58, -77, -96, -115, -133, -152, -171, -190, -208
    ]
values['Green']['Weapons'] = {}
values['Green']['Weapons']['Magic Critical Attack'] = [
    0, 128, 187, 246, 307, 368, 427, 486, 547, 608, 667
    ]
values['Green']['Weapons']['Block Penetration'] = [
    0, -3, -5, -7, -9, -11, -13, -15, -17, -19, -21
    ]
values['Green']['Glove/Shoe'] = {}
values['Green']['Glove/Shoe']['Critical Rate'] = [
    0, 15, 23, 31, 39, 46, 54, 62, 70, 78, 85
    ]
values['Green']['Glove/Shoe']['Block'] = [
    0, -3, -5, -7, -9, -11, -13, -15, -17, -19, -21
    ]

values['White'] = {}
values['White']['Top/Bottom'] = {}
values['White']['Top/Bottom']['Looting Chance'] = [
    0, 4, 6, 10, 14, 19, 24, 30, 36, 43, 50
    ]
values['White']['Top/Bottom']['INT'] = [
    0, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10
    ]
values['White']['Weapons'] = {}
values['White']['Weapons']['Looting Chance'] = [
    0, 4, 6, 10, 14, 19, 24, 30, 36, 43, 50
    ]
values['White']['Weapons']['STR'] = [
    0, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10
    ]
values['White']['Glove/Shoe'] = {}
values['White']['Glove/Shoe']['Looting Chance'] = [
    0, 4, 6, 10, 14, 19, 24, 30, 36, 43, 50
    ]
values['White']['Glove/Shoe']['CON'] = [
    0, -1, -2, -3, -4, -5, -6, -7, -8, -9, -10
    ]

logger = logging.getLogger('vaivora.cogs.gems')
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


async def which_one(ctx, opt: str, opts: dict, kind: str):
    """Finds and gets the valid reference given an `opt`ion.

    Options are colors and equips.

    Args:
        opt (str): the option input by the user
        opts (dict): the valid options
        kind (str): the kind of option to compare

    Returns:
        str: the option name, if matched
        None: if none were matched

    """
    for option, regex in opts.items():
        if regex.match(opt):
            return option

    await ctx.send(
        cleandoc(
            f"""{ctx.author.mention}

            **{opt}** is not a valid {kind}!
            """
            )
        )
    return None


async def format_stats(color: str, equip: str):
    """Formats stats to create a uniform message block.

    Args:
        color (str): color of the gem
        equip (str): the equip slot to use

    Returns:
        str: a formatted message with all values and stats

    """
    for stat, stat_values in values[color][equip].items():
        # i = level - 1
        formatted = ''.join([f'{stat_values[i+1]:>5}' for i in range(10)])
        if stat_values[1] > 0:
            pos_stat = stat
            positive = formatted
        else:
            neg_stat = stat
            negative = formatted
    return cleandoc(
        f"""{color} Gem for {equip}
        ```diff
        {pos_stat}
        +{positive}

        {neg_stat}
        -{negative}
        ```
        """
        )


async def format_efficiency(color: str, equip: str):
    """Calculates how efficient a gem level is relative to experience.

    Results are formatted similar to `format_stats`.

    Args:
        color (str): color of the gem
        equip (str): the equip slot to use

    Returns:
        str: a formatted message with only efficiency per level

    """
    for stat, stat_values in values[color][equip].items():
        # we only want positive values to compare efficiency
        if stat_values[1] < 0:
            continue
        efficiency = [
            (val*100/exp) if exp != 0 else 0
            for val, exp
            in zip(stat_values, gems)
            ]
        # As with `format_stats`, i = level - 1
        formatted = ''.join(
            [
                f'{efficiency[i+1]:>7.2f}' for i in range(1, 10)
                ]
            )
        # Unlike the return block in `format_stats`, only one
        # set of stats is used. The return block here could either
        # be inline to the loop or outside; no difference.
        return cleandoc(
            f"""{color} Gem for {equip}, lv.2 to lv.10
            ```diff
            {stat}
            +%{formatted}
            ```
            """
            )


class GemsCog(commands.Cog):
    """Interface for the `$gems` commands."""

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.group()
    async def gems(self, ctx):
        pass

    @gems.command(
        name='help',
        )
    async def _help(self, ctx):
        """Retrieves help pages for `$gems`.

        Args:

        Returns:
            bool: True

        """
        for _h in HELP:
            await ctx.author.send(_h)
        return True

    @gems.command(
        aliases=[
            'abrasive',
            'abrasives',
            'experience',
            ],
        )
    async def exp(self, ctx, *abrs: str):
        """Calculates the experience obtained from abrasives.

        Args:
            abrs: a list of abrasives to calculate, in the format
                QTY.LVL, where . is a delimiter of either
                'x' or '.'

        Returns:
            bool: True always

        """
        gem_exp = 0
        errs = []
        if not abrs:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    No abrasives were supplied!
                    """
                    )
                )
            return False

        for abrasive in abrs:
            try:
                a_qty, a_level = abrasive.split('x')
            except ValueError:
                try:
                    a_qty, a_level = abrasive.split('.')
                except ValueError:
                    errs.append(
                        f'{abrasive} has an invalid delimiter!'
                        )
                    continue
                except Exception as e:
                    logger.error(
                        f'Caught {e} in cogs.gems: exp; '
                        f'guild: {ctx.guild.id}; '
                        f'user: {ctx.author.id}; '
                        f'command: {ctx.command}'
                        )
                    errs.append(
                        f'{abrasive} is an invalid input and was ignored.'
                        )
                    continue

            a_qty = int(a_qty)
            a_level = int(a_level)

            try:
                gem_exp += a_qty * abrasives[a_level]
            except IndexError:
                errs.append(
                    f'{a_level} is an invalid abrasive level!'
                    )
                continue
            except Exception as e:
                logger.error(
                    f'Caught {e} in cogs.gems: exp; '
                    f'guild: {ctx.guild.id}; '
                    f'user: {ctx.author.id}; '
                    f'command: {ctx.command}'
                    )
                continue

        level = 0
        while gems[level+1] <= gem_exp and level < 10:
            level += 1

        leftover_exp = gem_exp - gems[level]

        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                You can make a level {level} gem, """
                f"""with {leftover_exp} leftover experience.
                Total gem experience: {gem_exp}
                """
                )
            )
        if errs:
            await ctx.send('\nAdditionally, errors were detected:')

            for err in await vaivora.common.chunk_messages(
                errs, 20, newlines=1
                ):
                async with ctx.typing():
                    await asyncio.sleep(1)
                    await ctx.send(err)

        return True

    @gems.command(
        aliases=[
            'lv',
            'lvl',
            ],
        )
    async def level(self, ctx, level: int, exp: int, final_level: int):
        """Calculates experience needed from a given gem level
        and experience to a `final_level`.

        `level` must always be less than `final_level`.

        `final_level` cannot exceed 10. `level` cannot be under 1.

        Args:
            level (int): the current gem level
            exp (int): the current gem experience
            final_level (int): the intended level

        Returns:
            bool: True if successful; False otherwise

        """
        if level > 9 or final_level > 10 or level < 1 or final_level < 1:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    You have entered an invalid gem level!
                    """
                    )
                )
            return False
        if level >= final_level:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    Final level is below starting level!
                    """
                    )
                )
            return False
        if gems[level+1] < (gems[level] + exp) or exp < 0:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    {exp} experience is invalid for gem level {level}!
                    """
                    )
                )

        exp_diff = gems[final_level] - (gems[level] + exp)

        valid_abrasives = []

        a_level = 2 # abrasives below lv2 do not exist
        while a_level < 10 and abrasives[a_level] <= exp_diff:
            a_qty = ceil(exp_diff/abrasives[a_level])
            valid_abrasives.append(
                f"""Abrasive level {a_level} quantity: {a_qty}"""
                )
            a_level += 1

        await ctx.send(
            cleandoc(
                f"""{ctx.author.mention}

                You need {exp_diff} experience for your gem.

                Additionally, the following table is provided as a reference:
                """
                )
            )
        await ctx.send('\n'.join(valid_abrasives))

    @gems.command(
        aliases=[
            'val',
            'value',
            ],
        )
    async def values(self, ctx, color: str, equip: Optional[str] = None):
        """Gets values of a gem given `color` and `equip` slot.

        Args:
            color (str): the color of the gem
            equip (Optional[str]): an optional equip to filter by;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """

        color = await which_one(ctx, color, colors, 'color')

        if not color:
            return False

        if equip:
            equip = await which_one(ctx, equip, equips, 'equip')

        blocks = []

        if equip:
            blocks.append(await format_stats(color, equip))
        else:
            for equip in values[color]:
                blocks.append(await format_stats(color, equip))

        try:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    {newline.join(blocks)}
                    """
                    )
                )
            return True
        except Exception as e:
            logger.error(
                f'Caught {e} in cogs.gems: values; '
                f'guild: {ctx.guild.id}; '
                f'user: {ctx.author.id}; '
                f'command: {ctx.command}'
                )
            return False

    @gems.command(
        aliases=[
            'eff',
            ],
        )
    async def efficiency(self, ctx, color: str, equip: Optional[str] = None):
        """Gets efficiency of values of a gem given `color` and `equip` slot.

        Efficiency is the value to experience ratio. Larger = better,
        smaller = worse.

        Args:
            color (str): the color of the gem
            equip (Optional[str]): an optional equip to filter by;
                defaults to None

        Returns:
            bool: True if successful; False otherwise

        """

        color = await which_one(ctx, color, colors, 'color')

        if not color:
            return False

        if equip:
            equip = await which_one(ctx, equip, equips, 'equip')

        blocks = []

        if equip:
            blocks.append(await format_efficiency(color, equip))
        else:
            for equip in values[color]:
                blocks.append(await format_efficiency(color, equip))

        try:
            await ctx.send(
                cleandoc(
                    f"""{ctx.author.mention}

                    {newline.join(blocks)}
                    """
                    )
                )
            return True
        except Exception as e:
            logger.error(
                f'Caught {e} in cogs.gems: efficiency; '
                f'guild: {ctx.guild.id}; '
                f'user: {ctx.author.id}; '
                f'command: {ctx.command}'
                )
            return False


def setup(bot):
    bot.add_cog(GemsCog(bot))
