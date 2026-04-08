from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('process/', views.process_payment, name='process_payment'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
    path('status/<int:order_id>/', views.payment_status, name='payment_status'),
]
