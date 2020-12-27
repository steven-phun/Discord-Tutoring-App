import json
from datetime import datetime


class Schedule:
    def __init__(self, course_code):
        self.course_code = course_code  # the class' course code
        self.schedule = get_schedule(course_code)

    def tutor_name(self):
        """get the tutor's name that is currently tutoring.

        if no tutor's is found tutoring right now, then get the next tutor that will be tutoring.
            this feature is for students that sign in early.

        :return: a str that represents the tutor's name.
        """
        # look up today's day of the week in schedule.
        today = self.schedule[datetime.now().strftime('%A')]

        # get tutor's name.
        tutor_name = None
        for tutor in today:
            # get fields from dictionary.
            start_hour = today[tutor]['start_hour']
            start_minute = today[tutor]['start_minute']
            end_hour = today[tutor]['end_hour']
            end_minute = today[tutor]['end_minute']

            # convert fields to time object.
            start_time = datetime.now().replace(hour=start_hour, minute=start_minute)
            end_time = datetime.now().replace(hour=end_hour, minute=end_minute)

            # get tutor's name.
            if start_time < datetime.now() < end_time:
                return tutor

            # store predicted tutor's name.
            if datetime.now() < start_time:
                tutor_name = tutor

        # return predicted tutor's name.
        return tutor_name

    def tutor_time(self, tutor_name, day=datetime.now().strftime('%A')):
        """get the given tutor's schedule for given day of the week.


        Parameters
        ----------
        :param str tutor_name: the tutor to look up the schedule for.
        :param 'datetime' day: the str that represents the day of the week.
        """
        # get tutor's schedule
        try:
            schedule = self.schedule[day][tutor_name]
        except KeyError:
            return 'N/A N/A'

        # get fields from dictionary.
        start_hour = schedule['start_hour']
        start_minute = schedule['start_minute']
        end_hour = schedule['end_hour']
        end_minute = schedule['end_minute']

        # convert fields to time object.
        start_time = datetime.now().replace(hour=start_hour, minute=start_minute)
        end_time = datetime.now().replace(hour=end_hour, minute=end_minute)

        return f'{to_string(start_time)} {to_string(end_time)}'

    def hours(self):
        """get the location, tutoring hours (12 hours format), and tutor's name for given course.

        converts tutoring hours from a .json file to a str to be printed.
        tutoring hours are stored in a local .json file
            in a 24 hour time format.
            for others to modify the hours without touching the code.

        :return: a str representation of the tutoring hours of a given course.
        """
        # store schedule in a string.
        tutoring_schedule = ''
        for day in self.schedule:
            # do not display weekends.
            if day == 'Saturday' or day == 'Sunday':
                continue

            # get day of the week.
            tutoring_schedule += f'\n__**{day}**__\n'

            # get tutor's schedule.
            for tutor in self.schedule[day]:
                # get fields from dictionary.
                location = self.schedule[day][tutor]['location']
                start_hour = self.schedule[day][tutor]['start_hour']
                start_minute = self.schedule[day][tutor]['start_minute']
                end_hour = self.schedule[day][tutor]['end_hour']
                end_minute = self.schedule[day][tutor]['end_minute']

                # convert fields to time object.
                start_time = datetime.now().replace(hour=start_hour, minute=start_minute)
                end_time = datetime.now().replace(hour=end_hour, minute=end_minute)

                # add tutor's time, location, and tutor's name time to array.
                tutoring_schedule += f'**{to_string(start_time)} - {to_string(end_time)}** [{location}] - *{tutor}*\n'

        return tutoring_schedule


def get_schedule(course_code):
    """convert the tutoring schedule to a dictionary from a local .json file.

    the tutoring schedule in .json is in a 24-hours format.

    Parameters
    ----------
    :param str course_code: the str that represents the class course code.
    :return: python dictionary that represents the tutoring schedule.
    """
    # get tutoring schedule from a local .json file.
    with open(f'json_files/tutoring_hours/{course_code}.json', encoding='UTF8') as file:
        return json.load(file)


def to_string(time):
    """converts a (24 hours format) time object to a (12 hours format) string.

    Parameters
    ----------
    :time: datetime time: the time object to convert.
    :return: a str that represents the time in 12 hours format.
    """
    return time.strftime("%I:%M%p").lstrip("0").lower()
