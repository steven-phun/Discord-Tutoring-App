from discord.ext import commands
from cogs.bot import send_embed, json_to_dict


class Chapel(commands.Cog):
    """listens for the chapel schedule commands."""

    @commands.command()
    async def chapel(self, ctx, arg: str = None):
        # print the entire chapel schedule.
        if arg is None:
            return await get_chapel_week(ctx)

        # print the chapel schedule of a specified week.
        if arg.isdigit():
            week_num = arg
            return await get_chapel_week(ctx, week_num)


async def get_chapel_week(ctx, week_num=None):
    """looks up the chapel schedule of a given week.

    chapel schedule is stored in a local .json file
        to allow others to modify the schedule without touching the code.
    a 'no week was found' error message will be displayed:
        when the given week is not found in the file that is storing the chapel schedule..

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param str week_num: the chapel week to print.
    :return: a str representation of the chapel schedule.
    """
    # get chapel schedule.
    contents = json_to_dict('json_files/chapel/chapel_schedule.json')

    schedule = []
    for week in contents:
        if week_num is not None and week != f'Week {week_num}':
            continue

        schedule.append('')
        schedule.append(f'__**{week}**__')

        # get chapel information for each week.
        for date in contents[week]:
            day_of_week = contents[week][date]['day_of_week']
            speaker = contents[week][date]['speaker']

            schedule.append(f'**{date}** [{day_of_week}] - *{speaker}*')

    # print chapel schedule.
    separator = '\n'
    description = separator.join(schedule)

    # print error message.
    if len(description) == 0:
        description = f'*no scheduled chapel for week {week_num}.*'

    await send_embed(ctx, title='⛪ Chapel Schedule', text=description)


# connect this cog to bot.
def setup(bot):
    bot.add_cog(Chapel(bot))
