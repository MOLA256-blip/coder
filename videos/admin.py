from django.contrib import admin
from .models import Video, Comment


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'uploader', 'views', 'uploaded_at', 'is_public']
    list_filter = ['is_public', 'uploaded_at', 'uploader']
    search_fields = ['title', 'description', 'uploader__username']
    readonly_fields = ['views', 'uploaded_at']
    ordering = ['-uploaded_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'content', 'video__title']
    ordering = ['-created_at']
