from django.db import models
from django.contrib.auth.models import User
from resources.models import Resource

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    resource = models.ForeignKey(Resource, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200) # Snapshot of title
    price = models.DecimalField(max_digits=10, decimal_places=2) # Snapshot of price
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.title} (x{self.quantity})"

class MpesaTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='mpesa_transactions')
    merchant_request_id = models.CharField(max_length=100, unique=True)
    checkout_request_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True, null=True)
    result_code = models.IntegerField(blank=True, null=True)
    result_desc = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='Sent')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TXN {self.checkout_request_id} - {self.phone_number}"

class MpesaConfiguration(models.Model):
    name = models.CharField(max_length=100, default="Primary Configuration")
    short_code = models.CharField(max_length=50, default='174379', help_text="The M-Pesa Paybill or Till Number")
    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    passkey = models.TextField(help_text="Lipa Na M-Pesa Online Passkey")
    is_sandbox = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "M-Pesa Configuration"
        verbose_name_plural = "M-Pesa Configurations"

    def __str__(self):
        return self.name
