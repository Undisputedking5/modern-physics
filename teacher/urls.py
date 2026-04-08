from django.urls import path
from . import views

app_name = 'teacher'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Resources / Books
    path('resources/', views.manage_resources, name='manage_resources'),
    path('resources/add/', views.add_resource, name='add_resource'),
    path('resources/edit/<int:pk>/', views.edit_resource, name='edit_resource'),
    path('resources/delete/<int:pk>/', views.delete_resource, name='delete_resource'),

    # Notes
    path('notes/', views.manage_notes, name='manage_notes'),
    path('notes/add/', views.add_note, name='add_note'),
    path('notes/edit/<int:pk>/', views.edit_note, name='edit_note'),
    path('notes/delete/<int:pk>/', views.delete_note, name='delete_note'),

    # Announcements / News
    path('announcements/', views.manage_announcements, name='manage_announcements'),
    path('announcements/add/', views.add_announcement, name='add_announcement'),
    path('announcements/edit/<int:pk>/', views.edit_announcement, name='edit_announcement'),
    path('announcements/delete/<int:pk>/', views.delete_announcement, name='delete_announcement'),

    # Lessons
    path('lessons/', views.manage_lessons, name='manage_lessons'),
    path('lessons/add/', views.add_lesson, name='add_lesson'),
    path('lessons/edit/<int:pk>/', views.edit_lesson, name='edit_lesson'),
    path('lessons/delete/<int:pk>/', views.delete_lesson, name='delete_lesson'),
    path('colleagues/', views.manage_colleagues, name='manage_colleagues'),
    path('payment-settings/', views.payment_settings, name='payment_settings'),
]
