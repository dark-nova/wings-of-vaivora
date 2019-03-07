from math import ceil
from typing import Optional

import discord
from discord.ext import commands

import checks
import constants.gems


gems = [0,
# Level 1    2     3     4      5      6       7        8        9       10
        0, 300, 1200, 3900, 14700, 57900, 230700, 1094700, 5414700, 9734700]
abrasives = gems[:-1]


class GemsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.remove_command('help')

    @commands.group()
    async def gems(self, ctx):
        pass

    @gems.command(name='help')
    async def _help(self, ctx):
        """
        :func:`_help` retrieves help pages for `$settings`.

        Args:
            ctx (discord.ext.commands.Context): context of the message

        Returns:
            True
        """
        _help = constants.gems.HELP
        for _h in _help:
            await ctx.author.send(_h)
        return True

    @gems.command(aliases=['experience', 'abrasives', 'abrasive'])
    async def exp(self, ctx, *abrs: str):
        """
        :func:`exp` calculates the exp obtained from abrasives.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            abrs: a list of abrasives to calculate, in the format
                QTY.LVL, where . is a delimiter of either
                'x' or '.'

        Returns:
            True always
        """
        gem_exp = 0
        errs = []
        if not abrs:
            await ctx.send(constants.gems.FAIL_NO_ABRS
                           .format(ctx.author.mention))
            return False

        for abrasive in abrs:
            try:
                a_qty, a_level = abrasive.split('x')
            except:
                try:
                    a_qty, a_level = abrasive.split('.')
                except ValueError:
                    errs.append(
                        constants.gems.INVALID_DELIM
                        .format(abrasive))
                    continue
                except:
                    continue

            a_qty = int(a_qty)
            a_level = int(a_level)

            try:
                gem_exp += a_qty * abrasives[a_level]
            except IndexError:
                errs.append(
                    constants.gems.INVALID_ALEVEL
                    .format(a_level))
                continue
            except:
                continue

        level = 0
        while gems[level+1] <= gem_exp and level < 10:
            level += 1

        leftover_exp = gem_exp - gems[level]

        await ctx.send('{}\n{}'
                       .format(ctx.author.mention,
                               constants.gems.SUCCESS_EXP
                               .format(level, leftover_exp,
                                       gem_exp)))
        if errs:
            await ctx.send(constants.gems.SOME_ERRORS)

            while len(errs) >= 20:
                await ctx.send('\n'.join(errs[:20]))
                errs = errs[20:]

            if len(errs) > 0:
                await ctx.send('\n'.join(errs))

        return True

    @gems.command(name='gem2lv', aliases=['gem2level'])
    async def gem_to_level(self, ctx, level: int, exp: int, final_level: int):
        """
        :func:`gem_to_level` calculates experience needed
        from a given gem level and experience to a `final_level`.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            level (int): the current gem level
            exp (int): the current gem experience
            final_level (int): the intended level

        Returns:
            True if successful; False otherwise
        """
        if level > 9 or final_level > 9 or level < 1 or final_level < 1:
            await ctx.send(constants.gems.INVALID_GLEVEL
                           .format(ctx.author.mention))
            return False
        if level >= final_level:
            await ctx.send(constants.gems.INVALID_FLEVEL
                           .format(ctx.author.mention))
            return False
        if gems[level+1] < (gems[level] + exp) or exp < 0:
            await ctx.send(constants.gems.INVALID_GEXP
                           .format(ctx.author.mention,
                                   exp, level))

        exp_diff = gems[final_level] - (gems[level] + exp)

        _abrasives = []

        a_level = 2 # abrasives below lv2 do not exist
        while abrasives[a_level] <= exp_diff and a_level < 10:
            a_qty = ceil(exp_diff/abrasives[a_level])
            _abrasives.append(constants.gems.ABRASIVE_TABLE
                              .format(a_level, a_qty))
            a_level += 1

        await ctx.send('{} {}'
                       .format(ctx.author.mention,
                               constants.gems.SUCCESS_GTL
                               .format(exp_diff)))
        await ctx.send('\n'.join(_abrasives))



def setup(bot):
    bot.add_cog(GemsCog(bot))
