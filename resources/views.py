from django.shortcuts import render, get_object_or_404
from .models import Resource


def resources_list(request):
    workbooks = Resource.objects.filter(resource_type='workbook')
    past_papers = Resource.objects.filter(resource_type='past_paper')

    context = {
        'workbooks': workbooks,
        'past_papers': past_papers,
        'all_resources': Resource.objects.all(),
    }
    return render(request, 'resources/list.html', context)


def resource_detail(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    context = {
        'resource': resource,
    }
    return render(request, 'resources/detail.html', context)