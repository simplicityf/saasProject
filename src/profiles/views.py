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
    return render(request, "profiles/list.html", context)


# Create your views here.
@login_required
def profile_view(request, username=None, *args, **kwargs):
    user = request.user
    # profile_user_obj = User.objects.get(username=username)
    profile_user_obj = get_object_or_404(User, username=username)
    is_me = profile_user_obj == user
    return HttpResponse(f"Hello {username} welcome to profile {profile_user_obj.id}, {is_me}")
