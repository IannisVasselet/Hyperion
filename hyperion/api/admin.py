from django.contrib import admin
from .models import Process, Service, Network, CPUUsage, MemoryUsage, NetworkUsage, UserProfile, AuditLog

admin.site.register(Process)
admin.site.register(Service)
admin.site.register(Network)
admin.site.register(CPUUsage)
admin.site.register(MemoryUsage)
admin.site.register(NetworkUsage)
admin.site.register(UserProfile)
admin.site.register(AuditLog)