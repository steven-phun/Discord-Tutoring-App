import discord  # pip3 install -U discord.py
from dotenv import load_dotenv  # pip3 install -U python-dotenv
import os
import random
import json
from discord.ext import commands
from pathlib import Path
from my_classes.Course import Course
from my_classes.Reaction import Reaction
from my_classes.Role import Role

######################
#  GLOBAL FUNCTIONS  #
######################
from my_classes.Student import to_student


async def send_embed(ctx=None, embed=None, user=None, channel=None):
    """send an embed message to a designated channel.

    WARNING: embed messages has a max length of 2048 characters.
        messages that exceeds this limit will be sent through multiple message instead of one.
        long messages cutoff will be the last full word under the max limit.
            to avoid any words breaking on to a new message.
        after the first message the embed title will be removed.
            to make multiple messages seamless and more like one message.
    this function covers sending messages in three forms.
        if user is specified then a direct message will be sent to that user.
        if a channel is specified then message will be sent to that channel.
        by default message will be sent to the channel the bot command was triggered.
    empty messages will not be sent.
    embed title by default will be the bot's name.
    embed color will be randomly generated each time.
        to make each message more distinct.

    Parameters
    ----------
    :param Context ctx: the current Context.
    :param discord.embeds. embed: the embed message.
    :param int user: the user's discord id.
    :param int channel: the discord channel id.
    :return: the discord.Embed sent.
    """
    # set embed title to bot's name by default.
    if len(embed.title) == 0:
        embed.title = os.getenv("BOT_NAME")

    # generate a random hex color code.
    embed.color = random.randint(0, 0xffffff)

    # send multiple messages if needed.
    embed_limit = 2048
    while len(embed.description) > embed_limit:
        long_msg = embed.description

        embed.description = long_msg[:long_msg.rindex(' ', 0, embed_limit)]
        await ctx.channel.send(embed=embed)

        embed.title = None
        embed.description = long_msg.replace(embed.description, '')

    # terminate function if message is empty.
    if len(embed.description) == 0:
        return

    # send an embed message to the designated channel.
    if user is not None:
        return await bot.get_user(user).send(embed=embed)
    if channel is not None:
        return await bot.get_channel(channel).send(embed=embed)
    return await ctx.channel.send(embed=embed)


def json_to_dict(file_path):
    """stores the contents of a .json file to a dictionary object.

    Parameters
    ----------
    :param str file_path: the file path the .json file is located.
    :return: a dictionary of the contents in a .json file.
    """
    # open and read help message from a .json file.
    with open(file_path) as file:
        return json.load(file)


def to_member(discord_id):
    """generate a member object by given discord id.

    :return: a discord.member.Member object
    """
    return bot.get_guild(int(os.getenv("GUILD_SERVER_ID"))).get_member(discord_id)


def mentioned_user(discord_id):
    """converts a discord it into discord's mention syntax.

    Parameters
    ----------
    :param int discord_id: the discord id of user being mentioned.
    :return: a str of how Discord mentions a user with given discord id.
    """
    return f'<@!{discord_id}>'


#####################
#  EVENT FUNCTIONS  #
#####################
async def notify_devs_when_ready():
    """sends a direct message to every user that has the 'developer' role.

    WARNING: the bot will not be able to send a message to a user:
        if the user has 'message from non-friends' disabled.
    the message will notify the developers that the bot is online.
    """
    members = bot.get_all_members()
    for user in members:
        for role in user.roles:
            if role.id == int(os.getenv("DEVELOPERS_ROLE_ID")):
                embed = discord.Embed(description='i am online!')
                try:
                    await send_embed(embed=embed, user=user.id)
                except:  # todo edit bare except.
                    f'{user} has message from non-friends disabled.'


async def bot_greeting_msg(ctx):
    """ displays a greeting message whenever the bot is mentioned in a message.

    the greeting message includes:
        a hello message from the bot and the command to display the help message.

    Parameters
    ----------
    :param Context ctx: the current Context.
    """
    prefix = os.getenv("BOT_PREFIX")
    embed = discord.Embed(description=f'`{prefix}help` to see what i can do.')

    await send_embed(ctx, embed)


