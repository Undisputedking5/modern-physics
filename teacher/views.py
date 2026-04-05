from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from django.db import models
from notes.models import Note, Category
from resources.models import Resource
from .models import Announcement, Lesson


def is_teacher_or_admin(user):
    return user.is_authenticated and user.is_superuser


def is_admin(user):
    return user.is_authenticated and user.is_superuser


staff_required = user_passes_test(is_teacher_or_admin, login_url='accounts:login')
admin_required = user_passes_test(is_admin, login_url='accounts:login')


def teacher_required(view_func):
    return login_required(staff_required(view_func), login_url='accounts:login')


# ── Dashboard ─────────────────────────────────────────────────────────────────
@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def dashboard(request):
    context = {
        'total_books': Resource.objects.filter(resource_type='workbook').count(),
        'total_past_papers': Resource.objects.filter(resource_type='past_paper').count(),
        'total_notes': Note.objects.count(),
        'total_announcements': Announcement.objects.count(),
        'total_lessons': Lesson.objects.count(),
        'recent_announcements': Announcement.objects.all()[:5],
        'recent_lessons': Lesson.objects.all()[:5],
    }
    return render(request, 'teacher/dashboard.html', context)


# ── Resources / Books ─────────────────────────────────────────────────────────
@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def manage_resources(request):
    resources = Resource.objects.all()
    return render(request, 'teacher/manage_resources.html', {'resources': resources})


