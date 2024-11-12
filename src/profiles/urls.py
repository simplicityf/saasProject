
from django.urls import path
from . import views

urlpatterns = [
    path("", views.profile_list_view),
    path("<username>/", views.profile_view),
]
