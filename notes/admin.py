from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Note

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'read_time', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = [
        ('Basic Information', {
            'fields': ['title', 'category', 'description']
        }),
        ('Content', {
            'fields': ['content', 'pdf_file', 'image']
        }),
        ('Meta', {
            'fields': ['read_time', 'created_at', 'updated_at']
        }),
    ]