from django.shortcuts import render

# Create your views here.
def home(request):
    from teacher.models import Announcement
    announcements = Announcement.objects.filter(is_published=True).order_by('-created_at')[:3]
    return render(request, 'home.html', {'announcements': announcements})


def info(request):
    return render(request, 'dashboard/info.html')
