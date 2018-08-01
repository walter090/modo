import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'modo.settings')

app = Celery('modo')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'pull_articles': {
        'task': 'modo.news.management.tasks.pull_articles',
        'schedule': crontab(hour='*/2')
    },
    'update_sources': {
        'task': 'modo.news.management.tasks.update_sources',
        'schedule': crontab(day_of_month=1)
    },
    'show_time': {
        'task': 'modo.news.management.tasks.show_time',
        'schedule': 10
    },
}
