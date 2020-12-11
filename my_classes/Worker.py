class Worker:
    def __init__(self, discord_id, course):
        self.discord_id = discord_id  # the tutor's discord id.
        self.course = course  # the course object the tutor is tutoring.

    def mention(self):
        """generate a discord syntax that represents a mention for given Worker.

        :return: a str that that represents a mention.
        """
        return f'<@!{self.discord_id}>'

    def hours(self):
        """convert the tutor's current session hours to a string.

        :return: a str that represents the tutor's current session hours.
        """
        return f'dummy string'
