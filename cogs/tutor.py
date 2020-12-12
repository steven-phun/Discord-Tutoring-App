import discord
import os
from discord.ext import commands
from cogs.bot import bot, send_embed, to_member, send_courses_reaction_message, tutoring_sessions, display_queue
from my_classes.Worker import Worker


class Tutor(commands.Cog):
    def __init__(self, client):
        self.tutor_accounts = {}  # a dictionary of tutor objects. { key=discord_id: value=tutor_object }

    @commands.command()
    async def tutor(self, ctx, arg=None, arg2=None, arg3=None):
        """listens for the tutor commands.

        Parameters
        -----------
        :param Context ctx: the current Context.
        :param str arg: the first argument.
        :param str arg2: the second argument.
        :param str arg3: the third argument.
        """
        if await is_tutor(ctx) is False:
            return

        if arg.lower() == 'start':
            return await start_tutoring_session(ctx, arg2, self.tutor_accounts)


async def start_tutoring_session(ctx, course_num, tutor_accounts):
    """prompt the students that the tutor is ready to tutor.

    a message will be sent to the 'bot announcement channel':
        the message will ping the role that represents student in the tutoring session:
            the tutor's name, tutoring session has started message, and the tutoring session hour.
        WARNING:
            role mention will be sent as a normal message because embed message does not ping role mentions.

    Parameters
    ----------
    :param Context ctx: the current context.
    :param str course_num: represents the course number.
    :param dict tutor_accounts: the dictionary that stores every tutor objects.
    """
    # get object that represents the course.
    course = tutoring_sessions.get(course_num)

    # set tutor's session.
    if course is None:
        course = await set_session(ctx, course_num, tutor_accounts)
        # if tutor does not select an available course code.
        if course is None:
            return

    # get tutor object.
    tutor = tutor_accounts[ctx.author.id]

    # print tutoring session has started message.
    guild = bot.get_guild(int(os.getenv("GUILD_SERVER_ID")))
    role = discord.utils.get(guild.roles, name=course.code)
    embed = discord.Embed(title=f'{tutor.hours()}', description=f'{tutor.mention()}\'s tutoring session has started!')
    channel_id = int(os.getenv("BOT_ANNOUNCEMENT_CHANNEL_ID"))
    await send_embed(channel=channel_id, embed=embed)

    # ping users in class course tutoring has started.
    await bot.get_channel(channel_id).send(role.mention)

    # print confirmation for tutor.
    embed = discord.Embed(title=f'Tutor Accounts', description=f'tutees of {course.code} thank you for tutoring!')
    await send_embed(ctx, embed)


async def set_session(ctx, course_num, tutor_accounts):
    """set the given tutoring session for tutor.

    this function is to allow tutors to not have to type the course after each tutor command.
    this function limits the tutor in setting one tutoring course code at a time.
        if a tutor needs to switch the tutoring course code they can call this function again.
    """
    code = await send_courses_reaction_message(ctx, course_num)
    course = tutoring_sessions.get(code[-3:])

    # add tutor object to tutor object dictionary.
    if course is not None:
        tutor = Worker(ctx.author.id, course)
        tutor_accounts[tutor.discord_id] = tutor

    return course


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
        embed = discord.Embed(description='*students are still responding.*')
        return await send_embed(ctx, embed)

    # display 'queue is empty' error message.
    if tutor.course.que_is_empty():
        embed = discord.Embed(description='*there are no students to tutor!*')
        return await send_embed(ctx, embed)

    # get the next student in queue.
    embed = discord.Embed(description='*waiting for the next student to respond.*')
    await send_embed(ctx, embed)
    await tutor.course.next()

    # display updated queue.
    await display_queue(ctx, tutor.course)


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
    embed = discord.Embed(description='*tutor\'s permission not found.*')
    await send_embed(ctx, embed)
    return False


# connect this cog to bot.
def setup(client):
    client.add_cog(Tutor(client))
