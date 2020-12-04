import discord
import json
from datetime import datetime


class Course:
    def __init__(self, code: str = None):
        self.code = code  # represents the course code.
        self.num = code[-3:]  # represents the course number.
        self.queue = []  # array of student objects that represents the tutoring queue.
        self.message = None  # stores the message sent in the bot announcement channel.

    async def hours(self):
        """display the location, tutoring hours in a 12 hours format, and tutor's name for given class course.

        converts tutoring hours from a given course code from a .json file to a str to be printed.
        tutoring hours are stored in a local .json file in a 24 hour time format.

        Parameters
        ----------
        :return: a str representation of the tutoring hours of a given course.
        """
        with open(f'json_files/tutoring_hours/{self.code}.json') as file:
            tutoring_hours = json.load(file)

        # store schedule in an array.
        array_schedule = []
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        for day in days_of_week:
            array_schedule.append('')
            array_schedule.append(f'__**{day}**__')

            # get tutor's schedule.
            for tutor in tutoring_hours[day]:
                # get fields from dictionary.
                location = tutoring_hours[day][tutor]['location']
                start_hour = tutoring_hours[day][tutor]['start_hour']
                start_minute = tutoring_hours[day][tutor]['start_minute']
                end_hour = tutoring_hours[day][tutor]['end_hour']
                end_minute = tutoring_hours[day][tutor]['end_minute']

                # convert fields to time object.
                start_time = datetime.now().replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
                end_time = datetime.now().replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)

                # add tutor's time, location, and tutor's name time to array.
                tutor_start_time = f'{start_time.strftime("%I:%M%p").lstrip("0").lower()}'
                tutor_end_time = f'{end_time.strftime("%I:%M%p").lstrip("0").lower()}'
                array_schedule.append(f'**{tutor_start_time} - {tutor_end_time}** [{location}] - *{tutor}*')

        return '\n'.join(array_schedule)

    def queue_embed(self, description=''):
        """generate a default queue embed.

        Parameters
        ----------
        :param str description: the description to initialize the embed description with.
        :return: a discord.Embed.
        """
        return discord.Embed(title=f'📋 {self.code} Queue', description=description)

    def hours_embed(self, description=''):
        """generate a default tutoring hours embed.

        Parameters
        ----------
        :param str description: the description to initialize the embed description with.
        :return: a discord.Embed.
        """
        return discord.Embed(title=f'🕘 {self.code} Tutoring Hours', description=description)