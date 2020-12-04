import discord
import os
from discord.ext import commands
from cogs.bot import send_embed, json_to_dict


class Java(commands.Cog):
    """listens for the java_cheat_sheet commands."""

    @commands.command()
    async def java(self, ctx, arg: str = None):
        if arg is not None:
            await get_java_cheat_sheet(ctx, arg)


async def get_java_cheat_sheet(ctx, method):
    """displays a java_cheat_sheet cheat sheet for a given class.

    each class method is stored in its own .json file
        so others can make modification to content without touching the code.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param str method: the specific method to display.
    """
    embed = discord.Embed(title=f'☕ Java {method.lower().capitalize()} Methods')

    # print cheat sheet.
    file_directory = 'json_files/java_cheat_sheet'
    java_file = f'{method.lower()}.json'
    for file in os.listdir(file_directory):
        if java_file == file:
            cheat_sheet = json_to_dict(f'{file_directory}/{java_file}')
            embed.description = get_cheat_sheet(cheat_sheet)

            return await send_embed(ctx, embed)


def get_cheat_sheet(cheat_sheet):
    """converts a cheat sheet from .json to string to display

    Parameters
    ----------
    :param dictionary cheat_sheet: dictionary that stores the content of given cheat sheet.
    :return: a str representation of a cheat sheet.
    """
    sheet = []
    separator = '\n'

    for data_type in cheat_sheet:
        sheet.append(f'__**{data_type}**__')
        for method in cheat_sheet[data_type]:
            method_description = cheat_sheet[data_type][method]
            sheet.append(f'**{method}** - {method_description}')
        sheet.append('')

    return separator.join(sheet)


def get_available_java_class():
    """stores every available java_cheat_sheet cheat sheet class in an array.

    :return: an array of available java_cheat_sheet class
    """

    return ['array', 'list', 'map', 'math', 'queue', 'scanner', 'string']


# connect this cog to bot.
def setup(bot):
    bot.add_cog(Java(bot))
