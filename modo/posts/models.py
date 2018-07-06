from django.db import models
from django.utils.translation import ugettext_lazy as _

from modo.util import auxiliary


class Post(models.Model):
    identifier = models.BigIntegerField(_('identifier'), unique=True,
                                        primary_key=True, default=auxiliary.make_id)
