from typing import Any
from django.core.management.base import BaseCommand

from subscriptions.models import Subscription

class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any):
        qs = Subscription.objects.filter(active=True)
        for obj in qs:
            # print("Groups present" ,obj.group.all(), "\n")
            sub_perms = obj.permission.all()
            for groups in obj.group.all():
                groups.permissions.set(sub_perms)
                # for perm in obj.permission.all():
                #     groups.permissions.add(perm)
            # print("All permissions" ,obj.permission.all())