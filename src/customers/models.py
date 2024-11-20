import helpers.billing
from django.conf import settings
from django.db import models

#  Import signals from allauth
from allauth.account.signals import (
    user_signed_up as allauth_user_signed_up,
    email_confirmed as allauth_user_email_confirmed
)

# Create your models here.


User = settings.AUTH_USER_MODEL # auth.user

class Customer(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    init_email = models.EmailField(blank=True, null=True)
    init_email_confirmed = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.user.username}'
    
    def save(self, *args, **kwargs):
        if not self.stripe_id:
            if self.init_email_confirmed and self.init_email:
                email = self.user.email
                if email != "" or email is not None:
                    stripe_id = helpers.billing.create_customer(email=email, metadata={'user_id': self.user.id, 'username': self.user.username}, raw=False)
                    self.stripe_id = stripe_id
                    # print("Stripe_response", stripe_response)
        super().save(*args, **kwargs)


def allauth_user_signed_up_handler(request, user, *args, **kwargs):
    email = user.email
    Customer.objects.create(
        user=user,
        init_email=email,
        init_email_confirmed=False
    )

allauth_user_signed_up.connect(allauth_user_signed_up_handler)

def allauth_user_email_confirmed_handler(request, email_address, *args, **kwargs):
    qs = Customer.objects.filter(
        init_email=email_address,
        init_email_confirmed=False
    )
    for obj in qs:
        obj.init_email_confirmed = True
        # Send signal for email confirmation
        obj.save()

allauth_user_email_confirmed.connect(allauth_user_email_confirmed_handler)