from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

class Resource(models.Model):
    RESOURCE_TYPES = [
        ('workbook', 'Workbook'),
        ('past_paper', 'Past Paper'),
        ('mock_exam', 'Mock Exam'),
        ('questions', 'Practice Questions'),
    ]

    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='workbook')
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)   # 0 = Free
    is_free = models.BooleanField(default=False)

    pdf_file = models.FileField(
        upload_to='resources/pdfs/',
        blank=True,
        null=True,
        storage=settings.PDF_STORAGE,
    )
    cover_image = models.ImageField(upload_to='resources/covers/', blank=True, null=True)

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def display_price(self):
        if self.is_free or self.price == 0:
            return "Free"
        return f"Ksh {self.price}"

    class Meta:
        ordering = ['-created_at']