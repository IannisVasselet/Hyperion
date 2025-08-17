# api/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse

from api.models import UserProfile

from rest_framework.authtoken.models import Token

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vérifier l'en-tête d'authentification pour les tokens
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Token '):
            token_key = auth_header.split(' ')[1]
            try:
                token = Token.objects.get(key=token_key)
                # Attacher l'utilisateur à la requête
                request.user = token.user
            except Token.DoesNotExist:
                pass
        # Paths that don't require authentication
        exempt_paths = [
            reverse('login'),
            reverse('2fa-verify'),
            '/admin/login/',
            '/static/',
            '/api/auth/api-login/',
        ]

        # Check if the path requires authentication
        requires_auth = not any(
            request.path.startswith(path) for path in exempt_paths
        )

        # Si authentification requise et utilisateur non authentifié
        if requires_auth and not request.user.is_authenticated:
            # Pour les requêtes API, renvoyer un JSON d'erreur plutôt qu'une redirection
            if request.path.startswith('/api/') and not request.path.startswith('/api/auth/'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Authentication required'
                }, status=401)
            # Pour les autres requêtes, redirection standard
            return redirect('login')

        response = self.get_response(request)
        return response

class RoleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                profile = request.user.userprofile
                request.user_role = profile.role
            except UserProfile.DoesNotExist:
                request.user_role = None
        return self.get_response(request)