import discord
import os
import re
from discord.ext import commands
from cogs.bot import bot, send_embed, to_member, send_courses_reaction_message, tutoring_sessions, tutoring_accounts, \
    give_admin_permissions, private_rooms, display_queue, is_bot_channel
from my_classes.Course import Course
from my_classes.Student import Student


class Tutee(commands.Cog):

    @commands.command()
    async def tutee(self, ctx, arg=None, arg2=None, arg3=None, arg4=None, arg5=None):
        """listens for the tutee commands.

        Parameters
        -----------
        :param Context ctx: the current Context.
        :param str arg: the first argument.
        :param str arg2: the second argument.
        :param str arg3: the third argument.
        :param str arg4: the fourth argument.
        :param str arg5: the sixth argument, default 'Trad'
        """
        if arg is None:
            return

        # not a command.
        update_students_ctx(ctx)

        # ignore command if command was made outside the designed channel.
        if await is_bot_channel(ctx) is False:
            return

        # send student their custom sign-in link.
        if arg.lower() == 'hi':
            return await sign_in(ctx, arg2, arg3, tutoring_accounts)

        # set up a student's tutoring account.
        if arg.lower() == 'set':
            return await setup_account(ctx, tutoring_accounts, arg2, arg3, arg4, arg5)

        # display the tutoring information for given course code.
        if arg.lower() == 'hours':
            return await display_tutoring_hours(ctx, tutoring_sessions.get(arg2))

        # add the student to their respective queue.
        if arg.lower() == 'join':
            return await add_student_to_queue(ctx, tutoring_sessions, tutoring_accounts)

        # remove the student in their respective queue.
        if arg.lower() == 'leave':
            return await remove_student_from_queue(ctx, tutoring_sessions, tutoring_accounts)

        # display the current queue.
        if arg.lower() == 'que':
            return await get_queue(ctx, tutoring_sessions, tutoring_accounts)

        # generate a private voice channel.
        if arg.lower() == 'room':
            return await generate_private_voice_channel(ctx, [arg2, arg3, arg4, arg5])


async def setup_account(ctx, accounts, first=None, last=None, student_id=None, degree=None):
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
    :param str degree: the student's program degree.
    :param [] accounts: the array of str that represents the student information.
    """
    # print error message.
    if None in (first, last, student_id):
        return await send_embed(ctx, title=get_student_accounts_title(), text='*missing fields.*')

    # delete command message.
    if str(ctx.channel.type) == 'text':
        await ctx.message.delete()

    # generate a student object.
    first_name = first.lower().capitalize()
    last_name = last.lower().capitalize()
    if degree is None:
        degree = 'Trad'
    student = Student(ctx, first_name, last_name, student_id, degree, ctx.author.id)

    # add student object to student accounts.
    accounts[ctx.author.id] = student

    # print account successfully added message.
    await send_embed(ctx, title=get_student_accounts_title(), text=f'{student.name()} has been added!')

    # encrypt and display the account information.
    channel_id = int(os.getenv("STUDENT_ACCOUNTS_CHANNEL_ID"))
    await send_embed(ctx, channel=channel_id, title=get_student_accounts_title(), text=student.encrypt())

    # update student's nickname.
    await edit_nickname(ctx, student.name())


async def edit_nickname(ctx, full_name):
    """change the user's discord nickname with their student account's full name.

    DISCORD PERMISSION NEEDED: change nicknames.
    WARNING: bot cannot change the discord guild creator's nickname.

    Parameters
    ----------
    :param Context ctx: the current context.
    :param str full_name: the str the bot will change the student's nickname to.
    """
    # updated user's nickname in the tutoring server.
    try:
        await to_member(ctx.author.id).edit(nick=full_name)
        description = f'nickname updated to {full_name}.'
    except discord.errors.Forbidden:
        description = '*nickname could not be updated.*'

    await send_embed(ctx, text=description)


async def display_tutoring_hours(ctx, course):
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

    await send_embed(ctx, title=course.hours_title(), text=course.schedule.hours())


async def add_student_to_queue(ctx, sessions, accounts):
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

    # display an error message if student's course is not not assigned.
    if student.course is None:
        return await send_embed(ctx, text=student.course_error_msg())

    # verify if student sign-in.
    verify = await send_is_verified(ctx, student)

    # display error message did not sign in.
    if verify is False:
        return await send_embed(ctx, text=student.course_error_msg())

    # add student to the queue.
    course = sessions[student.course.num()]
    course.append(student)

    # display updated queue.
    await display_queue(ctx, course)


async def sign_in(ctx, course_num, tutor_name, student_accounts):
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
    :param str course_num: the str that represents the course number.
    :param str tutor_name: the str that represents the tutor's first name.
    :param dict student_accounts: the dictionary that is storing every student accounts.
    """
    # if course number does not exists.
    if tutoring_sessions.get(course_num) is None:
        course_code = await send_courses_reaction_message(ctx, course_num)
        course_num = course_code[-3:]

    # validate course number.
    if course_num is None:
        return

    # get the student object.
    student = student_accounts.get(ctx.author.id)

    # set student's course code.
    student.course = tutoring_sessions.get(course_num)

    # verify if student sign-in.
    verify = await send_is_verified(ctx, student)

    # display error message.
    if verify is True:
        return await send_embed(user=student.discord_id, title=get_student_accounts_title(),
                                text=f'*you are already signed-in.*')

    # send student their custom sign-in link.
    await send_embed(user=student.ctx.discord_id(), title=get_student_accounts_title(),
                     text=f'your sign-in sheet [click here]({await student.sign_in(tutor_name)}).')


