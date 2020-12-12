import os


class Context:
    def __init__(self, ctx):
        self.ctx = ctx  # the discord Context for a given member.

    def member(self):
        """:return: class discord.member.Member"""
        return self.ctx.bot.get_guild(int(os.getenv("GUILD_SERVER_ID"))).get_member(self.ctx.author.id)

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
