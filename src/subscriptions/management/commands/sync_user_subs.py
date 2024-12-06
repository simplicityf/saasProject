import helpers.billing
from typing import Any
from django.core.management.base import BaseCommand
from customers.models import Customer

from subscriptions.models import UserSubscription

class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any):
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
                
            