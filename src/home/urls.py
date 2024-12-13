"""
URL configuration for home project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from auth import views as auth_views
from checkout import views as checkout_views
from subscriptions import views as subscription_views
from .views import (home_page,
                    about_page,
                    pwd_protected_view,
                    user_only_view,
                    staff_only_view
)

urlpatterns = [
    path("", home_page,  name='home'),
    path("checkout/sub-price/<int:price_id>/", checkout_views.product_price_redirect_view, name='sub-price-checkout'),
    path("checkout/start/", checkout_views.checkout_redirect_view, name='stripe-checkout-start'),
    path("checkout/success/", checkout_views.checkout_finalize_view, name='stripe-checkout-end'),
    path("login/", auth_views.login_view),
    path("register/", auth_views.register_view),
    path("pricing/", subscription_views.subscription_price_view, name='pricing'),
    path("pricing/<str:interval>/", subscription_views.subscription_price_view, name='pricing_interval'),
    path("about/", about_page),
    path('accounts/billing/', subscription_views.user_subscription_view, name='user_subscription'),
    path('accounts/billing/cancel/,', subscription_views.user_cancel_subscription_view, name='user_subscription_cancel'),
    path('accounts/', include('allauth.urls')),
    path('protected/user-only/', user_only_view),
    path('protected/staff-only/', staff_only_view),
    path('protected/', pwd_protected_view),
    path('profiles/', include('profiles.urls')),
    path('admin/', admin.site.urls),
]
