import json
import discord.errors
import asyncio.exceptions


class Reaction:
    async def add(self, bot, message, author, timeout):
        """add reactions to a message and wait for an intended author to respond to it.

        the bot will check if the reaction came from the intended author
            and if the reaction added was one of the original reaction emoji from the bot.
        the message will be deleted once the bot stops listening for a reaction
             to not confuse users thinking that the bot is still listening.
         the timeout timer will start counting right after message is sent.

        Parameters
        ----------
        :param bot : the bot that will use this function.
        :param Context message: the current Context.
        :param int author: the intended author's discord id.
        :param int timeout: the number of seconds the intended author have to respond.
        :return: str: the emoji that represents the intended author's reaction.
        """
        # add reactions to the message.
        for emoji in self.course_emojis():
            await message.add_reaction(emoji)

        # function to validate author and reaction added.
        def check(reaction, user):
            return user.id == author and str(reaction.emoji) in self.course_emojis()

        # wait for reaction.
        try:
            reaction, _ = await bot.wait_for('reaction_add', check=check, timeout=timeout)
        # if reaction message times out.
        except asyncio.exceptions.TimeoutError:
            reaction = None

        # delete reaction message.
        try:
            await message.delete()
        # if reaction message is removed prior to deletion.
        except discord.errors.NotFound:
            pass

        return reaction

    def validate(self, course_code):
        """validates if given course code is available for tutoring.

        Parameters
        ----------
        :param str course_code : the course code to validate.
        :return: True if given course code is available for tutoring, otherwise return False.
        """
        return course_code is not None and course_code.upper() in self.course_codes()

    def course_codes(self):
        """stores all available course code and their corresponding emoji in a dictionary.

        :return: a dictionary key=course code, value=corresponding emoji.
        """
        dictionary = {}

        courses = get_course_from_json()
        for course in courses:
            dictionary[course] = courses[course]['emoji']

        return dictionary

    def course_emojis(self):
        """stores the reverse of get_course_codes() where they keys are not the values and the values are not the keys.

        :return: a new dictionary that reverses the keys and values of get_course_codes().
        """
        course_emojis = {}
        for key, value in self.course_codes().items():
            course_emojis[value] = key

        return course_emojis

    def message(self):
        """generate a string all available courses for a student to choose from.

        :return: a str representation for the embed description message.
        """
        string = f'*Section Not Found.*\n\n' \
                 f'did you mean one of these?\n'

        courses = get_course_from_json()
        for course in courses:
            emoji = courses[course]["emoji"]
            description = courses[course]["course"]

            string += f'{emoji} - {course} {description}\n'

        return string


def get_course_from_json():
    """stores the all available course information in a dictionary.

    Parameters
    ----------
    :return: a dictionary of all available courses.
    """
    # open and read help message from a .json file.
    with open('json_files/tutoring_courses/courses.json', encoding="utf8") as file:
        return json.load(file)
