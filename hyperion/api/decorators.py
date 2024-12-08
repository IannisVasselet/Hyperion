# api/decorators.py
from functools import wraps
from django.core.exceptions import PermissionDenied

def require_permission(permission):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            
            user_profile = request.user.userprofile
            if not user_profile.role or permission not in user_profile.role.permissions:
                raise PermissionDenied
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator