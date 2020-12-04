import discord
import os
from discord.ext import commands
from cogs.bot import send_embed, to_member, send_courses_reaction_message, tutoring_sessions, tutoring_accounts
from my_classes.Course import Course
from my_classes.Student import Student
from my_classes.Reaction import Reaction


class Tutee(commands.Cog):

    @commands.command()
    async def tutee(self, ctx, arg=None, arg2=None, arg3=None, arg4=None, arg5=None, arg6='Trad'):
        """listens for the tutee commands.

        Parameters
        -----------
        :param Context ctx: the current Context.
        :param str arg: the first argument.
        :param str arg2: the second argument.
        :param str arg3: the third argument.
        :param str arg4: the fourth argument.
        :param str arg5: the fifth argument.
        :param str arg6: the sixth argument, default 'Trad'
        """
        if arg is None:
            return

        if arg.lower() == 'hi':
            return await sign_in(ctx, tutoring_accounts)

        if arg.lower() == 'hours':
            return await print_tutoring_hours(ctx, tutoring_sessions.get(arg2))

        if arg.lower() == 'join':
            return await join_queue(ctx, tutoring_sessions, tutoring_accounts)

        if arg.lower() == 'leave':
            return await remove_student_from_queue(ctx, tutoring_sessions, tutoring_accounts)

        if arg.lower() == 'que':
            return await print_current_queue(ctx, tutoring_sessions, tutoring_accounts)

        if arg.lower() == 'set':
            return await setup_account(ctx, tutoring_accounts, arg2, arg3, arg4, arg5, arg6)


async def setup_account(ctx, accounts, first=None, last=None, student_id=None, code=None, degree=None):
    """store the student's information in a dictionary.

    student's information will be encrypted and used for auto filling sign-in sheet.
    a 'missing fields' error message will be displayed:
        if the student did not pass in all necessary fields.
            necessary fields is determined by the google sheet required information.
    a reaction message will display all available classes:
        when student passes in a course code that is not available.
        then update their class section according to the response.
    the command that triggered this function will be deleted:
        when command was made on a public channel for the privacy of the student.
    the student's discord nickname will be updated with the student's full name.
        for other students and tutor to correctly identify the student.

    Parameters
    -----------
    :param Context ctx: the current Context.
    :param str first: the student's first name.
    :param str last: the student's last name.
    :param str student_id: the student's student id.
    :param str code: the course code that the student is in tutoring for.
    :param str degree: the student's program degree.
    :param [] accounts: the array of str that represents the student information.
    """
    # print error message.
    if None in (first, last, student_id, code, degree):
        embed = get_accounts_embed('*missing fields.*')
        return await send_embed(ctx, embed)

    # delete command message.
    if str(ctx.channel.type) == 'text':
        await ctx.message.delete()

    # display reaction message.
    course_code = await send_courses_reaction_message(ctx, code)

    # validate student's course code.
    if course_code is None:
        return

    # generate a student object.
    first_name = first.lower().capitalize()
    last_name = last.lower().capitalize()
    student = Student(first_name, last_name, student_id, course_code, degree, ctx.author.id)

    # add student object to student accounts.
    accounts[ctx.author.id] = student

    # print account successfully added message.
    embed = get_accounts_embed(f'{student.name} has been added!')
    await send_embed(ctx, embed)

    # encrypt and display the account information.
    embed = get_accounts_embed(student.encrypt())
    await send_embed(ctx, embed, channel=int(os.getenv("STUDENT_ACCOUNTS_CHANNEL_ID")))

    # update student's nickname.
    await edit_nickname(ctx, student.name)


async def edit_nickname(ctx, full_name):
    """change the user's discord nickname with their student account's full name.

    DISCORD PERMISSION NEEDED: change nicknames.
    WARNING: bot cannot change the discord guild creator's nickname.

    Parameters
    ----------
    :param Context ctx: the current context.
    :param str full_name: the str the bot will change the student's nickname to.
    """
    embed = discord.Embed()

    # updated user's nickname in the tutoring server.
    try:
        await to_member(ctx.author.id).edit(nick=full_name)
        embed.description = f'nickname updated to {full_name}.'
    except discord.errors.Forbidden:
        embed.description = '*nickname could not be updated.*'

    await send_embed(ctx, embed)


