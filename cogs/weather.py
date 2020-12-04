import discord
import os
import requests
from discord.ext import commands
from cogs.bot import send_embed


class Weather(commands.Cog):
    """listens for the weather commands."""

    @commands.command()
    async def weather(self, ctx, city=None, zip_code='', country='US', units='imperial'):
        if city is None:
            return

        # display current weather.
        await display_weather(ctx, city, zip_code, country, units)


async def display_weather(ctx, city, zip_code, country, units):
    """displays the current weather and weather condition of given city.

    for api documentation and parameters:
        https://openweathermap.org/current
    local weather lookup by default is by city name.
        as most users will be more familiar with a city name than its zip code.
    user have the option:
        to including the the zip code after the city name for a less ambiguous lookup.
        to specify a country code to search within that country.
            a few example of country codes:
                US - United states (default)
                GB - Great Britain
                JP - Japan
        to specify the units the temperature will be displayed in.
            imperial - Fahrenheit (default)
            metric   - celsius
            kelvin   - kelvin
    examples of weather conditions are:
        clear sky, few clouds, rain, thunderstorm, snow, mist, etc.
    a 'city not found' error message will be displayed:
        if local weather data for given city name is not found.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param str city: the city name for the local weather.
    :param str zip_code: the zip code for the local weather
    :param str country: the country code for the local weather..
    :param str units: the units the temperature will be displayed.
    """
    embed = discord.Embed(title=':white_sun_rain_cloud: Weather')
    api_key = os.getenv('WEATHER_API_KEY')
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city},{zip_code},{country}&appid={api_key}&units={units}'
    response = requests.get(url).json()

    try:
        temperature = round(response['main']['temp'])
        degrees = get_weather_units(units)
        city_name = response['name']
        country_code = response['sys']['country']
        condition = response['weather'][0]['description']

        embed.description = f'it is {temperature} {degrees} with {condition} in {city_name}, {country_code}'
    except:
        embed.description = f'cannot find city, {city}'

    await send_embed(ctx, embed)


def get_weather_units(units):
    """returns a str representation of units of measurement that corresponds to given system of units.

    if units is 'metric' return °C
    if units is 'kelvin' return K
    by default if units is 'imperial' return °F

    Parameters
    ----------
    :param str units: the system of units.
    :return: a str representation of the units of measurement.
    """
    degree_symbol = '\u00b0'
    if units.lower() == 'metric':
        return f'{degree_symbol}C'
    if units.lower() == 'kelvin':
        return 'K'

    return f'{degree_symbol}F'


# connect this cog to bot.
def setup(bot):
    bot.add_cog(Weather(bot))
