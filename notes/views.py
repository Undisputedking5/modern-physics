from django.shortcuts import render, get_object_or_404

from notes.models import Note, Category


# Create your views here.
def notes_list(request):
    notes = Note.objects.all()
    categories = Category.objects.all()

    context = {
        'notes': notes,
        'categories': categories,
    }
    return render(request, 'notes/index.html', context)


def note_detail(request, note_id):
    note = get_object_or_404(Note, id=note_id)

    context = {
        'note': note,
    }
    return render(request, 'notes/detail.html', context)