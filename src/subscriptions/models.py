import helpers.billing
from django.db.models import Q
from django.db import models
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.conf import settings
from django.urls import reverse
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
    subtitle= models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True)
    group = models.ManyToManyField(Group) #adding groups to admin site
    permission = models.ManyToManyField(Permission, limit_choices_to={"content_type__app_label": "subscriptions", "codename__in": [x[0] for x in SUBSCRIPTION_PERMISSIONS]}) # adding permission to admin site, limitting the permission to subscriptions only
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    order = models.IntegerField(default=-1, help_text='Ordering from Django Pricing page')
    featured = models.BooleanField(default=True, help_text='Feautured on Django Pricing page')
    updated=models.DateTimeField(auto_now=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    features = models.TextField(help_text="Feautures for Pricing, seperated by new line", blank=True, null=True)
    
    # Changing subscription object to name
    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        ordering = ['order', 'featured', '-updated']
        permissions = SUBSCRIPTION_PERMISSIONS
    
    def get_features_as_list(self):
        if not self.features:
            return [None]
        return [x.strip for x in self.features.split("\n")]
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
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    interval = models.CharField(max_length=120, default=IntervalChoices.MONTHLY, choices= IntervalChoices.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=99.99)
    order = models.IntegerField(default=-1, help_text='Ordering from Django Pricing page')
    featured = models.BooleanField(default=True, help_text='Feautured on Django Pricing page')
    updated=models.DateTimeField(auto_now=True)
    timestamp=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['subscription__order' ,'order', 'featured', '-updated']
    
    def get_checkout_urls(self):
        return reverse("sub-price-checkout",
                       kwargs = {"price_id": self.id})
    
    @property
    def display_features_list(self):
        if not self.subscription:
            return []
        return self.subscription.get_features_as_list() 
    @property
    def display_sub_name(self):
        if not self.subscription:
            return "Plan"
        return self.subscription.name
    
    @property
    def display_sub_subtitle(self):
        if not self.subscription:
            return "Plan"
        return self.subscription.subtitle
    
    @property
    def stripe_currency(self):
        return "usd"
    
    @property
    def stripe_price(self):
        """
        remove decimal places for price 
        """
        return int(self.price * 100)  # convert to cents
    
    @property
    def product_stripe_id(self):
        if not self.subscription:
            return None
        return self.subscription.stripe_id
    
    def save(self, *args, **kwargs):
        if (not self.stripe_id and self.product_stripe_id is not None):
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
        if self.featured and self.subscription:
            qs = SubscriptionPrice.objects.filter(
                subscription = self.subscription,
                interval = self.interval
            ).exclude(id=self.id)
            qs.update(featured=False)
        
# Subscription Status
class SubscriptionStatus(models.TextChoices):
    ACTIVE= 'active', 'Active'
    TRIALING= 'trialing', 'Trialing'
    INCOMPLETE= 'incomplete', 'Incomplete'
    INCOMPLETE_EXPIRED= 'incomplet_expired', 'Incomplete Expired'
    PAST_DUE= 'past_due', 'Past Due'
    CANCELED= 'canceled', 'Canceled'
    UNPAID= 'unpaid', 'Unpaid'
    PAUSED= 'paused', 'Paused'

class UserSubscriptionQuerySet(models.QuerySet):
    def by_active_trialing(self):
        active_qs_lookup = (
            Q(status = SubscriptionStatus.ACTIVE) |
            Q(status = SubscriptionStatus.TRIALING)
        )
        return self.filter(active_qs_lookup)
    
    def by_user_ids(self, user_ids=None):
        if isinstance(user_ids, list):
            return self.filter(user_id__in=user_ids)
        elif isinstance(user_ids, int):
            return self.filter(user_id__in=[user_ids])
        elif isinstance(user_ids, str):
            return self.filter(user_id__in=[user_ids])
        return self

class UserSubscriptionManager(models.Manager):
    def get_queryset(self):
        return UserSubscriptionQuerySet(self.model, using=self._db)
    
    # def by_user_ids(self, user_ids=None):
    #     return self.get_queryset().by_user_ids(user_ids=user_ids)

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # if user is deleted, their subscription is deleted as well
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True) # one-to-one relationship with subscription model
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    active = models.BooleanField(default=True)
    user_cancelled = models.BooleanField(default=False)
    original_period_start = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    current_period_start = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True) #subscription started
    current_period_end = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True) #subscription ended
    cancel_at_period_end = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=SubscriptionStatus.choices, null=True, blank=True) #setting current status
    
    objects = UserSubscriptionManager()
    
    def get_absolute_url(self):
        return reverse("user_subscription")
    
    def get_cancel_url(self):
        return reverse("user_subscription_cancel")
    
    @property
    def isactive_sub_status(self):
        return self.status in [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIALING]
    
    @property
    def plan_name(self):
        if not self.subscription:
            return None
        return self.subscription.name
    
    def serialize(self):
        return {
            "plan": self.plan_name,
            "status": self.status,
            "current_period_start": self.current_period_start,
            "current_period_end": self.current_period_end      
        }
    
    
    @property
    def billing_cycle_anchor(self):
        """
        https://docs.stripe.com/payments/checkout/billing-cycle
        Optional delay to start new subscription in stripe checkout
        """
        if not self.current_period_end:
            return None
        return int(self.current_period_end.timestamp()) 
    
    def save(self, *args, **kwargs):
        if ( self.original_period_start is None and self.current_period_start is not None):
            self.original_period_start = self.current_period_start
        super().save(*args, **kwargs)
    
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