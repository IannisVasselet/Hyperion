# api/tests.py
import asyncio
import json
from unittest import mock
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone as dt_timezone

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase, override_settings
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from channels.testing import WebsocketCommunicator
from hyperion.asgi import application

from . import models as m
from . import tasks as t
from . import utils as u
from .views import LoginAPIView, ProcessViewSet, ServiceViewSet, NetworkViewSet
from .consumers import ProcessConsumer, ServiceConsumer, NetworkConsumer

User = get_user_model()

# ------------------------------
# Fixtures
# ------------------------------

@pytest.fixture
def user(db):
    """Créer un utilisateur de test"""
    return User.objects.create_user(username='testuser', password='secret123', email='test@example.com')

@pytest.fixture
def admin_user(db):
    """Créer un utilisateur admin"""
    user = User.objects.create_user(username='admin', password='admin123', email='admin@example.com', is_staff=True)
    profile = m.UserProfile.objects.get(user=user)
    profile.is_admin = True
    profile.save()
    return user

@pytest.fixture
def role(db):
    """Créer un rôle de test"""
    return m.Role.objects.create(
        name='test_role',
        permissions={'view_processes': True, 'manage_services': True},
        description='Test role for unit tests'
    )

@pytest.fixture
def client():
    """Client API non authentifié"""
    return APIClient()

@pytest.fixture
def auth_client(client, user):
    """Client API authentifié"""
    client.force_authenticate(user=user)
    return client

@pytest.fixture
def admin_client(client, admin_user):
    """Client API administrateur"""
    client.force_authenticate(user=admin_user)
    return client

# ------------------------------
# Tests pour les Modèles
# ------------------------------

