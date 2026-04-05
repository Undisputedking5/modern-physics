from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Note(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="notes")
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)           # Full note content
    pdf_file = models.FileField(upload_to='notes/pdfs/', blank=True, null=True)
    image = models.ImageField(upload_to='notes/images/', blank=True, null=True)
    read_time = models.CharField(max_length=20, default="10 min")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']