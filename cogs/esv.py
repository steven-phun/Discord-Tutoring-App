import os
import requests
from discord.ext import commands
from cogs.bot import send_embed


class ESV(commands.Cog):
    """listens for the ESV Bible commands."""

    @commands.command()
    async def esv(self, ctx, *, passage: str = None):
        if passage is None:
            return

        # Bible verse numbers are wrapped with '[]' in the api
        # replace brackets with discord's single line code block.
        description = get_esv_verse(passage).replace('[', '`').replace(']', '`')

        await send_embed(ctx, title='🙏🏻 English Standard Version', text=description)


def get_esv_verse(passage):
    """looks up the given passage in English Standard Version using an ESV API.

    for the api's documentation and optional parameters:
        https://api.esv.org/docs/passage-text/
    the api returns the passage in a .json format.
    the .json file will be converted to a str and then printed to the user.

    Parameters
    ----------
    :param str passage: the book, chapter, and verse to look up.
    :return: a string of the given passage.
    """
    url = 'https://api.esv.org/v3/passage/text'

    params = {
        'q': passage,
        'include-footnotes': False,  # do not display footnotes.
        'include-short-copyright': False  # do not display (ESV)
    }

    headers = {
        'Authorization': f'Token {os.getenv("ESV_API_KEY")}'
    }

    # get passage from api.
    response = requests.get(url, params=params, headers=headers).json()['passages']

    return response[0] if response else 'passage not found.'


# connect this cog to bot.
def setup(bot):
    bot.add_cog(ESV(bot))
