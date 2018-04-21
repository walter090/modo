import datetime

from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _

from .managers import HumanManager
from . import auxiliary


class Human(AbstractBaseUser, PermissionsMixin):
    identifier = models.BigIntegerField(_('identifier'), unique=True,
                                        primary_key=True, default=auxiliary.make_id())
    email = models.EmailField(_('email address'), unique=True, null=False, blank=False)
    first_name = models.CharField(_('first name'), max_length=50, blank=True)
    last_name = models.CharField(_('last name'), max_length=50, blank=True)
    registered_since = models.DateField(_('registerd since'), default=datetime.date.today())
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    profile_pic = models.ImageField(_('profile picture'), upload_to='pic/',
                                    null=True, blank=True)

    USERNAME_FIELD = 'email'

    objects = HumanManager()

    def get_full_name(self):
        full_name = '{0} {1}'.format(self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name
