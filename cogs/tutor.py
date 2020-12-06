import discord
import os
from discord.ext import commands
from cogs.bot import send_embed, to_member


class Tutor(commands.Cog):

    @commands.command()
    async def tutor(self, ctx, arg=None, arg2=None, arg3=None):
        """listens for the tutor commands.

        Parameters
        -----------
        :param Context ctx: the current Context.
        :param str arg: the first argument.
        :param str arg2: the second argument.
        :param str arg3: the third argument.
        """
        if arg is None:
            return

        if await is_tutor(ctx) is False:
            return


async def is_tutor(ctx):
    """checks if member has the tutor role.

    a tutor role should be granted to members that has permission to use tutor commands.
    display a 'permission not found' error message:
        if the member does not have tutor permissions.

    Parameters
    -----------
    :param Context ctx: the current Context.
    :return: True if the member has a tutor role tag, False otherwise.
    """
    for role in to_member(ctx.author.id).roles:
        if role.id == int(os.getenv("TUTOR_ROLE_ID")):
            return True

    # display error message.
    embed = discord.Embed(description='*tutor\'s permission not found.*')
    await send_embed(ctx, embed)

    return False


# connect this cog to bot.
def setup(bot):
    bot.add_cog(Tutor(bot))
