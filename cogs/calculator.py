import discord
import re
from discord.ext import commands
from cogs.bot import send_embed


class Calculator(commands.Cog):
    """listens for the calculator app commands."""

    @commands.command()
    async def cal(self, ctx, *, expression=None):
        # evaluate given expression.
        await evaluate(ctx, expression)


async def evaluate(ctx, expression):
    """evaluates the given expression and display the result.

    WARNING:
        this command uses python's eval() method to calculate given expression.
        function should check for edge cases before eval() is called.
    display a 'expression cannot be evaluated':
        when expression cannot be evaluated.
    function will terminate to avoid users from abusing the eval():
        if the expression does not contain at least two digits.
        if the expression contains any letters.
    the result will be rounded to 3 decimal places.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param str expression: the expression to evaluate.
    """
    # edge cases.
    if check_edge_cases(expression) is False:
        return

    # evaluate expression.
    await evaluate_expression(ctx, expression)


async def evaluate_expression(ctx, expression):
    """evaluates the given expression

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param str expression: the expression to evaluate.
    """
    embed = discord.Embed(title='♾ Calculator')
    decimal_places = 3
    try:
        embed.description = f'result is {round(eval(expression), decimal_places)}.'
    except SyntaxError:
        embed.description = 'let me google that.'

    await send_embed(ctx, embed)


def check_edge_cases(expression):
    """checks for edge cases.

    Parameters
    ----------
    :param str expression: the expression to check.
    :return: True if all edge cases passes, otherwise return False.
    """
    # nothing to evaluate.
    if expression is None:
        return False

    # expression does not contain at least 2 digits.
    if len([x for x in expression if x.isdigit()]) < 2:
        return False

    # expression contains a letter.
    if re.compile('[a-zA-Z]+').search(expression) is not None:
        return False

    return True


# connect this cog to bot.
def setup(bot):
    bot.add_cog(Calculator(bot))
