import pathlib
from django.shortcuts import render
from django.http import HttpResponse
from visits.models import PageVisit

this_dir = pathlib.Path(__file__).resolve().parent

def home_page(request, *args, **kwargs):
    qs = PageVisit.objects.all()
    page_qs = PageVisit.objects.filter(path=request.path)

    try:
        percent = (page_qs.count() * 100.0) / qs.count() # Calculating the percentage of page visit
    except:
        percent = 0 # If no page visit, percent will be 0
    
    my_title = "My Page"
    my_context = {
        "page_title": my_title,
        "query_set_count" : page_qs.count(),
        "total_visit_count" : qs.count(),
        "percent": percent,
        "path": request.path,
        "last_visit": page_qs.last() if page_qs.exists() else None,  # Getting the last visit if exists
    }

    html_template = "home.html"

    PageVisit.objects.create()
    return render(request, html_template, my_context)

def about_page(request, *args, **kwargs):
    qs = PageVisit.objects.all()
    page_qs = PageVisit.objects.filter(path=request.path)

    try:
        percent = (page_qs.count() * 100.0) / qs.count() # Calculating the percentage of page visit
    except:
        percent = 0 # If no page visit, percent will be 0
    
    my_title = "My Page"
    my_context = {
        "page_title": my_title,
        "query_set_count" : page_qs.count(),
        "total_visit_count" : qs.count(),
        "percent": percent,
        "path": request.path,
        "last_visit": page_qs.last() if page_qs.exists() else None,  # Getting the last visit if exists
    }
    
    html_template = "about.html"

    PageVisit.objects.create()
    return render(request, html_template, my_context)