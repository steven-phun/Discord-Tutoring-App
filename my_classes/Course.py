import discord
import json
from datetime import datetime


class Course:
    def __init__(self, code: str = None):
        self.code = code  # represents the course code.
        self.queue = []  # array of student objects that represents the tutoring queue.
        self.message = None  # stores the message sent in the bot announcement channel.

    async def hours(self):
        """get the location, tutoring hours (12 hours format), and tutor's name for given course.

        converts tutoring hours from a .json file to a str to be printed.
        tutoring hours are stored in a local .json file
            in a 24 hour time format.
            for others to modify the hours without touching the code.

        Parameters
        ----------
        :return: a str representation of the tutoring hours of a given course.
        """
        with open(f'json_files/tutoring_hours/{self.code}.json') as file:
            hours = json.load(file)

        # store schedule in a string.
        schedule = ''
        for day in hours:
            schedule += f'\n__**{day}**__\n'

            # get tutor's schedule.
            for tutor in hours[day]:
                # get fields from dictionary.
                location = hours[day][tutor]['location']
                start_hour = hours[day][tutor]['start_hour']
                start_minute = hours[day][tutor]['start_minute']
                end_hour = hours[day][tutor]['end_hour']
                end_minute = hours[day][tutor]['end_minute']

                # convert fields to time object.
                start_time = datetime.now().replace(hour=start_hour, minute=start_minute)
                end_time = datetime.now().replace(hour=end_hour, minute=end_minute)

                # add tutor's time, location, and tutor's name time to array.
                tutor_start_time = f'{start_time.strftime("%I:%M%p").lstrip("0").lower()}'
                tutor_end_time = f'{end_time.strftime("%I:%M%p").lstrip("0").lower()}'
                schedule += f'**{tutor_start_time} - {tutor_end_time}** [{location}] - *{tutor}*\n'

        return schedule

    def append(self, student):
        """appends given student to the tutoring queue.

        student will not be added if:
            they are already in the queue.

        Parameters
        ----------
        :param Student student: the student object being added to the queue.
        """
        # do nothing if student is already in queue.
        for tutee in self.queue:
            if student.discord_id == tutee.discord_id:
                return

        # add student in queue.
        self.queue.append(student)

    def remove(self, student):
        """remove given student from the tutoring queue.

        display a 'not in queue' error message:
            if the student is currently not in their respective queue.

        Parameters
        ----------
        :param Student student: the student object in queue to removed.
        """
        # remove student from queue.
        try:
            self.queue.remove(student)
        # display error message.
        except ValueError:
            pass

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

    def num(self):
        """convert the course code to just the course number.

        example:
            EGR222 -> 222
            CSC312 -> 312

        :return: a str that represents the course number.
        """
        return self.code[-3:]
