import discord
import os
import re
from discord.ext import commands
from cogs.bot import bot, send_embed, to_member, send_courses_reaction_message, tutoring_sessions, tutoring_accounts, \
    give_admin_permissions, private_rooms
from my_classes.Course import Course
from my_classes.Student import Student


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
            return await display_tutoring_hours(ctx, tutoring_sessions.get(arg2))

        if arg.lower() == 'join':
            return await add_student_to_queue(ctx, tutoring_sessions, tutoring_accounts)

        if arg.lower() == 'leave':
            return await remove_student_from_queue(ctx, tutoring_sessions, tutoring_accounts)

        if arg.lower() == 'que':
            return await get_queue(ctx, tutoring_sessions, tutoring_accounts)

        if arg.lower() == 'room':
            return await generate_private_voice_channel(ctx, [arg2, arg3, arg4, arg5, arg6])

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

    await course.hours()


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

    # verify if student sign-in.
    verify = await send_is_verified(ctx, student)

    # display error message.
    if verify is False:
        embed = discord.Embed(description=f'<@!{student.discord_id}> *need to sign-in.*')
        return await send_embed(ctx, embed)

    # add student to the queue.
    course = sessions[student.course_code[-3:]]
    course.add(student)

    # display updated queue.
    await display_queue(ctx, course)


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

    # verify if student sign-in.
    verify = await send_is_verified(ctx, student)

    # display error message.
    if verify is True:
        embed = discord.Embed(description=f'*you are already signed-in.*')
        return await send_embed(user=student.discord_id, embed=embed)

    # send student their custom sign-in link.
    embed = get_accounts_embed(f'your sign-in sheet [click here]({await student.sign_in()}).')
    await send_embed(ctx, embed)


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
        embed = get_help_tutee_embed()
        return await send_embed(ctx, embed)

    # display progress message.
    embed = discord.Embed(description='*verifying sign-in.*')
    message = await send_embed(ctx, embed)

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
    student = accounts.get(ctx.author.id)

    # validate if student has set up a bot tutoring bot account.
    if student is None:
        embed = get_help_tutee_embed()
        return await send_embed(ctx, embed)

    # remove student from queue.
    course = sessions[student.course_code[-3:]]
    course.remove(student)

    # display updated queue.
    await display_queue(ctx, course)


async def display_queue(ctx, course, direct_msg=False, announcement=True):
    """display the current queue.

    DISCORD CHANNEL NEEDED: a bot announcement channel.
        bot will display an updated queue:
            everytime the queue has been modify.
        to keep the queue updated the bot will remove the queue message.
    the bot will display a 'user has not sign-in' error message.
        if the current student being helped ( queue[0] ) did not submit their sign-in form.
    a 'queue is empty' error message will be displayed:
        if there are no students in the queue.
    (optional) bot will send a direct message to each student their current position in the queue.

   Parameters
    ----------
    :param Context ctx: the current Context.
    :param Course course: the course queue's object to display.
    :param boolean direct_msg: if True direct message each student their position in the queue,
                               otherwise do nothing.
   :param boolean announcement: if True queue should be printed in the bot announcement channel,
                                otherwise do nothing.
    """
    embed = course.queue_embed()

    # display queue.
    for index, student in enumerate(course.queue, start=1):
        mention_student = f'<@!{student.discord_id}>'
        embed.description += f'#{index} {mention_student} - {student.times_helped}\n'

        # send student their position in queue.
        if direct_msg:
            await send_position_in_queue(student.discord_id, course, index)

    # display error message.
    if len(course.queue) == 0:
        embed.description = '*queue is empty.*'

    if announcement:
        # remove old queue message made by bot.
        if course.message is not None:
            await course.message.delete()

        # display updated queue in bot announcement channel.
        course.message = await send_embed(embed=embed, channel=int(os.getenv("BOT_ANNOUNCEMENT_CHANNEL_ID")))

    await send_embed(ctx, embed)


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
        embed = get_help_tutee_embed()
        return await send_embed(ctx, embed)

    # get queue.
    course = sessions[student.course_code[-3:]]
    await display_queue(ctx, course, announcement=False)


async def send_position_in_queue(discord_id, course, position):
    """DM given student their current position in the queue.
        since student in position 1 is with the tutor
            a position update is not needed.
        students in position 2 will have a custom message.
            while the other positions will get the default message.

    Parameters
    ----------
    :param int discord_id: the student's discord id.
    :param Course course: the course object.
    :param int position: the student's position in the queue.
    """
    if position == 1:
        return

    embed = course.queue_embed(f'#{position} in the queue')

    if position == 2:
        embed.description = 'you are next!'  # custom message.

    await send_embed(user=discord_id, embed=embed)


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
    display 'room already created' error message if the author tries to created more than one room.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param List other_members: a list of members that were mentioned.
    """
    server = bot.get_guild(int(os.getenv("GUILD_SERVER_ID")))
    member = server.get_member(ctx.author.id)

    # display 'room already generated' error message.
    if member.id in private_rooms.values():
        embed = discord.Embed(description='*you already generated a room.*')
        return await send_embed(ctx, embed)

    private_room_category = list(filter(lambda x: x.id == int(os.getenv("PRIVATE_ROOM_CATEGORY_ID")), server.categories))[
        0]
    created_room = await private_room_category.create_voice_channel(f'Private Room: {member}')
    await created_room.set_permissions(server.default_role, manage_permissions=False, connect=False, view_channel=False,
                                       stream=True, move_members=False)
    invite = await created_room.create_invite()
    other_members.append(member.id)
    for member in other_members:
        member = re.sub(r'\D', '', str(member))
        if member:
            try:
                member = server.get_member(int(member))
                await give_admin_permissions(member, created_room)

                # send other mentioned users a DM link to the private room.
                if member != member and member != bot.user:
                    embed = discord.Embed(description=f'<@!{member.id}> has created a private room and invited you')
                    await send_embed(embed=embed, user=member.id)
                    await bot.get_user(member.id).send(invite)
            except discord.errors.InvalidArgument:
                print(f'passed invalid member id: {member}')

    # author is not in voice channel.
    if member.voice is None:
        # direct message author an invite link.
        await ctx.author.send(f'Here is a link to your private room:\n {invite}')
    else:
        await member.move_to(created_room)

    # add author's room to a dictionary.
    private_rooms[created_room.id] = member.id


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
