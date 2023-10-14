from datetime import datetime

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, username=None, **extra_fields):
        """
		Creates and saves a User with the given email and password.
		"""
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            username=self.normalize_email(email), **extra_fields)

        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)

        return user

    def create_staffuser(self, email, password, **extra_fields):
        """
		Creates and saves a staff user with the given email and password.
		"""

        extra_fields.setdefault('is_staff', True)
        user = self.create_user(email, password=password, username=email, **extra_fields)
        user.is_active = True
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """
		Creates and saves a superuser with the given email and password.
		"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        user = self.create_user(email, password=password, username=email, **extra_fields)
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user


AUTH_PROVIDERS = {'google': 'google', 'email': 'email', 'microsoft': 'microsoft'}


Doctor, Nurse, Patient, Pharmacist, Management, Staff = range(6)
USER_ROLES = (
    (Doctor, "Doctor"), (Nurse, 'Nurse'), (Patient, 'Patient'), (Management, 'Management'),
    (Staff, 'Staff')
)


class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True, help_text="The user's email address")
    hospital = models.ForeignKey('tenants.Hospital', default=None, null=True, on_delete=models.CASCADE,
                                 help_text="The user's hosptal")
    mobile = models.CharField(max_length=30, default=None, null=True, help_text="The user's mobile number")
    mobiles = ArrayField(base_field=models.JSONField(default=dict), default=list, null=True, blank=True,
                         help_text="The list of a user's mobile numbers")
    is_active = models.BooleanField(default=False, help_text="shows if a user is active or archived")
    roles = ArrayField(base_field=models.PositiveSmallIntegerField(choices=USER_ROLES, default=None), default=list)
    auth_provider = models.CharField(
        max_length=255, blank=False,
        null=False, default=AUTH_PROVIDERS.get('email'),
        help_text="The auth provider through which this user signed up")
    city = models.CharField(max_length=70, default=None, null=True, help_text="The user's city of residence")
    country = models.CharField(max_length=70, default=None, null=True, help_text="The user's country of residence")
    timezone = models.CharField(max_length=30, default=None, null=True, help_text="The user's timezone")
    deletion_date = models.DateField(null=True, blank=True, default=None,
                                     help_text="The date at which this user will be deleted")


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email & Password are required by default.

    objects = UserManager()

    def __str__(self):
        return self.email

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def make_primary_contact(self, type_: str, contact_: str):
        list_ = self.emails if type_ == 'email' else self.mobiles
        list_ = list_ if list_ is not None else []
        new_contact = None
        for contact in list_:
            contact['primary'] = False
            if contact[type_] == contact_:
                new_contact = contact
                break
        list_.remove(new_contact)
        if new_contact is not None:
            new_contact['primary'] = True
            list_.insert(0, new_contact)
        if type_ == 'email':
            self.emails = list_
        else:
            self.mobiles = list_
        self.save()

    def add_new_contact(self, type_: str, contact_: str):
        data = {type_: contact_, "primary": False, "date_created": datetime.now().__str__()}
        list_ = self.emails if type_ == 'email' else self.mobiles
        list_ = list_ if list_ is not None else []
        list_.append(data)
        if type_ == 'email':
            self.emails = list_
            if self.email is None:
                self.email = contact_
            self.save()

        elif type_ == 'mobile':
            self.mobiles = list_
            if self.mobile is None:
                self.mobile = contact_
            self.save()

    def update_contact(self, type_: str, old_contact_: str, new_contact_: str):
        list_ = self.emails if type_ == 'email' else self.mobiles
        list_ = list_ if list_ is not None else []
        data = [contact for contact in list_ if contact[type_] == old_contact_][0]
        data_index = list_.index(data)
        new_data = data
        new_data[type_] = new_contact_
        list_.remove(data)
        list_.insert(data_index, new_data)
        if type_ == 'email':
            self.emails = list_
        else:
            self.mobiles = list_
        self.save()

    def delete_contact(self, type_: str, contact_: str):
        list_ = self.emails if type_ == 'email' else self.mobiles
        list_ = list_ if list_ is not None else []
        data = [contact for contact in list_ if contact[type_] == contact_][0]
        list_.remove(data)
        if type_ == 'email':
            self.emails = list_
        else:
            self.mobiles = list_
        self.save()

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def login_info_list(self):
        return LoginInformation.objects.filter(user=self).order_by('-login_date')


class LoginInformation(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    ip_address = models.GenericIPAddressField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, default=0.0)
    country = models.CharField(max_length=20, default="")
    city = models.CharField(max_length=20, default="")
    login_date = models.DateTimeField()
    logout_date = models.DateTimeField(null=True)
    browser_name = models.CharField(max_length=50)
    os = models.CharField(max_length=50)
    device_type = models.CharField(max_length=20, default="")
    locked = models.BooleanField(default=False)
