import helpers.billing
from django.db.models import Q
from customers.models import Customer

from subscriptions.models import Subscription, UserSubscription, SubscriptionStatus


def refresh_active_users_subscriptions(user_ids=None, active_only=True):
    qs = UserSubscription.objects.all()
    if active_only:
        qs = qs.by_active_trialing()
    if user_ids is not None:
        qs = qs.by_user_ids(user_ids=user_ids)
    complete_count = 0
    qs_count = qs.count()
    for obj in qs:
        if obj.stripe_id:
            sub_data = helpers.billing.get_subscription(obj.stripe_id, raw=False)
            for k,v in sub_data.items():
                setattr(obj, k, v)
            obj.save()
            complete_count += 1
    return complete_count == qs_count
    
def clear_dangling_sub():
    qs = Customer.objects.filter(stripe_id__isnull = False)
    for customer_obj in qs:
        user = customer_obj.user
        customer_stripe_id = customer_obj.stripe_id
        print(f"Sync {user} - {customer_stripe_id} subs and remove old ones")
        # python manage.py python manage.py sync_user_subs
        subs = helpers.billing.get_customer_active_subscription(customer_stripe_id)
        for sub in subs:
            print(sub.id) # python manage.py sync_user_subs
            existing_user_sub_qs = UserSubscription.objects.filter(stripe_id__iexact=f"{sub.id}".strip())
            if existing_user_sub_qs.exists():
                continue
            # Removing inactive sub from stripe
            helpers.billing.cancel_subscription(sub.id, reason="Dangling active subscription", cancel_at_period_end=True)
            print(sub.id, existing_user_sub_qs.exists()) # python manage.py sync_user_subs
                

def sync_subs_group_permissions():
    qs = Subscription.objects.filter(active=True)
    for obj in qs:
        # print("Groups present" ,obj.group.all(), "\n")
        sub_perms = obj.permission.all()
        for groups in obj.group.all():
            groups.permissions.set(sub_perms)          