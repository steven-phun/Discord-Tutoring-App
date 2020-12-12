import os


class Context:
    def __init__(self, ctx):
        self.ctx = ctx

    def discord_id(self):
        """:return: an int that represents the member's discord id"""
        return self.ctx.author.id

    def member(self):
        """:return: a class of discord.member.Member"""
        return self.ctx.bot.get_guild(int(os.getenv("GUILD_SERVER_ID"))).get_member(self.discord_id())

    def voice(self):
        """ represents the member's voice state.

        example of instances in voice state:
            VoiceState:
                self_mute=bool
                self_deaf=bool
                self_stream=bool
                channel=
                    VoiceChannel:
                        id=int
                        name=str
                        position=int
                        bitrate=int
                        user_limit=int
                        category_id=int

        :return: the member's discord.member.VoiceState."""
        return self.member().voice

    def mention(self):
        """:return: a str that allows given member to be mentioned."""
        return self.member().mention
