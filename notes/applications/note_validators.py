from django.core.exceptions import ValidationError


class NoteValidator:
    """Validation logic for Note model"""

    @staticmethod
    def validate_content(content):
        """Validate note content"""
        if not content or len(content.strip()) < 10:
            raise ValidationError(
                "Please share at least 10 characters of your thoughts.")
        return content.strip()

    @staticmethod
    def validate_author_name(author_name):
        """Validate author name"""
        if author_name and len(author_name.strip()) < 2:
            raise ValidationError(
                "Author name must be at least 2 characters long.")
        return author_name.strip() if author_name else None


class ReplyValidator:
    """Validation logic for Reply model"""

    @staticmethod
    def validate_content(content):
        """Validate reply content"""
        if not content or len(content.strip()) < 5:
            raise ValidationError(
                "Please write at least 5 characters for your response.")
        return content.strip()

    @staticmethod
    def validate_author_name(author_name):
        """Validate author name"""
        if author_name and len(author_name.strip()) < 2:
            raise ValidationError(
                "Author name must be at least 2 characters long.")
        return author_name.strip() if author_name else None

