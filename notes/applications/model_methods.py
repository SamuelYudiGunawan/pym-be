from django.utils import timezone


class NoteMethods:
    """Methods and properties for Note model"""

    @staticmethod
    def get_display_author(note):
        """Returns the author name to display"""
        if note.is_anonymous or not note.author_name:
            return "Anonymous"
        return note.author_name

    @staticmethod
    def get_reply_count(note):
        """Returns the number of replies to this note"""
        return note.replies.count()

    @staticmethod
    def get_str_representation(note):
        """Returns string representation of the note"""
        if note.is_anonymous or not note.author_name:
            return f"Anonymous Note - {note.created_at.strftime('%B %d, %Y')}"
        return f"{note.author_name}'s Note - {note.created_at.strftime('%B %d, %Y')}"


class ReplyMethods:
    """Methods and properties for Reply model"""

    @staticmethod
    def get_display_author(reply):
        """Returns the author name to display"""
        if reply.is_anonymous or not reply.author_name:
            return "Anonymous"
        return reply.author_name

    @staticmethod
    def get_str_representation(reply):
        """Returns string representation of the reply"""
        if reply.is_anonymous or not reply.author_name:
            return f"Anonymous Reply to {reply.note}"
        return f"{reply.author_name}'s Reply to {reply.note}"