@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def add_resource(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        resource_type = request.POST.get('resource_type', 'workbook')
        price = request.POST.get('price', '0')
        is_free = request.POST.get('is_free') == 'on'
        pdf_file = request.FILES.get('pdf_file')
        cover_image = request.FILES.get('cover_image')

        if title:
            r = Resource(
                title=title,
                description=description,
                resource_type=resource_type,
                price=price,
                is_free=is_free,
                author=request.user,
            )
            if pdf_file:
                r.pdf_file = pdf_file
            if cover_image:
                r.cover_image = cover_image
            r.save()
            messages.success(request, f'"{title}" added successfully.')
            return redirect('teacher:manage_resources')
    return render(request, 'teacher/resource_form.html', {'action': 'Add', 'resource': None})


@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def edit_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        resource.title = request.POST.get('title', resource.title).strip()
        resource.description = request.POST.get('description', resource.description).strip()
        resource.resource_type = request.POST.get('resource_type', resource.resource_type)
        resource.price = request.POST.get('price', resource.price)
        resource.is_free = request.POST.get('is_free') == 'on'
        if request.FILES.get('pdf_file'):
            resource.pdf_file = request.FILES['pdf_file']
        if request.FILES.get('cover_image'):
            resource.cover_image = request.FILES['cover_image']
        resource.save()
        messages.success(request, f'"{resource.title}" updated.')
        return redirect('teacher:manage_resources')
    return render(request, 'teacher/resource_form.html', {'action': 'Edit', 'resource': resource})


@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def delete_resource(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        name = resource.title
        resource.delete()
        messages.success(request, f'"{name}" deleted.')
        return redirect('teacher:manage_resources')
    return render(request, 'teacher/confirm_delete.html', {'object': resource, 'type': 'Resource'})


# ── Notes ─────────────────────────────────────────────────────────────────────
@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def manage_notes(request):
    notes = Note.objects.select_related('category').all()
    return render(request, 'teacher/manage_notes.html', {'notes': notes})


@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def add_note(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category_id = request.POST.get('category')
        description = request.POST.get('description', '').strip()
        content = request.POST.get('content', '').strip()
        read_time = request.POST.get('read_time', '10 min')
        pdf_file = request.FILES.get('pdf_file')
        image = request.FILES.get('image')

        if title and category_id:
            category = get_object_or_404(Category, pk=category_id)
            note = Note(
                title=title,
                category=category,
                description=description,
                content=content,
                read_time=read_time,
            )
            if pdf_file:
                note.pdf_file = pdf_file
            if image:
                note.image = image
            note.save()
            messages.success(request, f'Note "{title}" added.')
            return redirect('teacher:manage_notes')
    return render(request, 'teacher/note_form.html', {'action': 'Add', 'note': None, 'categories': categories})


@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def edit_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    categories = Category.objects.all()
    if request.method == 'POST':
        note.title = request.POST.get('title', note.title).strip()
        category_id = request.POST.get('category')
        if category_id:
            note.category = get_object_or_404(Category, pk=category_id)
        note.description = request.POST.get('description', note.description).strip()
        note.content = request.POST.get('content', note.content).strip()
        note.read_time = request.POST.get('read_time', note.read_time)
        if request.FILES.get('pdf_file'):
            note.pdf_file = request.FILES['pdf_file']
        if request.FILES.get('image'):
            note.image = request.FILES['image']
        note.save()
        messages.success(request, f'Note "{note.title}" updated.')
        return redirect('teacher:manage_notes')
    return render(request, 'teacher/note_form.html', {'action': 'Edit', 'note': note, 'categories': categories})


@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def delete_note(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == 'POST':
        name = note.title
        note.delete()
        messages.success(request, f'Note "{name}" deleted.')
        return redirect('teacher:manage_notes')
    return render(request, 'teacher/confirm_delete.html', {'object': note, 'type': 'Note'})


# ── Announcements / News ──────────────────────────────────────────────────────
@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def manage_announcements(request):
    announcements = Announcement.objects.all()
    return render(request, 'teacher/manage_announcements.html', {'announcements': announcements})


@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def add_announcement(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', 'news')
        body = request.POST.get('body', '').strip()
        is_published = request.POST.get('is_published') == 'on'
        if title:
            Announcement.objects.create(
                title=title, category=category, body=body,
                is_published=is_published, author=request.user
            )
            messages.success(request, f'Announcement "{title}" added.')
            return redirect('teacher:manage_announcements')
    return render(request, 'teacher/announcement_form.html', {'action': 'Add', 'announcement': None})


@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def edit_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        announcement.title = request.POST.get('title', announcement.title).strip()
        announcement.category = request.POST.get('category', announcement.category)
        announcement.body = request.POST.get('body', announcement.body).strip()
        announcement.is_published = request.POST.get('is_published') == 'on'
        announcement.save()
        messages.success(request, f'Announcement updated.')
        return redirect('teacher:manage_announcements')
    return render(request, 'teacher/announcement_form.html', {'action': 'Edit', 'announcement': announcement})


@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def delete_announcement(request, pk):
    announcement = get_object_or_404(Announcement, pk=pk)
    if request.method == 'POST':
        name = announcement.title
        announcement.delete()
        messages.success(request, f'Announcement "{name}" deleted.')
        return redirect('teacher:manage_announcements')
    return render(request, 'teacher/confirm_delete.html', {'object': announcement, 'type': 'Announcement'})


# ── Lessons ───────────────────────────────────────────────────────────────────
@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def manage_lessons(request):
    lessons = Lesson.objects.all()
    return render(request, 'teacher/manage_lessons.html', {'lessons': lessons})


@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def add_lesson(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        form = request.POST.get('form', '1')
        topic = request.POST.get('topic', '').strip()
        description = request.POST.get('description', '').strip()
        video_url = request.POST.get('video_url', '').strip()
        is_published = request.POST.get('is_published') == 'on'
        pdf_file = request.FILES.get('pdf_file')
        if title:
            lesson = Lesson(
                title=title, form=form, topic=topic, description=description,
                video_url=video_url or None, is_published=is_published, author=request.user
            )
            if pdf_file:
                lesson.pdf_file = pdf_file
            lesson.save()
            messages.success(request, f'Lesson "{title}" added.')
            return redirect('teacher:manage_lessons')
    return render(request, 'teacher/lesson_form.html', {'action': 'Add', 'lesson': None})


@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def edit_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        lesson.title = request.POST.get('title', lesson.title).strip()
        lesson.form = request.POST.get('form', lesson.form)
        lesson.topic = request.POST.get('topic', lesson.topic).strip()
        lesson.description = request.POST.get('description', lesson.description).strip()
        lesson.video_url = request.POST.get('video_url', '').strip() or None
        lesson.is_published = request.POST.get('is_published') == 'on'
        if request.FILES.get('pdf_file'):
            lesson.pdf_file = request.FILES['pdf_file']
        lesson.save()
        messages.success(request, f'Lesson updated.')
        return redirect('teacher:manage_lessons')
    return render(request, 'teacher/lesson_form.html', {'action': 'Edit', 'lesson': lesson})


@login_required(login_url='accounts:login')
@user_passes_test(is_teacher_or_admin, login_url='accounts:login')
def delete_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST':
        name = lesson.title
        lesson.delete()
        messages.success(request, f'Lesson "{name}" deleted.')
        return redirect('teacher:manage_lessons')
    return render(request, 'teacher/confirm_delete.html', {'object': lesson, 'type': 'Lesson'})


# ── Colleague Management ──────────────────────────────────────────────────────
@login_required(login_url='accounts:login')
@user_passes_test(is_admin, login_url='accounts:login')
def manage_colleagues(request):
    from accounts.models import Profile
    search_query = request.GET.get('q', '')
    if search_query:
        profiles = Profile.objects.filter(
            models.Q(user__username__icontains=search_query) |
            models.Q(full_name__icontains=search_query)
        ).exclude(user=request.user)
    else:
        profiles = Profile.objects.exclude(user=request.user)

    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        new_role = request.POST.get('role')
        if profile_id and new_role in ['student', 'teacher']:
            profile = get_object_or_404(Profile, pk=profile_id)
            profile.role = new_role
            profile.save()
            messages.success(request, f"Updated {profile.user.username}'s role to {new_role}.")
            return redirect('teacher:manage_colleagues')

    return render(request, 'teacher/manage_colleagues.html', {
        'profiles': profiles,
        'search_query': search_query
    })
