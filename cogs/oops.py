from discord.ext import commands
from cogs.bot import send_embed, msg_history


class Oops(commands.Cog):
    """listens for the undo command."""

    @commands.command()
    async def oops(self, ctx):
        await undo_message(ctx)


async def undo_message(ctx):
    """delete the last bot massage on the current channel made by the user.

    bot will also remove the command that triggered this function:
        if command made in a text channel.
            bot cannot remove user's messages on a private channel (DM) because of permissions.
        this feature was included to truly leave no trace of a mistake.
    the bot stores the message for each channel separately.
        data structure: array of bot messages.
            therefore, user is able to delete more than one last bot message.
        using this command on one channel will not delete a message from another channel.
    users will not be able to delete a bot messages made by other users.
    data structure used to store past message is a python dictionary.
        dict (key = user's discord id, value = dict (key = channel id, value = array[message])).
    a 'no messages to delete' error message will be displayed:
        if the user not longer has any bot messages to delete in that channel.

    Parameters
    ----------
    :param Context ctx: the current Context.
    """
    if msg_history.get(ctx.author.id) is not None:
        if msg_history[ctx.author.id].get(ctx.channel.id) is not None:
            if len(msg_history[ctx.author.id][ctx.channel.id]) > 0:
                # remove the message that triggered this command on a text channel.
                if str(ctx.channel.type) == 'text':
                    await ctx.message.delete()
                # remove the last bot message from data structure and channel.
                return await msg_history.get(ctx.author.id).get(ctx.channel.id).pop().delete()

    # print error message.
    await send_embed(ctx, title='😬 Oops Command', text='there are no messages to delete.')


# connect this cog to bot.
def setup(bot):
    bot.add_cog(Oops(bot))
