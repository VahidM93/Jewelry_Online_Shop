from django import forms
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from .models import *


class CustomerCreationForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("gender","image", "age")
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'image': _('image'), 'gender': _('gender'), 'age': _('age')
        }


class CustomerChangeForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('gender', 'image', 'age')


class CustomerNewAddress(forms.ModelForm):

    postal_code_validator = RegexValidator(regex=r'^\d{10}$', message='Postal code must be exactly 10 digits.')

    class Meta:
        model= Address
        fields= ("city","body","postal_code")
        widgets = {
            'city': forms.CharField(attrs={'class': 'form-control'}),
            'body': forms.CharField(attrs={'class': 'form-control'}),
            'postal_code': forms.CharField(attrs={'class': 'form-control'}),
        }
        labels = {
            'city': _('city'), 'body': _('body'), 'postal_code': _('postal_code')
        }

        def clean_postal_code(self):
            postal_code = self.cleaned_data['postal_code']

            if not CustomerNewAddress.postal_code_validator(postal_code):
                raise forms.ValidationError('Postal code must be exactly 10 digits.')

            if Address.objects.filter(postal_code=postal_code).exists():
                raise forms.ValidationError('An address with this postal code already exists.')

            return postal_code
    


class AddressUpdateForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'
        exclude = ['customer']