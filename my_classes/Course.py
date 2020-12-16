import discord
import json
from datetime import datetime


class Course:
    def __init__(self, code: str = None):
        self.code = code  # represents the course code.
        self.message = None  # stores the message sent in the bot announcement channel.
        self.queue = []  # array of student objects that represents the tutoring queue.
        self.size = 0  # the number of students in the queue.

    def hours(self):
        """get the location, tutoring hours (12 hours format), and tutor's name for given course.

        converts tutoring hours from a .json file to a str to be printed.
        tutoring hours are stored in a local .json file
            in a 24 hour time format.
            for others to modify the hours without touching the code.

        Parameters
        ----------
        :return: a str representation of the tutoring hours of a given course.
        """
        with open(f'json_files/tutoring_hours/{self.code}.json', encoding="utf8") as file:
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

    def update_que(self):
        """determine if the first student has been helped or need help.

        if the first student in the queue is being helped:
            then, move the student to the end of queue.
            otherwise, mark the student as being helped.
        """
        # move currently helped student to the end of the queue.
        if self.queue[0].being_helped:
            student = self.move(0, self.size)
            student.times_helped += 1

    def move(self, position_1, position_2):
        """move the student in the first position to the second position in the queue.

        Parameters
        ----------
        :param int position_1: the number position in the queue.
        :param int position_2: the number position in the queue.
        """
        # move student to their new position.
        try:
            student = self.queue.pop(position_1)
            student.being_helped = False
            self.queue.insert(position_2, student)
            return student
        except IndexError:
            return False

    def swap(self, position_1, position_2):
        """swap the student in the first position with the student in the second.

        Parameters
        ----------
        :param int position_1: the number position in the queue.
        :param int position_2: the number position in the queue.
        """
        # move student to their new position.
        try:
            self.queue[position_1], self.queue[position_2] = self.queue[position_2], self.queue[position_1]
        except IndexError:
            return False

    def kick(self, position):
        """remove the student at the given position in queue.

        Parameters
        ----------
        :param int position: the number position in the queue.
        """
        try:
            del self.queue[position]
            self.size -= 1
        except IndexError:
            return False

    def clear(self):
        """remove every student in queue."""
        self.queue.clear()
        self.size = 0

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

        # increment size.
        self.size += 1

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
            self.size -= 1
            return self.queue.remove(student)

        # display error message.
        except ValueError:
            return None

    def queue_title(self):
        """:return: a str that represents the default embed title for this command."""
        return f'📋 {self.code} Queue'

    def hours_title(self):
        """:return: a str that represents the default embed title for this command."""
        return f'🕘 {self.code} Tutoring Hours'

    def num(self):
        """convert the course code to just the course number.

        example:
            EGR222 -> 222
            CSC312 -> 312

        :return: a str that represents the course number.
        """
        return self.code[-3:]

    def que_is_empty(self):
        """checks if the queue is empty

        :return: True if the queue's length <= 0, otherwise return False.
        """
        return self.size <= 0