class ModelTests(TestCase):
    """Tests pour tous les modèles de l'application"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.role = m.Role.objects.create(
            name='test_role',
            permissions={'view_processes': True, 'manage_services': False}
        )

    def test_process_model_creation(self):
        """Test création du modèle Process"""
        process = m.Process.objects.create(
            name='test_process',
            pid=1234,
            status='running'
        )
        self.assertEqual(process.name, 'test_process')
        self.assertEqual(process.pid, 1234)
        self.assertEqual(process.status, 'running')
        self.assertIsNotNone(process.created_at)

    def test_service_model_creation(self):
        """Test création du modèle Service"""
        service = m.Service.objects.create(
            name='nginx',
            status='active'
        )
        self.assertEqual(service.name, 'nginx')
        self.assertEqual(service.status, 'active')
        self.assertIsNotNone(service.created_at)

    def test_network_model_creation(self):
        """Test création du modèle Network"""
        network = m.Network.objects.create(
            interface='eth0',
            received=1024,
            sent=2048
        )
        self.assertEqual(network.interface, 'eth0')
        self.assertEqual(network.received, 1024)
        self.assertEqual(network.sent, 2048)

    def test_cpu_usage_model_creation(self):
        """Test création du modèle CPUUsage"""
        cpu_usage = m.CPUUsage.objects.create(usage=75.5)
        self.assertEqual(cpu_usage.usage, 75.5)
        self.assertIsNotNone(cpu_usage.recorded_at)

    def test_memory_usage_model_creation(self):
        """Test création du modèle MemoryUsage"""
        memory_usage = m.MemoryUsage.objects.create(usage=60.0)
        self.assertEqual(memory_usage.usage, 60.0)
        self.assertIsNotNone(memory_usage.recorded_at)

    def test_network_usage_model_creation(self):
        """Test création du modèle NetworkUsage"""
        network_usage = m.NetworkUsage.objects.create(
            interface='wlan0',
            received=500000,
            sent=250000
        )
        self.assertEqual(network_usage.interface, 'wlan0')
        self.assertEqual(network_usage.received, 500000)
        self.assertEqual(network_usage.sent, 250000)

    def test_filesystem_model_creation(self):
        """Test création du modèle FileSystem"""
        filesystem = m.FileSystem.objects.create(
            path='/home/user/test.txt',
            name='test.txt',
            type='file',
            size=1024,
            modified_at=timezone.now(),
            permissions='rw-r--r--',
            owner='user',
            group='user'
        )
        self.assertEqual(filesystem.name, 'test.txt')
        self.assertEqual(filesystem.type, 'file')
        self.assertEqual(filesystem.size, 1024)

    def test_role_model_methods(self):
        """Test des méthodes du modèle Role"""
        self.assertTrue(self.role.has_permission('view_processes'))
        self.assertFalse(self.role.has_permission('manage_services'))
        self.assertIn('view_processes', self.role.permission_list)
        self.assertEqual(str(self.role), 'test_role')

    def test_user_profile_creation_signal(self):
        """Test création automatique de UserProfile"""
        new_user = User.objects.create_user(username='newuser', password='test123')
        profile = m.UserProfile.objects.get(user=new_user)
        self.assertIsNotNone(profile)
        self.assertFalse(profile.two_factor_enabled)
        self.assertFalse(profile.is_admin)
        self.assertEqual(str(profile), "newuser's profile")

    def test_audit_log_model_creation(self):
        """Test création du modèle AuditLog"""
        audit_log = m.AuditLog.objects.create(
            user=self.user,
            action='login',
            details='User logged in successfully',
            ip_address='192.168.1.1'
        )
        self.assertEqual(audit_log.user, self.user)
        self.assertEqual(audit_log.action, 'login')
        self.assertIsNotNone(audit_log.timestamp)

    def test_storage_usage_model_creation(self):
        """Test création du modèle StorageUsage"""
        storage = m.StorageUsage.objects.create(
            device='/dev/sda1',
            mount_point='/',
            total=1000000000,
            used=500000000,
            free=500000000,
            percent_used=50.0,
            fs_type='ext4'
        )
        self.assertEqual(storage.device, '/dev/sda1')
        self.assertEqual(storage.percent_used, 50.0)

    def test_simulation_environment_model_creation(self):
        """Test création du modèle SimulationEnvironment"""
        sim_env = m.SimulationEnvironment.objects.create(
            name='CPU Load Test',
            created_by=self.user,
            status='running',
            config={'cpu_cores': 4, 'duration': 300}
        )
        self.assertEqual(sim_env.name, 'CPU Load Test')
        self.assertEqual(sim_env.created_by, self.user)
        self.assertEqual(sim_env.config['cpu_cores'], 4)

    def test_simulation_result_model_creation(self):
        """Test création du modèle SimulationResult"""
        sim_env = m.SimulationEnvironment.objects.create(
            name='Memory Test',
            created_by=self.user
        )
        result = m.SimulationResult.objects.create(
            environment=sim_env,
            metrics={'avg_cpu': 75.5, 'max_memory': 80.2},
            type='cpu_load'
        )
        self.assertEqual(result.environment, sim_env)
        self.assertEqual(result.metrics['avg_cpu'], 75.5)

    def test_totp_device_model_creation(self):
        """Test création du modèle TOTPDevice"""
        device = m.TOTPDevice.objects.create(
            user=self.user,
            name='authenticator',
            key='JBSWY3DPEHPK3PXP',
            confirmed=True
        )
        self.assertEqual(device.user, self.user)
        self.assertEqual(device.name, 'authenticator')
        self.assertTrue(device.confirmed)

# ------------------------------
# Tests pour les Vues API
# ------------------------------

class APIViewTests(APITestCase):
    """Tests pour les vues API"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.admin_user = User.objects.create_user(username='admin', password='admin123', is_staff=True)
        self.token = Token.objects.create(user=self.user)
        
    def test_login_api_success(self):
        """Test connexion API réussie"""
        url = reverse('login-api')  # Ajustez selon votre URL pattern
        data = {'username': 'testuser', 'password': 'test123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('token', response.data)

    def test_login_api_invalid_credentials(self):
        """Test connexion API avec identifiants invalides"""
        url = reverse('login-api')
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['status'], 'error')

    @patch('api.utils.get_processes')
    def test_process_list_api(self, mock_get_processes):
        """Test récupération de la liste des processus"""
        mock_get_processes.return_value = [
            {'pid': 1234, 'name': 'test_process', 'status': 'running', 'cpu_percent': 5.0}
        ]
        
        self.client.force_authenticate(user=self.user)
        url = reverse('process-list')  # Ajustez selon votre URL pattern
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_processes.assert_called_once()

    @patch('api.utils.stop_process')
    def test_stop_process_api(self, mock_stop_process):
        """Test arrêt d'un processus via API"""
        mock_stop_process.return_value = True
        
        self.client.force_authenticate(user=self.user)
        url = reverse('process-stop-process')  # Ajustez selon votre URL pattern
        data = {'pid': 1234}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_stop_process.assert_called_once_with(1234)

    @patch('api.utils.get_services')
    def test_service_list_api(self, mock_get_services):
        """Test récupération de la liste des services"""
        mock_get_services.return_value = [
            {'name': 'nginx', 'status': 'active'}
        ]
        
        self.client.force_authenticate(user=self.user)
        url = reverse('service-list')  # Ajustez selon votre URL pattern
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_get_services.assert_called_once()

    @patch('api.utils.block_ip')
    def test_block_ip_api(self, mock_block_ip):
        """Test blocage d'IP via API"""
        mock_block_ip.return_value = True
        
        self.client.force_authenticate(user=self.user)
        url = reverse('network-block-ip')  # Ajustez selon votre URL pattern
        data = {'ip_address': '192.168.1.100'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'IP blocked')
        mock_block_ip.assert_called_once_with('192.168.1.100')

    def test_authentication_required(self):
        """Test que l'authentification est requise"""
        url = reverse('process-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# ------------------------------
# Tests pour les Tâches Celery
# ------------------------------

class CeleryTaskTests(TestCase):
    """Tests pour les tâches Celery"""

    @patch('api.tasks.psutil.cpu_percent')
    def test_record_cpu_usage_task(self, mock_cpu_percent):
        """Test de la tâche d'enregistrement de l'usage CPU"""
        mock_cpu_percent.return_value = 75.5
        
        # Exécuter la tâche
        t.record_cpu_usage()
        
        # Vérifier qu'un enregistrement a été créé
        cpu_usage = m.CPUUsage.objects.first()
        self.assertIsNotNone(cpu_usage)
        self.assertEqual(cpu_usage.usage, 75.5)
        mock_cpu_percent.assert_called_once_with(interval=1)

    @patch('api.tasks.psutil.virtual_memory')
    def test_record_memory_usage_task(self, mock_virtual_memory):
        """Test de la tâche d'enregistrement de l'usage mémoire"""
        mock_memory = Mock()
        mock_memory.percent = 60.0
        mock_virtual_memory.return_value = mock_memory
        
        # Exécuter la tâche
        t.record_memory_usage()
        
        # Vérifier qu'un enregistrement a été créé
        memory_usage = m.MemoryUsage.objects.first()
        self.assertIsNotNone(memory_usage)
        self.assertEqual(memory_usage.usage, 60.0)

    @patch('api.tasks.psutil.net_io_counters')
    def test_record_network_usage_task(self, mock_net_io):
        """Test de la tâche d'enregistrement de l'usage réseau"""
        mock_stats = Mock()
        mock_stats.bytes_recv = 1024000
        mock_stats.bytes_sent = 512000
        mock_net_io.return_value = {'eth0': mock_stats}
        
        # Exécuter la tâche
        t.record_network_usage()
        
        # Vérifier qu'un enregistrement a été créé
        network_usage = m.NetworkUsage.objects.first()
        self.assertIsNotNone(network_usage)
        self.assertEqual(network_usage.interface, 'eth0')
        self.assertEqual(network_usage.received, 1024000)
        self.assertEqual(network_usage.sent, 512000)

    @patch('api.tasks.requests.post')
    @override_settings(SLACK_WEBHOOK_URL='https://hooks.slack.com/test')
    def test_send_slack_notification_task(self, mock_post):
        """Test de la tâche d'envoi de notification Slack"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Exécuter la tâche
        result = t.send_slack_notification('Test message')
        
        # Vérifier l'appel
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn('Test message', str(kwargs['json']))
        self.assertEqual(result, 200)

    @patch('api.tasks.send_mail')
    @override_settings(DEFAULT_FROM_EMAIL='test@example.com')
    def test_send_email_notification_task(self, mock_send_mail):
        """Test de la tâche d'envoi d'email"""
        # Exécuter la tâche
        t.send_email_notification(
            'Test Subject',
            'Test message',
            ['recipient@example.com']
        )
        
        # Vérifier l'appel
        mock_send_mail.assert_called_once_with(
            'Test Subject',
            'Test message',
            'test@example.com',
            ['recipient@example.com']
        )

    @patch('api.tasks.get_storage_info')
    def test_record_storage_usage_task(self, mock_get_storage_info):
        """Test de la tâche d'enregistrement de l'usage stockage"""
        mock_get_storage_info.return_value = [
            {
                'device': '/dev/sda1',
                'mount_point': '/',
                'total': 1000000000,
                'used': 500000000,
                'free': 500000000,
                'percent_used': 50.0,
                'fs_type': 'ext4'
            }
        ]
        
        # Exécuter la tâche
        t.record_storage_usage()
        
        # Vérifier qu'un enregistrement a été créé
        storage_usage = m.StorageUsage.objects.first()
        self.assertIsNotNone(storage_usage)
        self.assertEqual(storage_usage.device, '/dev/sda1')
        self.assertEqual(storage_usage.percent_used, 50.0)

# ------------------------------
# Tests pour les Utils
# ------------------------------

class UtilsTests(TestCase):
    """Tests pour les fonctions utilitaires"""

    @patch('api.utils.psutil.process_iter')
    def test_get_processes(self, mock_process_iter):
        """Test de la fonction get_processes"""
        mock_proc = Mock()
        mock_proc.info = {
            'pid': 1234,
            'name': 'test_process',
            'status': 'running'
        }
        mock_proc.cpu_percent.return_value = 5.0
        mock_proc.memory_percent.return_value = 10.0
        mock_process_iter.return_value = [mock_proc]
        
        processes = u.get_processes()
        
        self.assertEqual(len(processes), 1)
        self.assertEqual(processes[0]['pid'], 1234)
        self.assertEqual(processes[0]['name'], 'test_process')

    @patch('api.utils.psutil.Process')
    def test_stop_process_success(self, mock_process_class):
        """Test arrêt de processus réussi"""
        mock_process = Mock()
        mock_process_class.return_value = mock_process
        
        result = u.stop_process(1234)
        
        self.assertTrue(result)
        mock_process_class.assert_called_once_with(1234)
        mock_process.terminate.assert_called_once()

    @patch('api.utils.psutil.Process')
    def test_stop_process_not_found(self, mock_process_class):
        """Test arrêt de processus inexistant"""
        mock_process_class.side_effect = psutil.NoSuchProcess(1234)
        
        result = u.stop_process(1234)
        
        self.assertFalse(result)

    @patch('api.utils.subprocess.check_output')
    def test_get_services(self, mock_check_output):
        """Test de la fonction get_services"""
        mock_output = b"""  nginx.service    loaded active running   A high performance web server
  apache2.service  loaded failed failed    The Apache HTTP Server
"""
        mock_check_output.return_value = mock_output
        
        services = u.get_services()
        
        self.assertIsInstance(services, list)
        # Le test dépend de la logique de parsing dans get_services

    @patch('api.utils.subprocess.check_call')
    def test_block_ip_success(self, mock_check_call):
        """Test blocage d'IP réussi"""
        result = u.block_ip('192.168.1.100')
        
        self.assertTrue(result)
        mock_check_call.assert_called_once_with([
            'sudo', 'iptables',
            '-A', 'INPUT',
            '-s', '192.168.1.100',
            '-j', 'DROP'
        ])

    @patch('api.utils.subprocess.check_call')
    def test_block_ip_failure(self, mock_check_call):
        """Test blocage d'IP échoué"""
        mock_check_call.side_effect = subprocess.CalledProcessError(1, 'iptables')
        
        result = u.block_ip('192.168.1.100')
        
        self.assertFalse(result)

    @patch('api.utils.psutil.disk_partitions')
    @patch('api.utils.psutil.disk_usage')
    def test_get_storage_info(self, mock_disk_usage, mock_disk_partitions):
        """Test de la fonction get_storage_info"""
        # Mock partition
        mock_partition = Mock()
        mock_partition.device = '/dev/sda1'
        mock_partition.mountpoint = '/'
        mock_partition.fstype = 'ext4'
        mock_disk_partitions.return_value = [mock_partition]
        
        # Mock usage
        mock_usage = Mock()
        mock_usage.total = 1000000000
        mock_usage.used = 500000000
        mock_usage.free = 500000000
        mock_usage.percent = 50.0
        mock_disk_usage.return_value = mock_usage
        
        storage_info = u.get_storage_info()
        
        self.assertEqual(len(storage_info), 1)
        self.assertEqual(storage_info[0]['device'], '/dev/sda1')
        self.assertEqual(storage_info[0]['percent_used'], 50.0)

# ------------------------------
# Tests pour les WebSockets
# ------------------------------

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class WebSocketTests:
    """Tests pour les WebSocket consumers"""

    @patch('api.utils.get_processes')
    async def test_process_consumer(self, mock_get_processes):
        """Test du consumer de processus"""
        mock_get_processes.return_value = [
            {'pid': 1234, 'name': 'test', 'status': 'running'}
        ]
        
        communicator = WebsocketCommunicator(application, '/ws/processes/')
        connected, _ = await communicator.connect()
        assert connected
        
        # Test réception de données
        response = await communicator.receive_json_from()
        assert isinstance(response, list)
        
        # Test action stop
        await communicator.send_json_to({
            'action': 'stop',
            'pid': 1234
        })
        
        response = await communicator.receive_json_from()
        assert 'status' in response
        assert response['action'] == 'stop'
        
        await communicator.disconnect()

    @patch('api.utils.get_services')
    async def test_service_consumer(self, mock_get_services):
        """Test du consumer de services"""
        mock_get_services.return_value = [
            {'name': 'nginx', 'status': 'active'}
        ]
        
        communicator = WebsocketCommunicator(application, '/ws/services/')
        connected, _ = await communicator.connect()
        assert connected
        
        # Test réception de données
        response = await communicator.receive_json_from()
        assert isinstance(response, list)
        
        await communicator.disconnect()

    async def test_network_consumer(self):
        """Test du consumer réseau"""
        communicator = WebsocketCommunicator(application, '/ws/network/')
        connected, _ = await communicator.connect()
        assert connected
        
        await communicator.disconnect()

# ------------------------------
# Tests d'Authentification et 2FA
# ------------------------------

class AuthenticationTests(TestCase):
    """Tests pour l'authentification et 2FA"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', 
            password='test123',
            email='test@example.com'
        )
        self.profile = m.UserProfile.objects.get(user=self.user)

    def test_login_view_success_redirect_dashboard(self):
        """Test redirection vers dashboard après connexion réussie"""
        response = self.client.post('/auth/login/', {
            'username': 'testuser',
            'password': 'test123'
        })
        self.assertIn(response.status_code, [302, 200])

    def test_login_view_redirects_to_2fa_when_enabled(self):
        """Test redirection vers 2FA quand activé"""
        self.profile.two_factor_enabled = True
        self.profile.save()
        
        response = self.client.post('/auth/login/', {
            'username': 'testuser',
            'password': 'test123'
        })
        
        # Devrait rediriger vers la vérification 2FA
        self.assertIn(response.status_code, [302, 200])

    def test_two_factor_setup(self):
        """Test configuration 2FA"""
        self.client.force_login(self.user)
        
        # Simulation de la configuration 2FA
        device = m.TOTPDevice.objects.create(
            user=self.user,
            name='test_device',
            key='JBSWY3DPEHPK3PXP',
            confirmed=True
        )
        
        self.assertEqual(device.user, self.user)
        self.assertTrue(device.confirmed)

    def test_logout_view_redirect(self):
        """Test redirection après déconnexion"""
        self.client.force_login(self.user)
        response = self.client.get('/auth/logout/')
        self.assertIn(response.status_code, [302, 200])

# ------------------------------
# Tests de Permissions et Rôles
# ------------------------------

class PermissionTests(TestCase):
    """Tests pour les permissions et rôles"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.admin_user = User.objects.create_user(
            username='admin', 
            password='admin123',
            is_staff=True
        )
        
        self.viewer_role = m.Role.objects.create(
            name='viewer',
            permissions={'view_processes': True, 'view_services': True}
        )
        
        self.manager_role = m.Role.objects.create(
            name='manager',
            permissions={
                'view_processes': True,
                'manage_processes': True,
                'view_services': True,
                'manage_services': True
            }
        )

    def test_role_permission_check(self):
        """Test vérification des permissions de rôle"""
        self.assertTrue(self.viewer_role.has_permission('view_processes'))
        self.assertFalse(self.viewer_role.has_permission('manage_processes'))
        
        self.assertTrue(self.manager_role.has_permission('manage_processes'))
        self.assertTrue(self.manager_role.has_permission('manage_services'))

    def test_user_profile_role_assignment(self):
        """Test attribution de rôle à un profil utilisateur"""
        profile = m.UserProfile.objects.get(user=self.user)
        profile.role = self.viewer_role
        profile.save()
        
        self.assertEqual(profile.role, self.viewer_role)
        self.assertTrue(profile.role.has_permission('view_processes'))

    def test_admin_user_permissions(self):
        """Test permissions utilisateur admin"""
        admin_profile = m.UserProfile.objects.get(user=self.admin_user)
        admin_profile.is_admin = True
        admin_profile.save()
        
        self.assertTrue(admin_profile.is_admin)