async def send_is_verified(ctx, student):
    """send a message to prompt the student that the bot is verifying their sign-in.

    WARNING: using google sheet api take 3-5 seconds to load the google sheet.
        because of the delay a progress message will be displayed
            then removed for the students when the bot finished verifying.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param Student student: the student object.
    :return: True, if student sign-in, otherwise False.
    """
    # validate if student has set up a bot tutoring bot account.
    if student is None:
        return await send_embed(ctx, title=get_student_accounts_title(), text=get_help_tutee_description())

    # display progress message.
    message = await send_embed(ctx, text='*verifying sign-in.*')

    # validate student submitted their sign-in sheet.
    verify = student.verify()

    # remove progress message.
    await message.delete()

    return verify


async def remove_student_from_queue(ctx, sessions, accounts):
    """removes student from their respective queue.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param Optional[Course] sessions: the dictionary that is storing every available tutoring session.
    :param dict accounts: the dictionary that is storing every student accounts.
    """
    # get student object.
    student = accounts.get(ctx.author.id)

    # validate if student has set up a bot tutoring bot account.
    if student is None:
        embed = get_help_tutee_description()
        return await send_embed(ctx, embed)

    # display an error message if student did not sign in.
    if student.course is None:
        return await send_embed(ctx, text=student.course_error_msg())

    # remove student from queue.
    course = sessions[student.course.num()]
    course.remove(student)

    # reset student's course.
    student.course = None

    # display updated queue.
    await display_queue(ctx, course)


async def get_queue(ctx, sessions, accounts):
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
        embed = get_help_tutee_description()
        return await send_embed(ctx, embed)

    # display an error message if student did not sign in.
    if student.course is None:
        return await send_embed(ctx, text=student.course_error_msg())

    # get queue.
    course = sessions[student.course.num()]
    await display_queue(ctx, course, announcement=False)


async def generate_private_voice_channel(ctx, other_members):
    """generate a private discord voice channel and send invites to all mentioned members.

    admin permissions will be granted to a member for this room.
        by default the permission will be granted to the user who triggered the command.
        if the user leaves the room:
            then the ownership will be transferred to member that has been in the room the longest.
            if there are no members to transfer, then the bot will remove the room from the server.
    the bot will automatically move the user that triggered this command to newly generated room.
    the bot will send the link as a direct message to join the voice channel:
        if the user that triggered this command is not in a voice channel
            because the bot cannot force members to join a voice channel, it can only move members.
        all other mentioned members.
    to prevent spamming this command:
        the rooms will be saved in a dictionary (key = room-id, value = member's-discord-id).
    display 'room already generated' error message:
        when a member tries to generate a room, but has one in the server already.
    the bot by default will move the member to the newly generated room
        if member is not in a voice channel the bot will send an invite instead.
        bot will send the other members an invite to give them a choice to accept or deny.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param List other_members: a list of members that were mentioned.
    """
    server = bot.get_guild(int(os.getenv("GUILD_SERVER_ID")))
    member = server.get_member(ctx.author.id)

    # display 'room already generated' error message.
    if member.id in private_rooms.values():
        return await send_embed(ctx, text='*you already own a room.*')

    # generate a private voice channel.
    category_id = int(os.getenv("PRIVATE_ROOM_CATEGORY_ID"))
    private_room_category = list(filter(lambda x: x.id == category_id, server.categories))[0]
    private_room_channel = await private_room_category.create_voice_channel(f'Private Room: {member}')
    await set_private_room_permissions(server, private_room_channel)

    # invite to send to members.
    invite = await private_room_channel.create_invite()

    # move/send an invite to the member.
    if member.voice is None:
        await ctx.author.send(f'Here is a link to your private room:\n {invite}')
    else:
        await member.move_to(private_room_channel)

    # send other members an invite.
    other_members.append(member.id)
    for member in other_members:
        member = re.sub(r'\D', '', str(member))
        if member:
            try:
                member = server.get_member(int(member))
                await give_admin_permissions(member, private_room_channel)

                # send other mentioned users a DM link to the private room.
                if member != member and member != bot.user:
                    await send_embed(user=member.id, text=f'<@!{member.id}> has created a private room and invited you')
                    await bot.get_user(member.id).send(invite)
            except discord.errors.InvalidArgument:
                await send_embed(ctx, text=f'{member} *is an invalid member.*')

    # add member's room to a dictionary.
    private_rooms[private_room_channel.id] = member.id


async def set_private_room_permissions(server, channel):
    """set the given channel with private room permissions.

    private room permissions are:
        permission to allow students to freely

    :param discord.Server server: the server object that the channel is in.
    :param discord.Channel channel: the channel object that the permission will be set in.
    :return:
    """
    await channel.set_permissions(server.default_role, manage_permissions=False, connect=False, view_channel=False,
                                  stream=True, move_members=False)


async def display_error_msg(ctx):
    """display invalid course code.

    Parameters
    ----------
    :param Context ctx: the current Context.
    """
    await send_embed(ctx, text='*invalid course code.*')


def update_students_ctx(ctx):
    """update student's Context with the given Context.

    when student object gets initialized, the object Context could not be decrypted,
        therefore, the bot will manually add the student's Context next time the student uses the bot.
    """
    student = tutoring_accounts.get(ctx.author.id)
    if student is None:
        return

    # update student's Context
    student.ctx.ctx = ctx


def get_student_accounts_title():
    """:return: a str that represents the default embed title for this command."""
    return 'Student Accounts'


def get_help_tutee_description():
    """:return: a str that represents the default help message for the tutee command."""
    return '`.help tutee` - for help to set up an account.'


# connect this cog to bot.
def setup(client):
    client.add_cog(Tutee(client))
