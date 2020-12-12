import discord
import os
from discord.ext import commands
from cogs.bot import bot, send_embed, to_member, send_courses_reaction_message, tutoring_sessions, display_queue
from my_classes.Worker import Worker


class Tutor(commands.Cog):
    def __init__(self, client):
        self.tutor_accounts = {}  # a dictionary of tutor objects. { key=discord_id: value=tutor_object }

    @commands.command()
    async def tutor(self, ctx, arg=None, arg2=None):
        """listens for the tutor commands.

        Parameters
        -----------
        :param Context ctx: the current Context.
        :param str arg: the first argument.
        :param str arg2: the second argument.
        """
        # terminate function if user does not have tutor permissions.
        if await is_tutor(ctx) is False:
            return

        if arg.lower() == 'start' or self.tutor_accounts.get(ctx.author.id) is None:
            await announce_session_started(ctx, arg2, self.tutor_accounts)

        if arg.lower() == 'next':
            return await get_next_student(ctx, self.tutor_accounts.get(ctx.author.id))


async def announce_session_started(ctx, course_num, tutor_accounts):
    """prompt the students that the tutor is ready to tutor.

    a message will be sent to the 'bot announcement channel':
        the message will ping the role that represents student in the tutoring session:
            the tutor's name, tutoring session has started message, and the tutoring session hour.
        WARNING:
            role mention will be sent as a normal message because embed message does not ping role mentions.

    Parameters
    ----------
    :param Context ctx: the current context.
    :param str course_num: the course number.
    :param dict tutor_accounts: a dictionary of all tutor accounts.
    """
    # set tutoring session.
    await set_session(ctx, course_num, tutor_accounts)

    # get tutor object.
    tutor = tutor_accounts.get(ctx.author.id)

    # terminate function if tutor objet is not found.
    if tutor is None:
        return

    # print tutoring session has started message.
    guild = bot.get_guild(int(os.getenv("GUILD_SERVER_ID")))
    role = discord.utils.get(guild.roles, name=tutor.course.code)
    channel_id = int(os.getenv("BOT_ANNOUNCEMENT_CHANNEL_ID"))
    await send_embed(channel=channel_id, title=f'{tutor.hours()}',
                     text=f'{tutor.ctx.mention()}\'s tutoring session has started!')

    # ping users in class course tutoring has started.
    await bot.get_channel(channel_id).send(role.mention)

    # print confirmation for tutor.
    await send_embed(ctx, title=f'Tutor Accounts', text=f'tutees of {tutor.course.code} thank you for tutoring!')


async def set_session(ctx, course_num, tutor_accounts):
    """set the given course number for tutor.

    this function is to allow tutors to not have to type the course number after each tutor command.
    this function limits the tutor in setting more than one tutoring course code at a time.
        if a tutor needs to switch the tutoring course code they can call this function again.
    """
    # get object that represents the course.
    course = tutoring_sessions.get(course_num)

    # set tutor's session.
    if course is None:
        code = await send_courses_reaction_message(ctx, course_num)
        course = tutoring_sessions.get(code[-3:])

    # add tutor object to tutor object dictionary.
    if course is not None:
        tutor = Worker(ctx, course)
        tutor_accounts[tutor.ctx.discord_id()] = tutor


async def get_next_student(ctx, tutor):
    """get the next student in tutoring queue that is ready.

    DISCORD PERMISSION NEEDED: move members
    if the student is in the same voice channel when this command is called:
        move current student being helped by a tutor to their previous voice channel prior to joining the tutor's.
            the current student being helped the the first student in the queue.
            if there is no previous voice channel or previous voice channel no longer exists:
                disconnect the student from the voice channel.
    student will be moved to the back of the queue.
    incrementing the number of times they have been helped by 1.
        this feature is to allow tutors to physically see how many times the student have been helped this session.
    move the next student that needs help to the tutor's voice channel.
        if the next student is not in a voice channel:
            send the student an invite to the tutor's voice channel.
    display an updated queue to the bot announcement channel.
    a 'no student in queue' error message will be displayed:
        if there are no students in the current queue.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param 'Worker' tutor: the object that represents a tutor.
    """
    # display 'reaction message is still circulating' error message.
    if tutor.is_circulating():
        return await send_embed(ctx, text='*students are still responding.*')

    # display 'queue is empty' error message.
    if tutor.course.que_is_empty():
        return await send_embed(ctx, text='*there are no students to tutor!*')

    # get the next student in queue.
    message = await send_embed(ctx, text='*waiting for the next student to respond.*')
    tutor.course.next()

    # remove message.
    await message.delete()

    # move next student to tutor's voice channel.
    await pull_next_student(ctx, tutor)

    # display updated queue.
    await display_queue(ctx, tutor.course)


