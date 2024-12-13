import helpers.billing
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from subscriptions.models import SubscriptionPrice, UserSubscription

# Create your views here.
@login_required
def user_subscription_view(request,):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        print('refresh sub')
        if user_sub_obj.stripe_id:
            sub_data = helpers.billing.get_subscription(user_sub_obj.stripe_id, raw=False)
            for k,v in sub_data.item():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
            messages.success(request, "Refresh Successfully")
        return redirect(user_sub_obj.get_absolute_url())
    return render(request, 'subscriptions/user_sub.html', {'subscription': user_sub_obj})

@login_required
def user_cancel_subscription_view(request,):
    user_sub_obj, created = UserSubscription.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        print('refresh sub')
        if user_sub_obj.stripe_id and user_sub_obj.isactive_sub_status:
            sub_data = helpers.billing.cancel_subscription(user_sub_obj.stripe_id, reason="End Subscription", feedback="other", cancel_at_period_end=True, raw=False)
            for k,v in sub_data.item():
                setattr(user_sub_obj, k, v)
            user_sub_obj.save()
            messages.success(request, "Plan Cancelled Successfully")
        return redirect(user_sub_obj.get_absolute_url())
    return render(request, 'subscriptions/user_cancel.html', {'subscription': user_sub_obj})



def subscription_price_view(request, interval='month'):
    # if not SubscriptionPrice.subscription.exists():
    #     pass
    qs = SubscriptionPrice.objects.filter(featured=True)
    monthly_qs = SubscriptionPrice.IntervalChoices.MONTHLY
    yearly_qs = SubscriptionPrice.IntervalChoices.YEARLY
    object_list = qs.filter(interval=monthly_qs)
    url_path_name = "pricing_interval"
    active = monthly_qs
    monthly_url = reverse(url_path_name, kwargs={"interval": monthly_qs})
    yearly_url = reverse(url_path_name, kwargs={"interval": yearly_qs})
    if interval == yearly_qs:
        object_list =   qs.filter(interval=yearly_qs)
        active=yearly_qs
    return render(request, "subscriptions/pricing.html", {
        "object_list":object_list,
        "monthly_url":monthly_url,
        "yearly_url":yearly_url,
        "active":active,
    })
