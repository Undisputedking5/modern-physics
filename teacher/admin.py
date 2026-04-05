from django.contrib import admin
from .models import Announcement, Lesson


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'is_published', 'created_at']
    list_filter = ['category', 'is_published']
    search_fields = ['title', 'body']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'form', 'topic', 'is_published', 'created_at']
    list_filter = ['form', 'is_published']
    search_fields = ['title', 'topic']
