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