async def pull_next_student(ctx, tutor):
    """move the next student that needs help to the tutor's voice channel.

    DISCORD VOICE PERMISSIONS NEEDED:
        move members.
    WARNING: bot cannot force anyone to join a voice channel.
        display a 'tutor not in voice channel' error message:
            if the tutor is not in a voice channel.
        the bot will send the student an invite link to the tutor's voice channel:
            if the student is not in a voice channel.
    the bot will DM a reaction message to the first student in the queue asking if they need help.
        if the student is not ready or did not respond withing a given amount of time
            the bot will continue to DM the next student
                and repeat until a student is ready of the tutor decides to stop waiting for a response.
    the student that reacted to the 'ready emoji':
        will be move to the top of the queue representing the student is being help by a tutor.
        will be move to the tutor's voice channel.
        display an updated waitlist.
    the tutor will get updates on how each student is responding.
        student got your invite - if the tutor is waiting for the student to accept the VC invite.
        student skipped - if the student reacted with a 'not ready emoji'.
        student did not respond - if the student did not respond with the 'ready or not ready emoji'.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param 'Worker' tutor: the tutor that called this function.
    """
    ready_emoji = '👍🏼'
    not_ready_emoji = '👎🏼'

    # cycle through the queue until a student is ready.
    index = 0
    while True:
        # DM reaction message to student.
        student = tutor.course.queue[index]
        description = f'do you need help?\n\n' \
                      f'{ready_emoji} - ready! connect me to the tutor.\n\n' \
                      f'{not_ready_emoji} - not yet, come back to me.'
        tutor.reaction_msg = await send_embed(user=student.discord_id(), title='Tutor', text=description)
        reaction = await add_reaction_to_message(tutor.reaction_msg, student.discord_id, [ready_emoji, not_ready_emoji], 15)

        # tutor canceled getting the next student.
        if tutor.reaction_msg is None: return

        # student did not respond.
        if reaction is None:
            embed = discord.Embed(description=f'{mention_student} did not respond.')
            await send_embed(ctx, embed)

        if reaction is not None:
            # student is ready.
            if str(reaction) == ready_emoji:
                # reaction message no longer circulating.
                tutor.reaction_msg = None
                student.being_helped = True

                # move student to position 1
                tutee = waitlist[index]
                waitlist.remove(tutee)
                waitlist.insert(0, tutee)

                # tutor not in voice channel.
                if not await is_tutor_in_vc(ctx): return

                # student is not in voice channel.
                if member.voice is None:
                    # DM invite to student.
                    invite = await tutors_voice_channel.create_invite()
                    embed = discord.Embed(title='Tutoring',
                                          description=f'join tutor\'s voice channel')
                    await give_connect_to_voice_channel_permission(member, tutors_voice_channel)
                    await send_embed(embed=embed, user=member.id)
                    await bot.get_user(member.id).send(invite)

                    # print error message.
                    embed = discord.Embed(description=f'waiting for {mention_student} to join your voice channel.')
                    return await send_embed(ctx, embed)

                # store user's voice channel
                # then move student to tutor's voice channel.
                student.prev_voice_channel = member.voice.channel
                await member.move_to(tutor_member.voice.channel)
                return await print_waitlist(ctx, class_section, dm=True, verify=True)

            # student is not ready.
            if str(reaction) == not_ready_emoji:
                embed = discord.Embed(description=f'<@!{student.discord_id}> skipped.')
                await send_embed(ctx, embed)

        # edge cases.
        if len(waitlist) == 0:
            tutor.reaction_msg = None
            return await print_waitlist(ctx, class_section)

        # get next student on the wait list.
        index = (index + 1) % len(waitlist)


async def add_reaction_to_message(message, author, choice_emojis, timeout):
    """add reactions to given message and wait for an intended author to respond to it.

    the bot will check if the reaction came from the intended author
        and if the reaction added was one of the original reaction emoji from the bot.
    the message will be deleted once the bot stops listening for a reaction
         to not confuse users thinking that the bot is still listening.
     the timeout timer will start counting right after message is sent.

    Parameters
    ----------
    :param Context message: the current Context.
    :param int author: the intended author's discord id.
    :param [] choice_emojis: an array of str emoji to add to the message.
    :param int timeout: the number of seconds the intended author have to respond.
    :return: str: the emoji that represents the intended author's reaction.
    """
    # add reactions to the message.
    for emoji in choice_emojis:
        await message.add_reaction(emoji)

    # function to validate author and reaction added.
    def check(reaction, user):
        return user.id == author and str(reaction.emoji) in choice_emojis

    # wait for reaction.
    try:
        reaction, _ = await bot.wait_for('reaction_add', check=check, timeout=timeout)
    except:
        reaction = None

    # try if the message hasn't been removed by the tutor prior to deletion.
    try:
        await message.delete()
    except:
        pass

    return reaction


async def is_tutor(ctx):
    """checks if member has the tutor role.

    a tutor role should be granted to members that has permission to use tutor commands.
    display a 'permission not found' error message:
        if the member does not have tutor permissions.

    Parameters
    -----------
    :param Context ctx: the current Context.
    :return: True if the member has a tutor role tag, False otherwise.
    """
    # check if member has tutor role.
    for role in to_member(ctx.author.id).roles:
        if role.id == int(os.getenv("TUTOR_ROLE_ID")):
            return True

    # display error message.
    await send_embed(ctx, text='*tutor\'s permission not found.*')
    return False


# connect this cog to bot.
def setup(client):
    client.add_cog(Tutor(client))
