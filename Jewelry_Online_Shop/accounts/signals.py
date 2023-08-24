from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Account
from customers.models import Customer
from rest_framework.authtoken.models import Token

@receiver(post_save, sender=Account)
def create_customer(sender, **kwargs):
    if kwargs['created']:
        Customer.objects.create(user=kwargs['instance'])
        
for user in Account.objects.all():
    Token.objects.get_or_create(user=user)    