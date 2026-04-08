from django.shortcuts import render

# Create your views here.
def home(request):
    from teacher.models import Announcement
    announcements = Announcement.objects.filter(is_published=True).order_by('-created_at')[:3]
    return render(request, 'home.html', {'announcements': announcements})


def info(request):
    from teacher.models import Announcement, Lesson
    announcements = Announcement.objects.filter(is_published=True).order_by('-created_at')
    latest_lessons = Lesson.objects.filter(is_published=True).order_by('-created_at')[:5]
    
    return render(request, 'dashboard/info.html', {
        'announcements': announcements,
        'latest_lessons': latest_lessons
    })
