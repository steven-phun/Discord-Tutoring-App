from my_classes.Context import Context


class Worker:
    def __init__(self, ctx, course: 'Course'):
        self.ctx = Context(ctx)  # the object that represents this member's Content.
        self.course = course  # the course object the tutor is tutoring.
        self.reaction_msg = None  # the reaction message sent by the tutor to get the next student.

    async def is_circulating(self):
        """checks if the tutor's reaction message is still awaiting a response.

        :return: True if the tutor's reaction message is still circulating the queue, otherwise return False.
        """
        return self.reaction_msg is None

    def hours(self):
        """convert the tutor's current session hours to a string.

        :return: a str that represents the tutor's current session hours.
        """
        return f'dummy string'
