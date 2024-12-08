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
    
class Role(models.Model):
    name = models.CharField(max_length=50)
    permissions = models.JSONField(default=dict)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    AVAILABLE_PERMISSIONS = {
        'view_processes': 'View system processes',
        'manage_processes': 'Manage system processes',
        'view_services': 'View system services',
        'manage_services': 'Manage system services',
        'view_files': 'View files',
        'manage_files': 'Manage files',
        'manage_network': 'Manage network settings',
        'manage_roles': 'Manage user roles',
        'manage_users': 'Manage users',
        'view_analytics': 'View system analytics'
    }

    def __str__(self):
        return self.name

    def has_permission(self, permission):
        return self.permissions.get(permission, False)
    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name

    @property
    def permission_list(self):
        return self.permissions.keys()
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=32, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create or get UserProfile when User is created"""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Get or create for existing users
        UserProfile.objects.get_or_create(user=instance)
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
        
class StorageUsage(models.Model):
    device = models.CharField(max_length=100)  # /dev/sda1, etc.
    mount_point = models.CharField(max_length=255)  # /, /home, etc.
    total = models.BigIntegerField()  # Total space in bytes
    used = models.BigIntegerField()  # Used space in bytes
    free = models.BigIntegerField()  # Free space in bytes
    percent_used = models.FloatField()  # Percentage used
    fs_type = models.CharField(max_length=50)  # ext4, ntfs, etc.
    recorded_at = models.DateTimeField(auto_now_add=True)