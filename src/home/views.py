import pathlib
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import HttpResponse
from visits.models import PageVisit


LOGIN_URL = settings.LOGIN_URL


this_dir = pathlib.Path(__file__).resolve().parent

def home_page(request, *args, **kwargs):
    return about_page(request, *args, **kwargs)
    # qs = PageVisit.objects.all()
    # page_qs = PageVisit.objects.filter(path=request.path)

    # try:
    #     percent = (page_qs.count() * 100.0) / qs.count() # Calculating the percentage of page visit
    # except:
    #     percent = 0 # If no page visit, percent will be 0
    
    # my_title = "My Page"
    # my_context = {
    #     "page_title": my_title,
    #     "query_set_count" : page_qs.count(),
    #     "total_visit_count" : qs.count(),
    #     "percent": percent,
    #     "path": request.path,
    #     "last_visit": page_qs.last() if page_qs.exists() else None,  # Getting the last visit if exists
    # }

    # html_template = "home.html"

    # PageVisit.objects.create()
    # return render(request, html_template, my_context)

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
    
    html_template = "home.html"

    PageVisit.objects.create()
    return render(request, html_template, my_context)

VALID_CODE = "abc123"

# Protecting Password view
def pwd_protected_view(request, *args, **kwargs):
    is_allowed = request.session.get('protected_page_allowed') or 0
    # print(request.session.get('protected_page_allowed'), type(request.session.get('protected_page_allowed')))
    if request.method == "POST":
        # print(request.POST)
        user_pwd_sent = request.POST.get("code") or None
        if user_pwd_sent == VALID_CODE:
            is_allowed = 1
            request.session['protected_page_allowed'] = is_allowed
    if is_allowed:
        return render(request, "protected/view.html", {})
    return render(request, "protected/entry.html", {})

@login_required(login_url=LOGIN_URL)
def user_only_view(request, *args, **kwargs):
    return render(request, "protected/user-only.html", {})

@staff_member_required(login_url=LOGIN_URL)
def staff_only_view(request, *args, **kwargs):
    return render(request, "protected/staff-only.html", {})