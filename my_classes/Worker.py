from my_classes.Context import Context
from my_classes.Schedule import Schedule


class Worker:
    def __init__(self, ctx, name: str, course: 'Course'):
        self.ctx = Context(ctx)  # the object that represents this member's Content.
        self.schedule = Schedule(course.code)  # the schedule object that corresponds to the tutor's session.
        self.name = name  # the str that represents the tutor's full name.
        self.course = course  # the course object the tutor is tutoring.
        self.reaction_msg = None  # the reaction message sent by the tutor to get the next student.

    def is_circulating(self):
        """checks if the tutor's reaction message is still awaiting a response.

        :return: True if the tutor's reaction message is still circulating the queue, otherwise return False.
        """
        return self.reaction_msg is not None
