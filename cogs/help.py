import os
from discord.ext import commands
from cogs.bot import send_embed, json_to_dict


class Help(commands.Cog):
    """listens for help message commands."""

    @commands.command()
    async def help(self, ctx, arg: str = None):
        # print help message.
        category = arg
        if arg is not None:
            category = f'{os.getenv("BOT_PREFIX")}{category}'

        return await get_help_msg(ctx, category)


async def get_help_msg(ctx, help_command=None):
    """returns a str of the help message for given command.

    display every public help message by default.
    display a 'no help message was found' error message:
        if the command is not found in the help_msg help message.
    help files are read from local .json file.
    help messages are stored in a local file
        so others can make modification to it without needing to edit the code.
    help messages are stored in multiple files:
        to avoid hitting the character limit of one message sent
            help messages will be sent in multiple messages (per file) by the bot.
        to be used by other bots.
            with multiple files bots can filter what help messages to use.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param str help_command: the command help message to print.
    """
    help_message_found = False
    separator = '\n'

    # get all help message files.
    file_directory = 'json_files/help_msg/'
    for help_file in os.listdir(file_directory):
        help_msg = []
        # get all commands in help file.
        categories = json_to_dict(f'{file_directory}/{help_file}')
        for category in categories:
            message = []
            for command in categories[category]:
                prefix = os.getenv("BOT_PREFIX")
                description = categories[category][command]

                # return all or specific help command messages.
                string = f'{prefix}{command}'
                if help_command is None or string.startswith(help_command):
                    message.append(f'`{string}` - {description}')
                    help_message_found = True

            # print the help message only if needed.
            if len(message) > 0:
                help_msg.append(f'__**{category}**__')
                help_msg.append(separator.join(message))
                help_msg.append('')

        await send_embed(ctx, title=get_help_title(), text=separator.join(help_msg))

    # print error message.
    if help_message_found is False:
        await send_embed(ctx, title=get_help_title(), text=f'no help message was found for `{help_command}`')


def get_help_title():
    """:return: a str that represents the default embed title for this command."""
    return '💬 Bot Usage Examples'


# connect this cog to bot.
def setup(client):
    client.add_cog(Help(client))
