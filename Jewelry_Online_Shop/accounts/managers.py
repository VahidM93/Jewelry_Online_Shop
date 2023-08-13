from django.contrib.auth.models import BaseUserManager
import re
from django.forms import ValidationError
from core.utils import phone_regex,full_name_regex

class AccountManager(BaseUserManager):
    def create_user(self, phone_number, email,full_name, password):
        if not phone_number:
            raise ValueError('user must have Phone Number')
        if not full_name:
            raise ValueError('user must have full_name')
        if not email:
            raise ValueError('user must have email')
        #create user ,model ref to objects=UserManager(),so it understant that User in model should be consider
        user = self.model(phone_number=phone_number,email=email,
                          full_name=full_name)
        #hash password and set
        user.set_password(password)
        #using to point running database
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email,full_name, password):
        user = self.create_user(phone_number,email,
                                full_name, password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
    @staticmethod
    def normalize_phone_number(phone_number, pattern=phone_regex):
        valid_phone = re.compile(pattern)
        if not valid_phone.match(phone_number):
            raise ValidationError("Phone number can be one of these forms: +989XXXXXXXXX | 09XXXXXXXXX")
        return phone_number
    
    @staticmethod
    def normalize_full_name(full_name, pattern=full_name_regex):
        valid_full_name = re.compile(pattern)
        if not valid_full_name.match(full_name):
            raise ValidationError("Invalid Full name. Full name must only contain alphabet letters and whitespace.")
        return full_name