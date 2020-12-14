import discord
import os
from discord.ext import commands
from cogs.bot import bot, send_embed, json_to_dict, to_member


class Developer(commands.Cog):
    """listens for the bot developer commands.

    REQUIRED: developer's role.

    developer commands are reserved only for developers that works on this bot.
    """
    @commands.command()
    async def dev(self, ctx, arg, arg2=None):
        # check if member has the dev role.
        if is_developer(ctx) is False:
            return

        # display the developer's help message.
        if arg.lower() == 'help':
            return await display_dev_help_msg(ctx)

        # display all available cogs.
        if arg.lower() == 'app':
            await display_available_apps(ctx)

        # display a blank google form link.
        if arg.lower() == 'form':
            await display_blank_google_form(ctx)

        # load, unload, or reload a cog.
        if arg.lower() == 'load' or arg.lower() == 'unload' or arg.lower() == 'reload':
            await modify_cogs_file(ctx, arg, arg2)


async def modify_cogs_file(ctx, action, cog):
    """load or unload given cog file.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param str action: the action to take on the cog (load/unload).
    :param str cog: the cog to load or unload.
    """
    # try except if extension exists.
    description = ''
    try:
        # loads a cog file without having to reset the bot.
        if action.lower() == 'load':
            bot.load_extension(f'cogs.{cog}')
            description = f'{cog} app loaded.'

        # unload a cog file without having to reset the bot.
        if action.lower() == 'unload':
            bot.unload_extension(f'cogs.{cog}')
            description = f'{cog} app unloaded.'

        # reloads a cog file without having to reset the bot.
        if action.lower() == 'reload':
            bot.unload_extension(f'cogs.{cog}')
            bot.load_extension(f'cogs.{cog}')
            description = f'{cog} app reloaded.'
    except discord.ext.commands.errors.ExtensionNotLoaded:
        description = f'`{cog}` file not found.'

    await send_embed(ctx, title=get_dev_title(), text=description)


async def display_dev_help_msg(ctx):
    """displays the developer's help message.

    Parameters
    ----------
    :param Context ctx: the current Context.
    """
    help_msg = []
    separator = '\n'
    file = json_to_dict('json_files/developers/dev_help_msg.json')
    prefix = os.getenv("BOT_PREFIX")
    for category in file:
        help_msg.append(f'__**{category}**__')
        for command in file[category]:
            description = file[category][command]
            help_msg.append(f'`{prefix}{command}` - {description}')
        help_msg.append('')

    await send_embed(ctx, title=get_dev_title(), text=separator.join(help_msg))


async def display_available_apps(ctx):
    """display all available application developers can load or unload.

    Parameters
    ----------
    :param Context ctx: the current Context.
    """
    # get all available application files.
    description = ''
    for file in os.listdir('cogs'):
        if file.endswith('.py') and not file.startswith('bot'):
            description += f'- {file.replace(".py", "")}\n'

    await send_embed(ctx, title=get_dev_title(), text=description)


async def display_blank_google_form(ctx):
    """display a non prefilled google form for student to sign in with.

    this function is here in case the bot is unable to provide the students their prefilled link.

    Parameters
    ----------
    :param Context ctx: the current Context.
    """
    await send_embed(ctx, text=f'sign-in sheet [click here]({os.getenv("GOOGLE_FORM_LINK")})')


def get_dev_title():
    """:return: a str that represents the default embed title for this command."""
    return '🤖 Bot Developers'


def is_developer(ctx):
    """checks if a user has permission to use the developer commands.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :return: True if user has the 'developer' role, otherwise return False.
    """
    member = to_member(ctx.author.id)
    for role in member.roles:
        if role.id == int(os.getenv("DEVELOPERS_ROLE_ID")):
            return True

    return False


# connect this cog to bot.
def setup(client):
    client.add_cog(Developer(client))
