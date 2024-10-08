import pathlib
from django.shortcuts import render
from django.http import HttpResponse
from visits.models import PageVisit

this_dir = pathlib.Path(__file__).resolve().parent

def home_page(request, *args, **kwargs):
    qs = PageVisit.objects.all()
    queryset = PageVisit.objects.filter(path=request.path)
    
    my_title = "My Page"
    my_context = {
        "page_title": my_title,
        "query_set_count" : queryset.count(),
        "total_visit_count" : qs.count()
    }

    html_template = "home.html"

    PageVisit.objects.create()
    return render(request, html_template, my_context)