async def send_courses_reaction_message(ctx, course_code):
    """display a reaction message of all the available session, then wait and return the student's response.

        a cancel emoji will also be displayed along with the available session.
        the reaction message will have a timeout time before the message is deleted.
        the reaction message will only listen to the attended author.

    Parameters
    ----------
    :param Context ctx: the current context.
    :param str course_code: the course code to validate.
    :return: str that represents a available course code, otherwise return None.
    """
    reaction = Reaction()

    if reaction.validate(course_code) is False:
        embed = discord.Embed(description=reaction.message)

        # display reaction message.
        msg = await send_embed(channel=ctx.channel.id, embed=embed)
        student_choice = await reaction.add(bot, msg, ctx.author.id, 30)

        # validate student's reaction choice.
        if student_choice is None:
            return None

        # update class section.
        for emoji in reaction.emojis:
            if str(student_choice) == emoji:
                return reaction.emojis[emoji]

    return course_code.upper()


async def store_private_voice_channels(member, before, after):
    """stores generated private voice channel in dictionary.

    Parameters
    ----------
    :param Member member: the member whose voice states changed.
    :param VoiceState before: the voice state prior to the changes.
    :param VoiceState after: the voice state after to the changes.
    """
    if after.channel and after.channel in private_rooms.keys():
        await give_admin_permissions(member, after.channel)
    if before.channel and before.channel != after.channel and before.channel.id in private_rooms.keys():
        channel = before.channel
        if not channel.members:
            private_rooms.pop(channel.id)
            await channel.delete()
        else:
            private_rooms[channel.id] = channel.members[0].id


async def get_user_info(ctx):
    """print information about the message to the console for debugging.

    the purpose of this function is to see what commands causes the bot the crash.
    messages made by any bot will be ignored.

    Parameters
    ----------
    :param Context ctx: the current Context.
    """
    if ctx.author.bot:
        return

    information = '\n' \
                  f'user: {ctx.author}   \n' \
                  f'server: {ctx.guild}  \n' \
                  f'ch: {ctx.channel}    \n' \
                  f'msg: {ctx.content}   \n'

    print(information)


def store_last_bot_msg(message):
    """store the last bot message and the user's discord id who triggered the bot command.

    this function is for the undo command
        stored message allows users to delete them in the future.
    this method is placed in this file because it relies on the on_message event.

    Parameters
    ----------
    :param Message message: the current message.
    """
    global msg_history, user_discord_id, channel_id
    if message.author != bot.user:
        user_discord_id = message.author.id
        channel_id = message.channel.id
    if message.author.bot:
        if msg_history.get(user_discord_id) is not None:
            if msg_history[user_discord_id].get(channel_id) is not None:
                msg_history[user_discord_id][channel_id].append(message)
            else:
                msg_history[user_discord_id][channel_id] = [message]
        else:
            msg_history[user_discord_id] = {channel_id: [message]}


async def give_admin_permissions(member, channel):
    """give admin like permission to a given member for a given channel.

    :param discord.Member member: the member object that is being granted the permissions.
    :param discord.Channel channel: the channel object that the permission will be set.
    """
    await channel.set_permissions(member, manage_permissions=True, connect=True,
                                  view_channel=True, stream=True, move_members=True, speak=True)


########################
#  INSTANCE FUNCTIONS  #
########################
def generate_bot_client():
    """generates an instance of a Discord Bot.

    API UPDATE: In version 1.5 of discord.py comes the introduction of Intents.
        This is a radical change in how bots are written.
        An intent basically allows a bot to subscribe into specific buckets of events.

    :return: an instance of a discord bot.
    """
    prefix = os.getenv("BOT_PREFIX")
    intents = discord.Intents(messages=True, guilds=True, members=True, presences=True, reactions=True,
                              voice_states=True)

    return commands.Bot(command_prefix=prefix, help_command=None, intents=intents)


def initialize_sessions():
    """initialize and store every available class course to their tutoring sessions object.

    :return: a dictionary of course number as key and the course object as value.
                example:
                    222 : Course(EGR222)
                    312 : Course(CSC312)
    """
    sessions = {}

    for course_code in Reaction().courses:
        course = Course(course_code)
        sessions[course.num()] = course

    return sessions


async def initialize_accounts(dictionary):
    """read then store each student accounts from a discord channel as an object to given dictionary.

    DISCORD REQUIREMENT:
        read_message_history permission.
    WARNING:
        the discord channel that is storing the student accounts should not allows others to modify or add content to
            because decrypting any text that is not in encrypted format will throw an error.
        DO NOT add this function to @event on_ready
            because the bot cannot read the contents on the message before going online.
    this function is called when the student's account is empty
        to represent the accounts being initialize every time the bot goes online for the first time.
    to not cause an infinite loop
        because this function will be called  when the array storing the student accounts len is 0.
        when the student account is truly empty the bot will append a dummy value increasing the array's length.
            the dummy value will be ignored when initializing the accounts.
    deleting the message that contains the student info
        is the same as removing the student account from a database.
    the messages being read are embed messages.
    a dictionary is used to store the objects:
        key=student's discord id, value=student object

    Parameters
    ----------
    :param dict dictionary: the dictionary to store the student objects.
    """
    # gets student account from designed discord channel.
    channel = bot.get_channel(int(os.getenv("STUDENT_ACCOUNTS_CHANNEL_ID")))
    history = await channel.history(oldest_first=True).flatten()

    # get student accounts.
    for msg in history:
        student = to_student(msg.embeds[0].description)  # todo convert method to class?
        dictionary[student.discord_id] = student  # add student accounts to dictionary.


######################
#  GLOBAL INSTANCES  #
######################
# bot instance.
load_dotenv()  # load the environment variables from a local .env file.
bot = generate_bot_client()  # an instance of the discord bot.

# tutee and tutor fields.
tutoring_sessions = initialize_sessions()  # a dictionary of every available tutoring session.
tutoring_accounts = {}  # a dictionary of student objects.
private_rooms = {}  # a dictionary of generated private voice channel rooms.

# oops commands fields.
msg_history = {}  # keeps track of the Bot's past messages to delete.
user_discord_id = 'discord_id'  # stores the discord id of the last user that triggered a bot command.
channel_id = 'channel'  # stores the discord channel id the bot message was sent.


################
#  BOT EVENTS  #
################
@bot.event
async def on_ready():
    """executes these functions when the client is done preparing the data received from Discord."""
    await initialize_accounts(tutoring_accounts)  # bot needs to be ready before fetching messages.
    await Role(bot).add()
    await notify_devs_when_ready()


@bot.event
async def on_message(message):
    """listens when a Message is created and sent.

    WARNING: on_message by default will prevent other commands from triggering.

    Parameters
    ----------
    :param Message message: the current message.
    """
    # ignore messages made and sent by other bots.
    if message.author.bot and message.author != bot.user:
        return

    # get message information for debugging.
    if message.content.startswith(os.getenv('BOT_PREFIX')):
        await get_user_info(message)

    # display a greeting message when the bot is mentioned.
    if mentioned_user(int(os.getenv("BOT_ID"))) in message.content:
        await bot_greeting_msg(message)

    # store the last bot message.
    store_last_bot_msg(message)

    # this code will override default process commands
    # and allow custom generated commands to trigger.
    await bot.process_commands(message)


@bot.event
async def on_voice_state_update(member, before, after):
    """
    PERMISSION NEEDED: This requires Intents.voice_states to be enabled.

    Parameters
    ----------
    :param Member member: the member whose voice states changed.
    :param VoiceState before: the voice state prior to the changes.
    :param VoiceState after: the voice state after to the changes.
    """
    await store_private_voice_channels(member, before, after)


@bot.event
async def on_raw_reaction_add(payload):
    """called when a message has a reaction added to it.

    Parameters
    ----------
    :param discord.raw_models. payload: the raw event payload data.
    """
    # add roles
    await Role(bot).edit(payload, add=True, delete=True)


@bot.event
async def on_raw_reaction_remove(payload):
    """called when a message has a reaction removed from it.

    Parameters
    ----------
    :param discord.raw_models. payload: the raw event payload data.
    """
    # remove roles
    await Role(bot).edit(payload, remove=True)


# load other commands from other files.py.
directory = 'cogs'
for path in Path(__file__).parent.parent.joinpath(directory).iterdir():
    if path.name.endswith('.py') and 'bot' not in path.name:
        bot.load_extension(f'{directory}.{path.name[:-3]}')
