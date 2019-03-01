import discord
from discord.ext import commands

import checks


gems = [0, 0, 300, 1200, 3900, 14700, 57900, 230700, 1094700, 5414700, 9734700]
abrasives = [:-1]


class GemsCog:

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def gems(self, ctx)
        pass

    @gems.command(aliases=['experience', 'abrasives', 'abrasive'])
    async def exp(self, ctx, abrasives: commands.Greedy[str]):
        """
        :func:`exp` calculates the exp obtained from abrasives.

        Args:
            ctx (discord.ext.commands.Context): context of the message
            abrasives: a list of abrasivse to calculate, in the format
                QTY.LVL, where . is a delimiter of either
                'x' or '.'

        Returns:
            True always
        """
        gem_exp = 0
        errs = []
        for abrasive in abrasives:
            try:
                a_qty, a_level = abrasive.split('x')
            except:
                try:
                    a_qty, a_level = abrasive.split('.')
                except ValueError:
                    errs.append(
                        '{} has an invalid delimiter!'
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
                    '{} is an invalid abrasive level!'
                    .format(a_level))
                continue
            except:
                continue

        level = 1
        while gems[level] <= gem_exp and level < 10:
            level += 1

        leftover_exp = gem_exp - gems[level]

        await ctx.send('{}\n\n{}'
                       .format(ctx.author.mention,
                               """You can make a level {} gem,
                                  with {} leftover experience.
                                  \nTotal gem experience: {}"""
                               .format(level, leftover_exp,
                                       gem_exp)))
        if errs:
            await ctx.send('\nAdditionally, errors were detected:')

            while len(errs) >= 20:
                await ctx.send('\n'.join(errs[:20]))
                errs = errs[20:]

            if len(errs) > 0:
                await ctx.send('\n'.join(errs))

        return True

def setup(bot):
    bot.add_cog(GemsCog(bot))
