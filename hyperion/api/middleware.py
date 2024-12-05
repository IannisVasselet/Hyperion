# api/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Paths that don't require authentication
        exempt_paths = [
            reverse('login'),
            reverse('2fa-verify'),
            '/admin/login/',
            '/static/',
        ]

        # Check if the path requires authentication
        requires_auth = not any(
            request.path.startswith(path) for path in exempt_paths
        )

        if requires_auth and not request.user.is_authenticated:
            return redirect('login')

        response = self.get_response(request)
        return response