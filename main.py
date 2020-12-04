from cogs.bot import bot
import os

#    WARNING: pushing new codes to the hosting server will cause the bot to reset.
#         clearing all stored data like: waitlist, student accounts, message history, etc.
#     WARNING: the hosting server cannot store information permanently because it will reset every 24 hours.
#         to avoid students and tutors typing their information every time the bot resets:
#             information will be encrypted and printed on a text channel.
#                 the bot will read all past message on that channel and initialize the accounts before going live.

# set up bot to connect to Discord.
if __name__ == '__main__':
    bot.run(os.getenv("BOT_TOKEN"))
