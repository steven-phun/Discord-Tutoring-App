import discord
import os
from discord.ext import commands
from cogs.bot import bot, send_embed, json_to_dict, to_member


class Developer(commands.Cog):
    """listens for the bot developer commands.

    developer commands are reserved only for developers that works on this bot.
    """

    @commands.command()
    async def dev(self, ctx, arg, arg2=None):
        # check for dev role.
        if is_developer(ctx) is False:
            return

        # print the developer help message.
        if arg.lower() == 'help':
            return await display_dev_help_msg(ctx)

        if arg.lower() == 'app':
            await display_available_apps(ctx)

        # WARNING: other dev commands need to go above this edge case.
        if arg2 is None:
            return

        # modify cogs file.
        await modify_cogs_file(ctx, arg, arg2)


async def modify_cogs_file(ctx, action, cog):
    """load or unload given cog file.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param str action: the action to take on the cog (load/unload).
    :param str cog: the cog to load or unload.
    """
    embed = get_dev_embed()

    # try except if extension exists.
    try:
        # loads a cog file without having to reset the bot.
        if action.lower() == 'load':
            bot.load_extension(f'cogs.{cog}')
            embed.description = f'{cog} app loaded.'

        # unload a cog file without having to reset the bot.
        if action.lower() == 'unload':
            bot.unload_extension(f'cogs.{cog}')
            embed.description = f'{cog} app unloaded.'

        # reloads a cog file without having to reset the bot.
        if action.lower() == 'reload':
            bot.unload_extension(f'cogs.{cog}')
            bot.load_extension(f'cogs.{cog}')
            embed.description = f'{cog} app reloaded.'
    except discord.ext.commands.errors.ExtensionNotLoaded:
        embed.description = f'`{cog}` file not found.'

    await send_embed(ctx, embed)


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

    embed = get_dev_embed(separator.join(help_msg))
    await send_embed(ctx, embed)


async def display_available_apps(ctx):
    """display all available application developers can load or unload.

    Parameters
    ----------
    :param Context ctx: the current Context.
    """
    embed = get_dev_embed()

    # get all available application files.
    file_directory = 'cogs'
    for file in os.listdir(file_directory):
        if file.endswith('.py'):
            embed.description += f'- {file.replace(".py", "")}\n'

    await send_embed(ctx, embed)


def get_dev_embed(description=''):
    """generate a default discord embed for the Bot Developers.

    Parameters
    ----------
    :param str description: the description to initialize the embed with.
    :return: a discord.embeds.Embed for the Bot Developers.
    """

    return discord.Embed(title='🤖 Bot Developers', description=description)


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
def setup(bot):
    bot.add_cog(Developer(bot))