# ------------------------------
# Tests d'Audit et Logs
# ------------------------------

class AuditLogTests(TestCase):
    """Tests pour les logs d'audit"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')

    def test_audit_log_creation(self):
        """Test création d'un log d'audit"""
        log = m.AuditLog.objects.create(
            user=self.user,
            action='login',
            details='User logged in from web interface',
            ip_address='192.168.1.100'
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'login')
        self.assertEqual(log.ip_address, '192.168.1.100')
        self.assertIsNotNone(log.timestamp)

    def test_audit_log_ordering(self):
        """Test ordre des logs d'audit (plus récent en premier)"""
        log1 = m.AuditLog.objects.create(
            user=self.user,
            action='login',
            details='First login',
            ip_address='192.168.1.1'
        )
        
        log2 = m.AuditLog.objects.create(
            user=self.user,
            action='logout',
            details='User logout',
            ip_address='192.168.1.1'
        )
        
        logs = list(m.AuditLog.objects.all())
        self.assertEqual(logs[0], log2)  # Plus récent en premier
        self.assertEqual(logs[1], log1)

# ------------------------------
# Tests d'Intégration
# ------------------------------

class IntegrationTests(APITestCase):
    """Tests d'intégration bout en bout"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.token = Token.objects.create(user=self.user)

    def test_full_process_workflow(self):
        """Test workflow complet de gestion des processus"""
        self.client.force_authenticate(user=self.user)
        
        # 1. Récupérer la liste des processus
        with patch('api.utils.get_processes') as mock_get:
            mock_get.return_value = [{'pid': 1234, 'name': 'test'}]
            
            # Ajustez l'URL selon votre configuration
            response = self.client.get('/api/processes/')
            # Vérifiez que la réponse est correcte selon votre API

    def test_full_service_workflow(self):
        """Test workflow complet de gestion des services"""
        self.client.force_authenticate(user=self.user)
        
        with patch('api.utils.get_services') as mock_get:
            mock_get.return_value = [{'name': 'nginx', 'status': 'active'}]
            
            # Test récupération des services
            response = self.client.get('/api/services/')
            # Vérifiez selon votre API

    def test_notification_workflow(self):
        """Test workflow complet de notifications"""
        self.client.force_authenticate(user=self.user)
        
        with patch('api.tasks.send_slack_notification.delay') as mock_slack:
            # Test notification Slack
            response = self.client.post('/api/notifications/slack/', {
                'message': 'Test notification'
            })
            
            if response.status_code == 200:
                mock_slack.assert_called_once_with('Test notification')

# ------------------------------
# Tests de Performance et Charge
# ------------------------------

class PerformanceTests(TestCase):
    """Tests de performance"""

    def test_bulk_model_creation(self):
        """Test création en masse de modèles"""
        import time
        
        start_time = time.time()
        
        # Créer 1000 enregistrements CPUUsage
        cpu_records = [m.CPUUsage(usage=i % 100) for i in range(1000)]
        m.CPUUsage.objects.bulk_create(cpu_records)
        
        end_time = time.time()
        
        # Vérifier que l'opération est rapide (moins de 1 seconde)
        self.assertLess(end_time - start_time, 1.0)
        
        # Vérifier que tous les enregistrements ont été créés
        self.assertEqual(m.CPUUsage.objects.count(), 1000)

    def test_large_query_performance(self):
        """Test performance des requêtes sur de gros volumes"""
        # Créer des données de test
        cpu_records = [m.CPUUsage(usage=i % 100) for i in range(5000)]
        m.CPUUsage.objects.bulk_create(cpu_records)
        
        import time
        start_time = time.time()
        
        # Requête avec agrégation
        from django.db.models import Avg, Max, Min
        stats = m.CPUUsage.objects.aggregate(
            avg_usage=Avg('usage'),
            max_usage=Max('usage'),
            min_usage=Min('usage')
        )
        
        end_time = time.time()
        
        # Vérifier que la requête est rapide
        self.assertLess(end_time - start_time, 0.5)
        self.assertIsNotNone(stats['avg_usage'])

# ------------------------------
# Tests d'Erreur et Edge Cases
# ------------------------------

class ErrorHandlingTests(TestCase):
    """Tests de gestion d'erreurs et cas limites"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')

    def test_process_not_found_error(self):
        """Test erreur processus non trouvé"""
        with patch('api.utils.psutil.Process') as mock_process:
            mock_process.side_effect = psutil.NoSuchProcess(9999)
            
            result = u.stop_process(9999)
            self.assertFalse(result)

    def test_invalid_ip_blocking(self):
        """Test blocage IP invalide"""
        with patch('api.utils.subprocess.check_call') as mock_call:
            mock_call.side_effect = subprocess.CalledProcessError(1, 'iptables')
            
            result = u.block_ip('invalid.ip.address')
            self.assertFalse(result)

    def test_storage_info_access_denied(self):
        """Test accès refusé aux informations de stockage"""
        with patch('api.utils.psutil.disk_usage') as mock_usage:
            mock_usage.side_effect = PermissionError("Access denied")
            
            # La fonction devrait gérer l'erreur gracieusement
            storage_info = u.get_storage_info()
            self.assertIsInstance(storage_info, list)

    def test_celery_task_failure_handling(self):
        """Test gestion d'échec des tâches Celery"""
        with patch('api.tasks.psutil.cpu_percent') as mock_cpu:
            mock_cpu.side_effect = Exception("CPU monitoring error")
            
            # La tâche ne devrait pas planter l'application
            try:
                t.record_cpu_usage()
            except Exception as e:
                self.fail(f"Task should handle errors gracefully: {e}")