async def print_tutoring_hours(ctx, course):
    """display tutoring hours of a given course.

    display a 'tutoring hours not available':
        when there is no .json file associated for given given course's tutoring hours.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param Course course: the course's tutoring hours to print.
    """
    if course is None:
        return await display_error_msg(ctx)

    await course.hours(ctx)


async def print_current_queue(ctx, sessions, accounts):
    """display the student's current respective queue.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param Optional[Course] sessions: the dictionary that is storing every available tutoring session.
    :param dict accounts: the dictionary that is storing every student accounts.
    """
    student = accounts.get(ctx.author.id)

    # validate if student has set up a bot tutoring bot account.
    if student is None:
        embed = get_help_tutee_embed()
        return await send_embed(ctx, embed)

    # display current queue.
    course = sessions[student.course_code[-3:]]
    await course.print(ctx, announcement=False)


async def join_queue(ctx, sessions, accounts):
    """add student to the given tutor session's queue.

    student are added to the queue only if they submitted their sign-in sheet.
        sign-in sheet is submitted through google form.
    this function automatically puts the student into their respective queue
        therefore, the student needs to have set up a tutoring account with the bot.
    display an 'account not found' error message:
        if student's account is not found in dict.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param Optional[Course] sessions: the dictionary that is storing every available tutoring session.
    :param dict accounts: the dictionary that is storing every student accounts.
    """
    student = accounts.get(ctx.author.id)

    # validate if student has set up a bot tutoring bot account.
    if student is None:
        embed = get_help_tutee_embed()
        return await send_embed(ctx, embed)

    # validate student submitted their sign-in sheet.

    # add student to the queue.
    course = sessions[student.course_code[-3:]]
    await course.add(ctx, student)


async def remove_student_from_queue(ctx, sessions, accounts):
    """removes student from their respective queue.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param Optional[Course] sessions: the dictionary that is storing every available tutoring session.
    :param dict accounts: the dictionary that is storing every student accounts.
    """
    student = accounts.get(ctx.author.id)

    # validate if student has set up a bot tutoring bot account.
    if student is None:
        embed = get_help_tutee_embed()
        return await send_embed(ctx, embed)

    # student's respective course object.
    course = sessions[student.course_code[-3:]]

    # remove student from queue.
    await course.remove(ctx, student)


async def sign_in(ctx, student_accounts):
    """send student their custom sign-in sheet to submit.

    student's custom sign-in sheet link will be sent
        as a direct message because their custom sign-in link may contain sensitive information.
    students will not get their custom sign-ink link:
        if they have not provided their student information prior.
            an 'account not found' error direct message will be sent to the student.
        if they have already sign-in for that tutoring session.
            to avoid a student singing in twice on the same tutoring session.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param dict student_accounts: the dictionary that is storing every student accounts.
    """
    student = student_accounts.get(ctx.author.id)

    # print error message.
    if student is None:
        embed = get_help_tutee_embed()
        return await send_embed(ctx, embed)

    # print error message.
    # if student.verified: embed.description = 'you are already signed-in.'
    # todo implement check if student already sign-in.

    # send student their custom sign-in link.
    embed = get_accounts_embed(f'your sign-in sheet [click here]({await student.sign_in()}).')
    await send_embed(ctx, embed)


async def display_error_msg(ctx):
    """display invalid course code.

    Parameters
    ----------
    :param Context ctx: the current Context.
    """
    embed = discord.Embed(description='*invalid course code.*')
    await send_embed(ctx, embed)


def get_accounts_embed(description=''):
    """stores the default discord.Embed() object for student accounts.

    Parameters
    ----------
    :param str description: the description to initial the embed description with.
    :return: discord.Embed() for student accounts.
    """
    return discord.Embed(title='Student Accounts', description=description)


def get_help_tutee_embed():
    """display a help message for the tutee command."""
    return get_accounts_embed('`.help tutee` - for help to set up an account.')

# connect this cog to bot.
def setup(bot):
    bot.add_cog(Tutee(bot))
