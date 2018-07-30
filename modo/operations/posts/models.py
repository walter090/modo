import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import JSONField

from modo.util import auxiliary
from .management import managers
from person.models import Human


class Post(models.Model):
    identifier = models.BigIntegerField(_('identifier'), unique=True,
                                        primary_key=True, default=auxiliary.make_id)
    title = models.TextField(_('title'))
    slug = models.SlugField(_('slug title'), max_length=200, null=True)
    author = models.ForeignKey('person.Human', on_delete=models.SET_NULL, null=True, related_name='posted')
    support = JSONField(_('support contributors'))

    drafted_at = models.DateTimeField(_('drafted_at'), default=datetime.datetime.utcnow)
    published_at = models.DateTimeField(_('published_at'), null=True)
    last_edition_at = models.DateTimeField(_('last_edited_at'), null=True)
    draft = models.BooleanField(_('is draft'), default=True)

    viewed_by = models.ManyToManyField(Human, related_name='viewed_posts')
    saved_by = models.ManyToManyField(Human, related_name='saved_posts')

    objects = managers.PostManager()

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    identifier = models.BigIntegerField(_('identifier'), unique=True,
                                        primary_key=True, default=auxiliary.make_id)
    author = models.ForeignKey('person.Human', on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
