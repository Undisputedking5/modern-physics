from django.db import models
from django.contrib.auth.models import User


class Announcement(models.Model):
    CATEGORY_CHOICES = [
        ('news', 'News'),
        ('info', 'Info'),
        ('event', 'Event'),
    ]
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='news')
    body = models.TextField()
    is_published = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Lesson(models.Model):
    FORM_CHOICES = [
        ('1', 'Form 1'),
        ('2', 'Form 2'),
        ('3', 'Form 3'),
        ('4', 'Form 4'),
    ]
    title = models.CharField(max_length=200)
    form = models.CharField(max_length=5, choices=FORM_CHOICES, default='1')
    topic = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or any video link")
    pdf_file = models.FileField(upload_to='lessons/pdfs/', blank=True, null=True)
    is_published = models.BooleanField(default=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Form {self.form} – {self.title}"

    class Meta:
        ordering = ['-created_at']
