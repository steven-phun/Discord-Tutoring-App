import os
import gspread
from datetime import date, datetime
from cryptography.fernet import Fernet
from my_classes.Context import Context


class Student:
    def __init__(self, ctx, first_name: str, last_name: str, student_id: str, course_code: str, program_degree: str, discord_id: int):
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

    async def sign_in(self):
        """send the student their custom sign-in sheet link.

        REQUIREMENT: google form.
            the google form requires: course code, tutor's name, student name, student id, and degree program.
        WARNING: https links spaces are represented with '+'
            this will be used when adding a space between student's first and last name.

        :return: a str that represents the student's custom sign-in link.
        """
        # generate custom sign-in link.
        return f'https://docs.google.com/forms/d/e/1FAIpQLSeLjQ8XunqxtzlWGHKB5Kt52-ZAyBqPiyBmLPfNcDuYhb5dsg/viewform?usp=pp_url&entry.79479348={date.today()}&entry.1178312123={self.course_code}&entry.1604735080={None}1&entry.174697377={self.first}+{self.last}&entry.1854395744={self.student_id}&entry.905892592={self.program_degree}'

    def verify(self):
        """verify student if they submitted their sign-in sheet via google forms.

        BOT AUTHENTICATION AND AUTHORIZATION NEEDED:
            for gspread api: https://gspread.readthedocs.io/en/latest/
        API DOCUMENTATIONS AND RESTRICTIONS LIMITS:
            restrictions:
                Sheets API v4 introduced Usage Limits as of this writing:
                    500 requests per 100 seconds per project,
                    100 requests per 100 seconds per user.
                API will display an APIError 429 RESOURCE_EXHAUSTED:
        ACTION NEEDED:
            google form appends new data to the end of the sheet rather than inserting it at the top of the sheet.
                to reduce the time complexity, new data should be searched first.
            add a new sheet and insert the formula in the A1 cell.
                =SORT('Form responses 1'!A1:R,1,false)
                'Form responses 1' is the sheet's name that contains the sign-in information.
        the bot will give the students a link to sign-in, but the student is still required to submit the form.
            this function will verify if the student submitted the form.
        WARNING: google sheet api takes 3-5 seconds to open.
            to improve user's experience place this function where the user would feel the least amount of delay.
            it is NOT recommend to look up and modify the sheet directly because the delay will be noticeable.
                instead store the sheet's content in a data structure
                    then perform the look ups and modification on the data structure.

        :return: True if the student has submitted their sign-in sheet, otherwise False.
        """
        # get authentication and authorization from google sheet credentials file.
        credentials = gspread.service_account(filename='credentials/google_sheet.json')

        # get sign-in sheet.
        sheet = credentials.open_by_key(os.getenv("GOOGLE_SHEET_KEY")).get_worksheet(1)

        # store content in dictionary.
        content = sheet.get_all_records()

        # verify student's sign-in.
        for data in content:
            # only check entries that were submitted today.
            if data['Timestamp'].split(' ')[0] != date.strftime(date.today(), '%m/%d/%Y'):
                return False
            # check if student signed-in.
            if data['Student Name'] == self.name() and \
                    str(data['Student ID']) == self.student_id and \
                    data['Course Code'] == self.course_code and \
                    data['Degree'] == self.program_degree:
                return True

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
