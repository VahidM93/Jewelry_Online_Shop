from django.db import models
from accounts.models import Account
from core.models import ModelInfo
from django.utils.translation import gettext_lazy as _


class Customer(ModelInfo):
    user = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='customer', verbose_name=_('Account'))
    CHOICES = [('male', 'MALE'), ('female', 'FEMALE')]
    gender = models.CharField(max_length=20, choices=CHOICES, default='male', verbose_name=_('Gender'))
    image = models.ImageField(upload_to="customer/", null=True, blank=True, verbose_name=_('Image'))
    age = models.PositiveIntegerField(null=True, blank=True,verbose_name=_('Age'))

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')

    def __str__(self):
        return self.user.full_name

    def save(self, *args, **kwargs):
        male = 'img/male.png'
        female = 'img/female.png'
        if not self.image:
            self.image = male if self.gender == 'male' else female
        elif self.image and self.image in [male, female]:
            self.image = male if self.gender == 'male' else female
        super(Customer, self).save(*args, **kwargs)


class Address(ModelInfo):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses',
                                 verbose_name=_('Customer'))
    city = models.CharField(max_length=20, verbose_name=_('City'))
    body = models.TextField(max_length=120, verbose_name=_('Body'))
    postal_code = models.CharField(max_length=10, unique=True, verbose_name=_('Postal Code'))

    class Meta:
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')

    def __str__(self):
        return f'{self.city} - {self.body} - {self.postal_code}'