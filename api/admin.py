from django.contrib import admin
from .models import Process, Service, Network, CPUUsage, MemoryUsage, NetworkUsage, UserProfile, AuditLog, BugReport

admin.site.register(Process)
admin.site.register(Service)
admin.site.register(Network)
admin.site.register(CPUUsage)
admin.site.register(MemoryUsage)
admin.site.register(NetworkUsage)
admin.site.register(UserProfile)
admin.site.register(AuditLog)

@admin.register(BugReport)
class BugReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'severity', 'status', 'module_affected', 'reported_by', 'assigned_to', 'created_at')
    list_filter = ('severity', 'status', 'module_affected', 'created_at')
    search_fields = ('title', 'description', 'module_affected')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'severity', 'status', 'module_affected')
        }),
        ('Détails techniques', {
            'fields': ('steps_to_reproduce', 'expected_behavior', 'actual_behavior', 'environment', 'logs')
        }),
        ('Attribution', {
            'fields': ('reported_by', 'assigned_to', 'resolution')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )