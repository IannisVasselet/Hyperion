# api/tasks.py
from celery import shared_task
from .models import CPUUsage, MemoryUsage, NetworkUsage, StorageUsage
from .utils import get_storage_info
import psutil
import requests
from django.conf import settings

@shared_task
def record_cpu_usage():
    usage = psutil.cpu_percent(interval=1)
    CPUUsage.objects.create(usage=usage)

@shared_task
def record_memory_usage():
    usage = psutil.virtual_memory().percent
    MemoryUsage.objects.create(usage=usage)

@shared_task
def record_network_usage():
    for interface, stats in psutil.net_io_counters(pernic=True).items():
        NetworkUsage.objects.create(
            interface=interface,
            received=stats.bytes_recv,
            sent=stats.bytes_sent
        )

@shared_task
def send_slack_notification(message):
    webhook_url = settings.SLACK_WEBHOOK_URL
    payload = {'text': message}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, json=payload, headers=headers)
    return response.status_code

@shared_task
def send_email_notification(subject, message, recipient_list):
    from django.core.mail import send_mail
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
    
@shared_task
def record_cpu_usage():
    usage = psutil.cpu_percent(interval=1)
    CPUUsage.objects.create(usage=usage)
    
@shared_task
def record_storage_usage():
    for info in get_storage_info():
        StorageUsage.objects.create(**info)