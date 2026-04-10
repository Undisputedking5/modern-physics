from django.shortcuts import render, get_object_or_404

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


def lesson_list(request):
    from teacher.models import Lesson
    lessons = Lesson.objects.filter(is_published=True).order_by('form', '-created_at')
    
    # Group lessons by form
    grouped_lessons = {}
    for lesson in lessons:
        if lesson.form not in grouped_lessons:
            grouped_lessons[lesson.form] = []
        grouped_lessons[lesson.form].append(lesson)
    
    return render(request, 'dashboard/lesson_list.html', {
        'grouped_lessons': sorted(grouped_lessons.items())
    })


def lesson_detail(request, pk):
    from teacher.models import Lesson
    lesson = get_object_or_404(Lesson, pk=pk, is_published=True)
    return render(request, 'dashboard/lesson_detail.html', {'lesson': lesson})
