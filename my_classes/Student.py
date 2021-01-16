import os
from datetime import date
from cryptography.fernet import Fernet
from my_classes.Context import Context
from my_classes.GoogleSheet import get_google_sheet
from my_classes.Schedule import Schedule


class Student:
    def __init__(self, ctx, first_name: str, last_name: str, student_id: str, program_degree: str, discord_id: int):
        self.ctx = Context(ctx)  # the object that represents this member's Content.

        self.first = first_name  # the student's first name.
        self.last = last_name  # the student's last name
        self.student_id = student_id  # the student's student id.
        self.course = None  # the course object that the student is in tutoring for.
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
        information = f'{self.first} {self.last} {self.student_id} {self.program_degree} {self.discord_id}'
        fernet = Fernet(os.getenv("FERNET_KEY"))
        encrypted_account = fernet.encrypt(information.encode('utf-8'))

        return encrypted_account.decode('utf-8')

    async def sign_in(self, first_name):
        """send the student their custom sign-in sheet link.

        REQUIREMENT: google form.
            the google form requires: course code, tutor's name, student name, student id, and degree program.
        WARNING: https links spaces are represented with '+'
            this will be used when adding a space between student's first and last name.
        override default tutor's name:
        if student passed in a tutor's name as an argument.

        Parameters
        ----------
        :param str first_name: the str that represents the tutor's first name.
        :return: a str that represents the student's custom sign-in link.
        """

        if first_name is None:
            # get tutor's name from schedule.
            schedule = self.course.schedule
            tutor = schedule.tutor_name()
            if tutor is not None:
                tutor = tutor.replace(' ', '+')
        else:
            # default tutor's name
            tutor = first_name.lower().capitalize()

        # generate custom sign-in link.
        return f'https://docs.google.com/forms/d/e/1FAIpQLSeLjQ8XunqxtzlWGHKB5Kt52-ZAyBqPiyBmLPfNcDuYhb5dsg/viewform?usp=pp_url&entry.1178312123={self.course.code}&entry.1604735080={tutor}&entry.174697377={self.first}+{self.last}&entry.1854395744={self.student_id}+&entry.905892592={self.program_degree}'

    def verify(self):
        """verify student if they submitted their sign-in sheet via google forms.

        the bot will give the students a link to sign-in, but the student is still required to submit the form.
            this function will verify if the student submitted the form.

        :return: True if the student has submitted their sign-in sheet, otherwise False.
        """
        # verify student's sign-in.
        for content in get_google_sheet():
            # only check entries that were submitted today.
            if content['Timestamp'].split(' ')[0] != date.today().strftime('%m-%d-%Y'):
                return False
            # check if student signed-in.
            schedule = Schedule(self.course.code)
            if content['Student Name'] == self.name() and \
                    str(content['Student ID']) == self.student_id and \
                    content['Course Code'] == self.course.code and \
                    content['Degree'] == self.program_degree and \
                    content['Tutor'] == schedule.tutor_name():

                return True

    def name(self):
        """:return: str of the student's first and last name."""
        return f'{self.first} {self.last}'


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
    return Student(None, info[0], info[1], info[2], info[3], int(info[4]))
