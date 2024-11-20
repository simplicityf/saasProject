import helpers.billing
import stripe

from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.conf import settings

from decouple import config

# Create your models here.

User = settings.AUTH_USER_MODEL # auth.User

ALLOW_CUSTOM_GROUPS = True # Alllow custom group

STRIPE_SECRET_KEY=config("STRIPE_SECRET_KEY", default="", cast=str)

# Subcriptions permission
SUBSCRIPTION_PERMISSIONS = [
            ("advance pro", "Advance Pro Perm"), # subscriptions.advance  pro
            ("advance", "Advance Perm"), # subscriptions.advance
            ("basic", "Basic Perm"), # subscriptions.basic
            ("free", "Free Perm") # subscriptions.free
        ]


class Subscription(models.Model):
    """
    Subscription Plan = Stripe Product
    """
    name = models.CharField(max_length=255)
    active = models.BooleanField(default=True)
    group = models.ManyToManyField(Group) #adding groups to admin site
    permission = models.ManyToManyField(Permission, limit_choices_to={"content_type__app_label": "subscriptions", "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]}) # adding permission to admin site, limitting the permission to subscriptions only
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    
    # Changing subscription object to name
    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        permissions = SUBSCRIPTION_PERMISSIONS
    
    def save(self, *args, **kwargs):
        if not self.stripe_id:
            stripe_id = helpers.billing.create_product(name=self.name, metadata={'subscription_plan_id': self.id}, raw=False)
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)


class SubscriptionPrice(models.Model):
    """
    Subscription Pricing = Stripe Price
    """
    
    # Choices for price plan
    class IntervalChoices(models.TextChoices):
        MONTHLY = 'month', 'Monthly'
        YEARLY = 'year', 'Yearly'
    
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    interval = models.CharField(max_length=120, default=IntervalChoices.MONTHLY, choices= IntervalChoices.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    
    @property
    def stripe_currency(self):
        return "usd"
    
    @property
    def stripe_price(self):
        """
        remove decimal places for price 
        """
        return self.price * 100  # convert to cents
    
    @property
    def product_stripe_id(self):
        if not self.subscription:
            return None
        subscription_stripe_id = self.subscription.stripe_id
        return subscription_stripe_id + f':{self.id}'
    
    def save(self, *args, **kwargs):
        if (not self.stripe_id and self.product_stripe_id is not None):
            # stripe.api_key = STRIPE_SECRET_KEY

            stripe_id = helpers.billing.create_price(
                currency=self.stripe_currency,
                unit_amount=self.stripe_price,
                interval=self.interval,
                product=self.product_stripe_id,
                metadata= {
                    "subscription_plan_price_id": self.id
                },
                raw=False
            )
            self.stripe_id = stripe_id
        super().save(*args, **kwargs)
        
    

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # if user is deleted, their subscription is deleted as well
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True) # one-to-one relationship with subscription model
    active = models.BooleanField(default=True)
    
    # Changing usersubscription object to name
    def __str__(self):
        return f'{self.user.username} - {self.subscription}' if self.subscription else f'{self.user.username} - No subscription'  

def user_sub_post_save(sender, instance, *args, **kwargs):
    user_sub_instance = instance
    user = user_sub_instance.user
    subscription_obj = user_sub_instance.subscription

    groups_ids = []  # Initialize to an empty list to avoid UnboundLocalError
    groups = []      # Default empty queryset for safety

    if subscription_obj is not None:
        groups = subscription_obj.group.all() 
        groups_ids = list(groups.values_list('id', flat=True))  # Convert to list

    if not ALLOW_CUSTOM_GROUPS:
        # If custom groups are not allowed, simply assign the subscription's groups
        user.groups.set(groups)
    else:
        # Handle custom group logic
        sub_qs = Subscription.objects.filter(active=True)

        if subscription_obj is not None:
            sub_qs = sub_qs.exclude(id=subscription_obj.id)  # Exclude current subscription

        # Get IDs of all groups from other active subscriptions
        subs_groups = sub_qs.values_list("group__id", flat=True)
        subs_groups_set = set(subs_groups)

        # Current groups assigned to the user
        current_groups = user.groups.all().values_list('id', flat=True)
        current_groups_set = set(current_groups) - subs_groups_set

        # Combine groups from the subscription with existing valid groups
        groups_ids_set = set(groups_ids)
        final_group_ids = list(groups_ids_set | current_groups_set)

        # Assign the final group list to the user
        user.groups.set(final_group_ids)
 
post_save.connect(user_sub_post_save, sender=UserSubscription)