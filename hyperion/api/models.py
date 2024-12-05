# api/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Process(models.Model):
    name = models.CharField(max_length=100)
    pid = models.IntegerField()
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class Service(models.Model):
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class Network(models.Model):
    interface = models.CharField(max_length=100)
    received = models.BigIntegerField()
    sent = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

class CPUUsage(models.Model):
    usage = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)

class MemoryUsage(models.Model):
    usage = models.FloatField()
    recorded_at = models.DateTimeField(auto_now_add=True)

class NetworkUsage(models.Model):
    interface = models.CharField(max_length=100)
    received = models.BigIntegerField()
    sent = models.BigIntegerField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    
class FileSystem(models.Model):
    path = models.CharField(max_length=255)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20)  # 'file' or 'directory'
    size = models.BigIntegerField()
    modified_at = models.DateTimeField()
    permissions = models.CharField(max_length=10)
    owner = models.CharField(max_length=50)
    group = models.CharField(max_length=50)
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('failed_login', 'Failed Login'),
        ('2fa_setup', '2FA Setup'),
        ('2fa_disable', '2FA Disable'),
        ('process_stop', 'Process Stop'),
        ('service_control', 'Service Control'),
    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.TextField()
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']