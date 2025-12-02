from django.db import models
from django.utils import timezone


class Note(models.Model):
    """Model for storing user thoughts/notes"""
    content = models.TextField(
        help_text="Your thoughts to share with the world")
    author_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Your name (leave blank to post anonymously)"
    )
    is_anonymous = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['is_anonymous']),
        ]


class Reply(models.Model):
    """Model for storing replies to notes"""
    note = models.ForeignKey(
        Note, on_delete=models.CASCADE, related_name='replies')
    content = models.TextField(help_text="Your response to this thought")
    author_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Your name (leave blank to reply anonymously)"
    )
    is_anonymous = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = "Replies"
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['is_anonymous']),
            models.Index(fields=['note', 'created_at']),
        ]
