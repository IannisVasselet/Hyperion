# api/models.py
from django.db import models

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