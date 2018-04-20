import datetime

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _

from .managers import HumanManager


class Human(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('Email address'), unique=True, null=False, blank=False,
                              primary_key=True)
    first_name = models.CharField(_('First name'), max_length=50, blank=True)
    last_name = models.CharField(_('Last name'), max_length=50, blank=True)
    registered_since = models.DateField(_('Registerd since'), default=datetime.date.today())
    is_active = models.BooleanField(_('Active'), default=True)
    is_staff = models.BooleanField(_('Staff status'), default=False)
    profile_pic = models.ImageField(_('Profile picture'), upload_to='pic/',
                                    null=True, blank=True)

    USERNAME_FIELD = 'email'

    objects = HumanManager()

    def get_full_name(self):
        full_name = '{0} {1}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name