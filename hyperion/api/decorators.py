# api/decorators.py
from functools import wraps
from django.core.exceptions import PermissionDenied
from .models import AuditLog, UserProfile

def require_permission(permission):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            
            try:
                profile = request.user.userprofile
                if not profile.role:
                    AuditLog.objects.create(
                        user=request.user,
                        action='permission_denied',
                        details=f'No role assigned'
                    )
                    raise PermissionDenied
                    
                if not profile.role.has_permission(permission):
                    AuditLog.objects.create(
                        user=request.user,
                        action='permission_denied',
                        details=f'Access denied to {permission}'
                    )
                    raise PermissionDenied
                
                AuditLog.objects.create(
                    user=request.user,
                    action='permission_granted',
                    details=f'Access granted to {permission}'
                )
                    
                return view_func(request, *args, **kwargs)
            except UserProfile.DoesNotExist:
                raise PermissionDenied
                
        return _wrapped_view
    return decorator