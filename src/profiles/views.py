from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model


User = get_user_model()


@login_required
def profile_list_view(request):
    context = {
        "object_list": User.objects.filter(is_active = True)
    }
    return render(request, "profiles/userlist.html", context)


# @login_required
# def profile_view(request, username=None, *args, **kwargs):
#     user = request.user
#     # profile_user_obj = User.objects.get(username=username)
#     profile_user_obj = get_object_or_404(User, username=username)
#     is_me = profile_user_obj == user
#     return HttpResponse(f"Hello {username} welcome to profile {profile_user_obj.id}, {is_me}")

@login_required
def profile_detail_view(request, username=None, *args, **kwargs):
    user = request.user
    
    # # print("Has free permission",user.has_perm("subcriptions.free"),
    #       "Has basic permission",user.has_perm("subcriptions.basic"),
    #       "Has advance permission",user.has_perm("subcriptions.advance"),
    #       "Has advance pro permission",user.has_perm("subcriptions.advance pro"))
    
    # user_groups = user.groups.all()
    # print("User groups", user_groups)
    # if user_groups.filter(name__icontains='free').exists():
    #     return HttpResponse("You are on free plan")
    # elif user_groups.filter(name__icontains='Advance Pro Plan').exists():
    #     return HttpResponse("You are on Advance Pro plan plan")
    profile_user_obj = get_object_or_404(User, username=username)
    is_me = profile_user_obj == user
    context = {
        "object": profile_user_obj,
        "instance": profile_user_obj,
        "is_me": is_me,
    }
    return render(request, "profiles/detailuserprofile.html", context)
