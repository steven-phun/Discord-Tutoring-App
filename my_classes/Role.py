import discord
import os
from my_classes.Reaction import Reaction


class Role:
    """
    ACTION NEEDED:
        developers will need to create a message that is designed for editing a student's role.
        developers should label which emoji is for which course code for the students.
            example:
                :emoji_1: EGR222 - Software Engineering
                :emoji_2: EGR227 - Data Structure
                :emoji_3: CSC312 - Algorithm
                :emoji_4: EGR329 - Computer Architecture
    """
    def __init__(self, bot):
        self.bot = bot  # the discord bot that will be using this class
        self.emojis = Reaction().emojis  # a dictionary of available course codes and it corresponding emojis.
        self.channel = int(os.getenv("ROLE_REACTION_CHANNEL_ID"))  # the discord role reaction channel id.
        self.message = int(os.getenv("ROLE_REACTION_MESSAGE_ID"))  # the discord role message id.

    async def add(self):
        """add reactions to the role assigning message."""
        message = await self.bot.get_channel(self.channel).fetch_message(self.message)
        for emoji in self.emojis:
            await message.add_reaction(emoji)

    async def edit(self, payload, add=False, remove=False, delete=False):
        """edit a discord role from user according to the action of a reaction.

        add the corresponding role if user adds a reaction to the role reaction message.
        remove the corresponding role if user removes a reaction from the role reaction message.
        delete any reactions to the role reaction message that does not corresponding to a course code.
            custom emojis cannot be removed.

        Parameters
        ----------
        :param discord.raw_models. payload: the raw event payload data.
        :param bool add: True, if bot is adding a role to the user.
        :param bool remove: True, if the bot is removing a role from the user.
        :param bool delete: True, if any non role assigning reactions will be deleted.
        """
        if (add and remove) or (not add and not remove):
            return

        # get reaction message and roles.
        message_id = payload.message_id
        if message_id == self.message:
            guild_id = payload.guild_id
            guild = discord.utils.find(lambda guild: guild.id == guild_id, self.bot.guilds)

            role = None
            for emoji in self.emojis:
                if payload.emoji.name == emoji:
                    role = discord.utils.get(guild.roles, name=self.emojis.get(emoji))

            if role is not None:
                member = discord.utils.find(lambda member: member.id == payload.user_id, guild.members)

                # edit student's role.
                if member is not None:
                    if add:
                        await member.add_roles(role)
                    if remove:
                        await member.remove_roles(role)

            # delete non course code reactions.
            if delete:
                if payload.emoji.name not in self.emojis:
                    message = await self.bot.get_channel(payload.channel_id).fetch_message(self.message)
                    emoji = payload.emoji.name
                    user = self.bot.get_user(payload.user_id)

                    await message.remove_reaction(emoji, user)
