from django.contrib import admin
from .models import Resource

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'price', 'is_free', 'created_at']
    list_filter = ['resource_type', 'is_free', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = [
        ('Basic Information', {
            'fields': ['title', 'resource_type', 'description', 'author']
        }),
        ('Pricing', {
            'fields': ['price', 'is_free']
        }),
        ('Files', {
            'fields': ['pdf_file', 'cover_image']
        }),
        ('Meta', {
            'fields': ['created_at', 'updated_at']
        }),
    ]