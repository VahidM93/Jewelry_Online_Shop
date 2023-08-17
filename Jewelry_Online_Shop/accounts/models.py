from datetime import timedelta,datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,Group,Permission
import pytz
from .managers import AccountManager
from django.utils.translation import gettext_lazy as _
from core.utils import phone_regex_validator




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
    groups = models.ManyToManyField(Group, related_name='user_accounts')
    user_permissions = models.ManyToManyField(Permission, related_name='user_accounts_permissions')
    class Meta:
        verbose_name = _('Account')
        verbose_name_plural = _('Accounts')

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['email','full_name']

    def __str__(self):
        return self.phone_number

    @property
    def is_staff(self):
        return self.is_admin

class OtpCode(models.Model):
        phone_number = models.CharField(max_length=13, validators=[phone_regex_validator], verbose_name=_('Phone Number'))
        code = models.PositiveSmallIntegerField(verbose_name=_('Code'))
        created = models.DateTimeField(auto_now=True, verbose_name=_('Created'))

        class Meta:
            verbose_name = _('Otp Code')
            verbose_name_plural = _('Otp Codes')

        def save(self, *args, **kwargs):
            self.phone_number = '0' + self.phone_number[3:] if len(self.phone_number) == 13 else self.phone_number
            super(OtpCode, self).save(*args, **kwargs)

        @classmethod
        def is_code_available(cls, phone_number):
         counter = cls.objects.filter(phone_number=phone_number).count()
         return False if counter > 5 else True

        def __str__(self):
            return f'{self.phone_number} - {self.code} - {self.created}'

        def is_valid(self):
            # utc = pytz.UTC
            # expire = self.created + timedelta(minutes=30, hours=3)
            # checked_on = datetime.now().replace(tzinfo=utc)
            # expired_on = expire.replace(tzinfo=utc)
            # if expired_on > checked_on:
                return True
            # self.delete()
            # return False