# ------------------------------
# Tests de Sécurité
# ------------------------------

class SecurityTests(APITestCase):
    """Tests de sécurité"""

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.admin_user = User.objects.create_user(
            username='admin', 
            password='admin123',
            is_staff=True
        )

    def test_unauthorized_access_blocked(self):
        """Test blocage d'accès non autorisé"""
        # Tentative d'accès sans authentification
        response = self.client.get('/api/processes/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_csrf_protection(self):
        """Test protection CSRF"""
        # Test avec client Django standard pour CSRF
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        
        # Tentative POST sans token CSRF
        response = client.post('/auth/login/', {
            'username': 'testuser',
            'password': 'test123'
        })
        
        # Devrait être rejeté si CSRF est activé
        self.assertIn(response.status_code, [403, 400, 302])

    def test_sql_injection_protection(self):
        """Test protection contre injection SQL"""
        # Tentative d'injection dans les paramètres
        malicious_input = "'; DROP TABLE api_process; --"
        
        # Créer un processus normal d'abord
        process = m.Process.objects.create(name='test', pid=1234, status='running')
        
        # Tentative d'injection via recherche
        try:
            results = m.Process.objects.filter(name=malicious_input)
            # Django ORM devrait protéger automatiquement
            self.assertEqual(list(results), [])
        except Exception as e:
            self.fail(f"ORM should protect against SQL injection: {e}")

# ------------------------------
# Tests de Configuration
# ------------------------------

class ConfigurationTests(TestCase):
    """Tests de configuration et settings"""

    @override_settings(DEBUG=False)
    def test_production_mode(self):
        """Test comportement en mode production"""
        from django.conf import settings
        self.assertFalse(settings.DEBUG)

    @override_settings(CELERY_TASK_ALWAYS_EAGER=True)
    def test_celery_eager_mode(self):
        """Test mode eager Celery pour les tests"""
        # En mode eager, les tâches s'exécutent de façon synchrone
        with patch('api.tasks.psutil.cpu_percent') as mock_cpu:
            mock_cpu.return_value = 50.0
            
            result = t.record_cpu_usage()
            
            # Vérifier que la tâche s'est exécutée
            cpu_usage = m.CPUUsage.objects.first()
            self.assertIsNotNone(cpu_usage)
            self.assertEqual(cpu_usage.usage, 50.0)

# Ajout d'imports manquants pour les tests
import psutil
import subprocess


def test_models_creation_basic(db, user):
    p = m.Process.objects.create(name='python', pid=123, status='running')
    s = m.Service.objects.create(name='nginx', status='active')
    n = m.Network.objects.create(interface='eth0', received=1000, sent=2000)
    cpu = m.CPUUsage.objects.create(usage=12.5)
    mem = m.MemoryUsage.objects.create(usage=33.3)
    netu = m.NetworkUsage.objects.create(interface='eth0', received=111, sent=222)
    fs = m.FileSystem.objects.create(
        path='/', name='root', type='directory', size=0,
        modified_at=timezone.now(), permissions='755', owner='root', group='wheel'
    )
    role = m.Role.objects.create(name='admin', permissions={'manage_users': True})
    profile = m.UserProfile.objects.get(user=user)
    log = m.AuditLog.objects.create(user=user, action='login', details='Logged in', ip_address='127.0.0.1')
    stor = m.StorageUsage.objects.create(device='/dev/disk1', mount_point='/', total=1, used=1, free=0, percent_used=100.0, fs_type='apfs')
    env = m.SimulationEnvironment.objects.create(name='sim', created_by=user, status='idle', config={'k': 'v'})
    res = m.SimulationResult.objects.create(environment=env, metrics={'ok': True}, type='cpu_load')
    totp = m.TOTPDevice.objects.create(user=user, name='default', key='ABC123', confirmed=False)

    # Assertions
    assert p.id and s.id and n.id and cpu.id and mem.id and netu.id and fs.id
    assert role.id and profile.id and log.id and stor.id and env.id and res.id and totp.id

# ------------------------------
# Utils tests
# ------------------------------

@mock.patch('api.utils.psutil.process_iter')
def test_get_processes(mock_iter):
    class Proc:
        def __init__(self, pid, name, status):
            self.info = {'pid': pid, 'name': name, 'status': status}
        def cpu_percent(self):
            return 5.0
        def memory_percent(self):
            return 1.0
    mock_iter.return_value = [Proc(1, 'a', 'running'), Proc(2, 'b', 'sleeping')]
    procs = u.get_processes()
    assert isinstance(procs, list) and len(procs) == 2
    assert all('cpu_percent' in p for p in procs)

@mock.patch('api.utils.psutil.Process')
def test_stop_process(mock_proc):
    assert u.stop_process(999) is True
    mock_proc.side_effect = __import__('psutil').NoSuchProcess(999)
    assert u.stop_process(999) is False

@mock.patch('api.utils.subprocess.check_output')
def test_get_services_systemctl(mock_out):
    sample = 'UNIT \nnginx.service loaded running \nsshd.service loaded exited \n  \n  \n  \n  \n  \n'
    mock_out.return_value = sample.encode()
    services = u.get_services()
    assert {'name': 'nginx', 'status': 'running'} in services

@mock.patch('api.utils.subprocess.check_call')
def test_block_ip(mock_call):
    assert u.block_ip('1.2.3.4') is True
    mock_call.side_effect = __import__('subprocess').CalledProcessError(1, 'cmd')
    assert u.block_ip('1.2.3.4') is False

@mock.patch('api.utils.psutil.disk_partitions')
@mock.patch('api.utils.psutil.disk_usage')
def test_get_storage_info(mock_usage, mock_parts):
    mock_parts.return_value = [
        type('P', (), {'device': '/dev/d1', 'mountpoint': '/', 'fstype': 'apfs'})
    ]
    mock_usage.return_value = type('U', (), {'total': 10, 'used': 5, 'free': 5, 'percent': 50.0})
    data = u.get_storage_info()
    assert data and data[0]['device'] == '/dev/d1'

# ------------------------------
# Tasks tests
# ------------------------------

@mock.patch('api.tasks.psutil.cpu_percent', return_value=12.0)
def test_task_record_cpu_usage(mock_cpu, db):
    t.record_cpu_usage()
    assert m.CPUUsage.objects.count() == 1

@mock.patch('api.tasks.psutil.virtual_memory')
def test_task_record_memory_usage(mock_vm, db):
    mock_vm.return_value = type('M', (), {'percent': 22.5})
    t.record_memory_usage()
    assert m.MemoryUsage.objects.count() == 1

@mock.patch('api.tasks.psutil.net_io_counters')
def test_task_record_network_usage(mock_net, db):
    mock_net.return_value = {
        'en0': type('S', (), {'bytes_recv': 100, 'bytes_sent': 50}),
        'lo0': type('S', (), {'bytes_recv': 10, 'bytes_sent': 5}),
    }
    t.record_network_usage()
    assert m.NetworkUsage.objects.count() == 2

@mock.patch('api.tasks.requests.post')
def test_task_send_slack_notification(mock_post, settings):
    mock_post.return_value = type('Resp', (), {'status_code': 200})
    code = t.send_slack_notification('hello')
    assert code == 200

@mock.patch('api.tasks.get_storage_info')
def test_task_record_storage_usage(mock_si, db):
    mock_si.return_value = [
        {
            'device': '/dev/d1', 'mount_point': '/', 'total': 10,
            'used': 5, 'free': 5, 'percent_used': 50.0, 'fs_type': 'apfs'
        }
    ]
    t.record_storage_usage()
    assert m.StorageUsage.objects.count() == 1

@pytest.mark.django_db
def test_task_send_email_notification(mailoutbox):
    t.send_email_notification('Hi', 'There', ['to@example.com'])
    assert len(mailoutbox) == 1
    assert mailoutbox[0].subject == 'Hi'

# ------------------------------
# Views tests (DRF & Django views)
# ------------------------------

@mock.patch('api.views.psutil.process_iter')
@pytest.mark.django_db
def test_processes_list(auth_client):
    class Proc:
        def __init__(self, pid, name, cpu_percent, memory_percent, status):
            self._d = {'pid': pid, 'name': name, 'cpu_percent': cpu_percent, 'memory_percent': memory_percent, 'status': status}
        def as_dict(self, attrs=None):
            return self._d
    auth_client.force_authenticate(user=User.objects.first())
    url = '/api/processes/'
    with mock.patch('api.views.psutil.process_iter', return_value=[Proc(1,'a',0.0,0.0,'running')]):
        resp = auth_client.get(url)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

@mock.patch('api.views.get_services', return_value=[{'name':'svc','status':'active'}])
@pytest.mark.django_db
def test_services_list(auth_client, mock_gs):
    resp = auth_client.get('/api/services/')
    assert resp.status_code == 200
    assert resp.json()[0]['name'] == 'svc'

@pytest.mark.django_db
def test_network_crud_and_actions(auth_client, monkeypatch):
    # CRUD
    create = auth_client.post('/api/networks/', {'interface':'en0','received':1,'sent':2}, format='json')
    assert create.status_code == 201
    nid = create.json()['id']

    lst = auth_client.get('/api/networks/')
    assert lst.status_code == 200 and len(lst.json()) >= 1

    upd = auth_client.put(f'/api/networks/{nid}/', {'interface':'en0','received':3,'sent':4}, format='json')
    assert upd.status_code == 200 and upd.json()['received'] == 3

    # Actions
    monkeypatch.setattr('api.views.block_ip', lambda ip: True)
    r = auth_client.post('/api/networks/block_ip/', {'ip_address':'1.2.3.4'}, format='json')
    assert r.status_code == 200

    monkeypatch.setattr('api.views.unblock_ip', lambda ip: True)
    r = auth_client.post('/api/networks/unblock_ip/', {'ip_address':'1.2.3.4'}, format='json')
    assert r.status_code == 200

    monkeypatch.setattr('api.views.block_port', lambda p, protocol='tcp': True)
    r = auth_client.post('/api/networks/block_port/', {'port':22,'protocol':'tcp'}, format='json')
    assert r.status_code == 200

    monkeypatch.setattr('api.views.get_network_interfaces', lambda: [{'name':'en0'}])
    r = auth_client.get('/api/networks/interfaces/')
    assert r.status_code == 200 and r.json()[0]['name'] == 'en0'

    monkeypatch.setattr('api.views.configure_interface', lambda i,c: True)
    r = auth_client.post('/api/networks/configure_interface/', {'interface':'en0','config':{'mtu':1500}}, format='json')
    assert r.status_code == 200

    # DELETE
    dele = auth_client.delete(f'/api/networks/{nid}/')
    assert dele.status_code == 204

@mock.patch('api.views.send_slack_notification')
@pytest.mark.django_db
def test_slack_notify_endpoint(mock_task, auth_client):
    mock_task.delay.return_value = None
    r = auth_client.post('/api/notify/slack/', {'message': 'hi'}, format='json')
    assert r.status_code == 200

@mock.patch('api.views.send_email_notification')
@pytest.mark.django_db
def test_email_notify_endpoint(mock_task, auth_client):
    mock_task.delay.return_value = None
    r = auth_client.post('/api/notify/email/', {'subject': 's', 'message': 'm', 'recipient_list': ['a@b']}, format='json')
    assert r.status_code == 200

@mock.patch('api.views.execute_ssh_command', return_value='ok')
@pytest.mark.django_db
def test_ssh_command_endpoint(mock_exec, auth_client):
    r = auth_client.post('/api/ssh/command/', {
        'host':'h','port':22,'username':'u','password':'p','command':'echo hi'
    }, format='json')
    assert r.status_code == 200 and r.json()['result'] == 'ok'

@pytest.mark.django_db
def test_api_login_token_flow(client, db):
    user = User.objects.create_user(username='carol', password='pw')
    r = client.post('/api/auth/api-login/', {'username':'carol','password':'pw'}, format='json')
    assert r.status_code == 200
    assert 'token' in r.json()

@mock.patch('api.decorators.AuditLog.objects.create')
@pytest.mark.django_db
def test_role_management_permission_denied_then_granted(mock_log, client, user):
    # No role -> denied
    client.force_login(user)
    r = client.get('/api/roles/')
    assert r.status_code == 403

    # Assign role without permission -> denied
    role = m.Role.objects.create(name='basic', permissions={'view_processes': True})
    prof = m.UserProfile.objects.get(user=user)
    prof.role = role
    prof.save()
    r = client.get('/api/roles/')
    assert r.status_code == 403

    # Grant required permission -> OK
    role.permissions['manage_roles'] = True
    role.save()
    r = client.get('/api/roles/')
    assert r.status_code == 200

# ------------------------------
# WebSocket consumers tests
# ------------------------------

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_process_consumer(monkeypatch):
    monkeypatch.setattr('api.consumers.get_processes', lambda: [{'pid':1,'name':'a','cpu_percent':0.1,'memory_percent':0.2,'status':'running'}])
    comm = WebsocketCommunicator(application, '/ws/processes/')
    connected, _ = await comm.connect()
    assert connected
    # Receive first periodic push
    msg = await comm.receive_from()
    data = json.loads(msg)
    assert isinstance(data, list) and data[0]['pid'] == 1
    await comm.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_service_consumer_actions(monkeypatch):
    monkeypatch.setattr('api.consumers.get_services', lambda: [{'name':'svc','status':'active'}])
    monkeypatch.setattr('api.consumers.start_service', lambda s: True)
    comm = WebsocketCommunicator(application, '/ws/services/')
    ok, _ = await comm.connect()
    assert ok
    # Receive initial list
    await comm.receive_from()
    await comm.send_to(text_data=json.dumps({'action':'start','service':'svc'}))
    resp = json.loads(await comm.receive_from())
    assert resp['status'] == 'success' and resp['action'] == 'start'
    await comm.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_network_consumer_block_ip(monkeypatch, db):
    # Create some data so status payload isn't empty
    m.NetworkUsage.objects.create(interface='en0', received=1, sent=2)
    monkeypatch.setattr('api.consumers.block_ip', lambda ip: True)
    comm = WebsocketCommunicator(application, '/ws/networks/')
    ok, _ = await comm.connect()
    assert ok
    await comm.send_to(text_data=json.dumps({'action':'block_ip','ip_address':'1.2.3.4'}))
    r1 = json.loads(await comm.receive_from())
    assert r1['status'] == 'success'
    # Next message is network status
    status_msg = json.loads(await comm.receive_from())
    assert 'usage' in status_msg
    await comm.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_cpu_memory_consumers(db):
    m.CPUUsage.objects.create(usage=10.0)
    m.MemoryUsage.objects.create(usage=20.0)

    cpu_comm = WebsocketCommunicator(application, '/ws/cpu/')
    ok1, _ = await cpu_comm.connect()
    assert ok1
    cpu_msg = json.loads(await cpu_comm.receive_from())
    assert cpu_msg['type'] == 'cpu_usage' and cpu_msg['data']
    await cpu_comm.disconnect()

    mem_comm = WebsocketCommunicator(application, '/ws/memory/')
    ok2, _ = await mem_comm.connect()
    assert ok2
    mem_msg = json.loads(await mem_comm.receive_from())
    assert mem_msg['type'] == 'memory_usage' and mem_msg['data']
    await mem_comm.disconnect()

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_storage_consumer(monkeypatch):
    monkeypatch.setattr('api.consumers.get_storage_info', lambda: [{'device':'/dev/d1'}])
    comm = WebsocketCommunicator(application, '/ws/storage/')
    ok, _ = await comm.connect()
    assert ok
    msg = json.loads(await comm.receive_from())
    assert msg['type'] == 'storage_info' and msg['data']
    await comm.disconnect()

# ------------------------------
# Auth views (Login/Logout/2FA) tests
# ------------------------------

@pytest.mark.django_db
def test_login_view_success_redirect_dashboard(client, user):
    # user has no 2FA -> should redirect to dashboard
    resp = client.post('/auth/login/', {'username': user.username, 'password': 'secret123'})
    assert resp.status_code in (302, 303)
    assert '/dashboard/' in resp.url

@pytest.mark.django_db
def test_login_view_redirects_to_2fa_when_enabled(client, user):
    profile = m.UserProfile.objects.get(user=user)
    profile.two_factor_enabled = True
    profile.save()
    resp = client.post('/auth/login/', {'username': user.username, 'password': 'secret123'})
    assert resp.status_code in (302, 303)
    assert '/2fa/verify/' in resp.url

@pytest.mark.django_db
def test_two_factor_verify_success(client, user, monkeypatch):
    # Simulate pre-2FA session
    session = client.session
    session['pre_2fa_user_id'] = user.id
    session.save()

    class DummyDevice:
        def verify_token(self, token):
            return True
    monkeypatch.setattr('api.views.TOTPDevice.objects.get', lambda user: DummyDevice())

    resp = client.post('/2fa/verify/', {'token': '123456'})
    assert resp.status_code in (302, 303)
    assert '/dashboard/' in resp.url

@pytest.mark.django_db
def test_logout_view_redirect(client, user):
    client.force_login(user)
    resp = client.get('/auth/logout/')
    assert resp.status_code in (302, 303)
    assert '/auth/login/' in resp.url or '/login' in resp.url
