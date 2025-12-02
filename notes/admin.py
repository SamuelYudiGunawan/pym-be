from django.contrib import admin
from .models import Note, Reply
from .applications.model_methods import NoteMethods, ReplyMethods


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_preview', 'get_display_author',
                    'is_anonymous', 'created_at', 'get_reply_count']
    list_filter = ['is_anonymous', 'created_at']
    search_fields = ['content', 'author_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

    def get_display_author(self, obj):
        return NoteMethods.get_display_author(obj)
    get_display_author.short_description = 'Author'

    def get_reply_count(self, obj):
        return NoteMethods.get_reply_count(obj)
    get_reply_count.short_description = 'Replies'


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ['id', 'content_preview',
                    'get_display_author', 'is_anonymous', 'note', 'created_at']
    list_filter = ['is_anonymous', 'created_at', 'note']
    search_fields = ['content', 'author_name', 'note__content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

    def get_display_author(self, obj):
        return ReplyMethods.get_display_author(obj)
    get_display_author.short_description = 'Author'
