import os
import json
from datetime import date, datetime
from cryptography.fernet import Fernet
from my_classes.Context import Context
from my_classes.GoogleSheet import get_google_sheet


class Student:
    def __init__(self, ctx, first_name: str, last_name: str, student_id: str, course_code: str, program_degree: str,
                 discord_id: int):
        self.ctx = Context(ctx)  # the object that represents this member's Content.

        self.first = first_name  # the student's first name.
        self.last = last_name  # the student's last name
        self.student_id = student_id  # the student's student id.
        self.course_code = course_code  # the course code that the student is in tutoring for.
        self.program_degree = program_degree  # the degree the student is current pursuing.
        self.discord_id = discord_id  # the student's discord id.

        self.times_helped = 0  # the number of times the student has been helped by the tutor.
        self.prev_voice_channel = None  # the voice channel id the student is in prior to joining the tutor's.
        self.being_helped = False  # if the student is currently being helped by a tutor.

    def encrypt(self):
        """encrypt and display student's information.

        encryption is done by using a Fernet Key:
            API here: https://cryptography.io/en/latest/index.html
        encryption converts str to bytes.
            need to strip bytes' format to be printed.
        student's account is NOT stored locally for in a database for transparency.
            student's account are stored in a discord channel to be read by the bot in the future.
        """
        # encrypt student information
        information = f'{self.first} {self.last} {self.student_id} {self.course_code} {self.program_degree} {self.discord_id}'
        fernet = Fernet(os.getenv("FERNET_KEY"))
        encrypted_account = fernet.encrypt(information.encode('utf-8'))

        return encrypted_account.decode('utf-8')

    async def sign_in(self, tutor_name):
        """send the student their custom sign-in sheet link.

        REQUIREMENT: google form.
            the google form requires: course code, tutor's name, student name, student id, and degree program.
        WARNING: https links spaces are represented with '+'
            this will be used when adding a space between student's first and last name.
        override default tutor's name:
        if student passed in a tutor's name as an argument.

        :return: a str that represents the student's custom sign-in link.
        """
        # default tutor's name
        if tutor_name is None:
            tutor = self.tutor_name()
        else:
            tutor = tutor_name.lower().capitalize()

        # generate custom sign-in link.
        return f'https://docs.google.com/forms/d/e/1FAIpQLSeLjQ8XunqxtzlWGHKB5Kt52-ZAyBqPiyBmLPfNcDuYhb5dsg/viewform?usp=pp_url&entry.1178312123={self.course_code}&entry.1604735080={tutor}&entry.174697377={self.first}+{self.last}&entry.1854395744={self.student_id}+&entry.905892592={self.program_degree}'

    def verify(self):
        """verify student if they submitted their sign-in sheet via google forms.

        the bot will give the students a link to sign-in, but the student is still required to submit the form.
            this function will verify if the student submitted the form.

        :return: True if the student has submitted their sign-in sheet, otherwise False.
        """
        # verify student's sign-in.
        for content in get_google_sheet():
            # only check entries that were submitted today.
            if content['Timestamp'].split(' ')[0] != date.strftime(date.today(), '%m/%d/%Y'):
                return False
            # check if student signed-in.
            if content['Student Name'] == self.name() and \
                    str(content['Student ID']) == self.student_id and \
                    content['Course Code'] == self.course_code and \
                    content['Degree'] == self.program_degree:
                return True

    def tutor_name(self):
        """get the name of the tutor that is tutoring the student's respective course.

        tutor's name is obtained by looking at the tutoring hours
            and seeing which tutor's timeslot fall between the current time this command was called.
        if no tutor's name is found, then get the next tutor that will be tutoring.
            this feature is for students that sign in early.
        the tutoring hours are stored in a local .json file in a 24-hour format.
        """
        # get tutoring schedule from a local .json file.
        with open(f'json_files/tutoring_hours/{self.course_code}.json') as file:
            schedule = json.load(file)

        # look up today's day of the week in schedule.
        today_schedule = schedule[datetime.now().strftime('%A')]

        # get tutor's name.
        tutor_name = None
        for tutor in today_schedule:
            # get fields from dictionary.
            start_hour = today_schedule[tutor]['start_hour']
            start_minute = today_schedule[tutor]['start_minute']
            end_hour = today_schedule[tutor]['end_hour']
            end_minute = today_schedule[tutor]['end_minute']
            # convert fields to time object.
            start_time = datetime.now().replace(hour=start_hour, minute=start_minute)
            end_time = datetime.now().replace(hour=end_hour, minute=end_minute)

            # get tutor's name.
            if start_time < datetime.now() < end_time:
                return tutor

            # predict tutor's name.
            if datetime.now() < start_time:
                tutor_name = tutor

        return tutor_name

    def name(self):
        """:return: str of the student's first and last name."""
        return f'{self.first} {self.last}'

    def course_num(self):
        """:return: a str that presents the course number."""
        return self.course_code[-3:]


def to_student(student_info):
    """convert an encrypted student information to a Student object.

    the student information is given as a decrypted str.

    Parameters
    ----------
    :param str student_info: the str that represents the student's information.
    :return: a Student object that represents the given student's information.
    """
    # decrypt student information.
    fernet = Fernet(os.getenv("FERNET_KEY"))
    decrypt_info = fernet.decrypt(student_info.encode('utf-8'))

    # parse string for Student object.
    info = decrypt_info.decode('utf-8').split(' ')

    # generate Student object.
    return Student(None, info[0], info[1], info[2], info[3], info[4], int(info[5]))
