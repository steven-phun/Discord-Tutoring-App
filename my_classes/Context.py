class Context:
    def __init__(self, ctx):
        self.ctx = ctx  # the discord Context for a given member.

    def voice(self):
        """represents the member's voice channel

        :return: the member's discord.member.VoiceState.
        """
        return self.ctx.author.voice
