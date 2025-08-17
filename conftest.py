import os
import pytest
from django.conf import settings as django_settings

@pytest.fixture(autouse=True, scope='session')
def _configure_test_settings():
    # DB -> SQLite en mémoire pour les tests
    django_settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }

    # URLConf minimal pour éviter les imports Swagger/Jet
    django_settings.ROOT_URLCONF = 'api.urls'

    # Channel layer en mémoire (pas de Redis requis)
    django_settings.CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }

    # Email en mémoire
    django_settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

    # Slack webhook bidon
    django_settings.SLACK_WEBHOOK_URL = 'https://example.invalid/webhook'

    # Nettoyer INSTALLED_APPS des paquets tiers non nécessaires
    apps = list(django_settings.INSTALLED_APPS)
    for bogus in ['psutil', 'paramiko', 'jet.dashboard', 'jet', 'drf_yasg', 'corsheaders']:
        if bogus in apps:
            apps.remove(bogus)
    django_settings.INSTALLED_APPS = apps

    # Retirer les middlewares non nécessaires ou dépendants d'apps retirées
    middlewares = list(django_settings.MIDDLEWARE)
    for mw in [
        'api.middleware.AuthenticationMiddleware',
        'corsheaders.middleware.CorsMiddleware',
    ]:
        if mw in middlewares:
            middlewares.remove(mw)
    django_settings.MIDDLEWARE = middlewares

    # Two-factor: s'assurer du module settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyperion.settings')

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def user(db, django_user_model):
    user = django_user_model.objects.create_user(username='alice', password='secret123')
    return user

@pytest.fixture
def admin_user(db, django_user_model):
    """Fixture pour créer un utilisateur administrateur"""
    admin = django_user_model.objects.create_user(
        username='admin',
        password='admin123',
        email='admin@example.com',
        is_staff=True,
        is_superuser=True
    )
    # Créer le profil admin
    from api.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=admin)
    profile.is_admin = True
    profile.save()
    return admin

@pytest.fixture
def role(db):
    """Fixture pour créer un rôle de test"""
    from api.models import Role
    return Role.objects.create(
        name='test_role',
        permissions={
            'view_processes': True,
            'manage_processes': False,
            'view_services': True,
            'manage_services': True
        },
        description='Role for testing purposes'
    )

@pytest.fixture
def mock_process_data():
    """Données de processus simulées pour les tests"""
    return [
        {
            'pid': 1234,
            'name': 'test_process',
            'status': 'running',
            'cpu_percent': 15.5,
            'memory_percent': 8.2
        },
        {
            'pid': 5678,
            'name': 'another_process',
            'status': 'sleeping',
            'cpu_percent': 0.5,
            'memory_percent': 2.1
        }
    ]

@pytest.fixture
def mock_service_data():
    """Données de services simulées pour les tests"""
    return [
        {'name': 'nginx', 'status': 'active'},
        {'name': 'apache2', 'status': 'inactive'},
        {'name': 'mysql', 'status': 'failed'}
    ]

@pytest.fixture
def mock_storage_data():
    """Données de stockage simulées pour les tests"""
    return [
        {
            'device': '/dev/sda1',
            'mount_point': '/',
            'total': 1000000000,
            'used': 600000000,
            'free': 400000000,
            'percent_used': 60.0,
            'fs_type': 'ext4'
        },
        {
            'device': '/dev/sda2',
            'mount_point': '/home',
            'total': 500000000,
            'used': 200000000,
            'free': 300000000,
            'percent_used': 40.0,
            'fs_type': 'ext4'
        }
    ]
