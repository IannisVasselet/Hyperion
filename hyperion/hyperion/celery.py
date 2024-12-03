# hyperion/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyperion.settings')

app = Celery('hyperion')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'record-cpu-usage-every-minute': {
        'task': 'api.tasks.record_cpu_usage',
        'schedule': crontab(minute='*/1'),
    },
    'record-memory-usage-every-minute': {
        'task': 'api.tasks.record_memory_usage',
        'schedule': crontab(minute='*/1'),
    },
    'record-network-usage-every-minute': {
        'task': 'api.tasks.record_network_usage',
        'schedule': crontab(minute='*/1'),
    },
}