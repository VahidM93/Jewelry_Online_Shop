from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import AccountManager
from django.utils.translation import gettext_lazy as _
from core.utils import phone_regex_validator
from core.models import ModelInfo


class Account(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=100, verbose_name='Full name')
    birth_date = models.DateField(null=True, blank=True, verbose_name='Birthday')
    postal_code = models.IntegerField(null=True, blank=True, verbose_name='Postal Code')
    phone_number = models.CharField(max_length=13, unique=True, validators=[phone_regex_validator],
                                    verbose_name=_('Phone Number'))
    email = models.EmailField(max_length=255, unique=True, null=True, blank=True, verbose_name='Email')
    created_at=models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    objects = AccountManager()

    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    def __str__(self):
        return self.phone_number

    @property
    def is_staff(self):
        return self.is_admin


class Address(ModelInfo):
    address = models.CharField(max_length=200)
    account_id = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return self.address
