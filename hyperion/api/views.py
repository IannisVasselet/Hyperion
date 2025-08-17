# api/views.py
import os
import base64
from django.shortcuts import render
from django.core.serializers import serialize
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import FormView, TemplateView
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.clickjacking import xframe_options_deny
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from django import forms
import json
import psutil

# Security imports for enhanced protection
try:
    from django_ratelimit.decorators import ratelimit
    RATELIMIT_AVAILABLE = True
except ImportError:
    # Fallback decorator if django-ratelimit is not installed
    def ratelimit(group=None, key=None, rate=None, method=['POST'], block=True):
        def decorator(func):
            return func
        return decorator
    RATELIMIT_AVAILABLE = False

# OTP imports - fixed StaticDevice import
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp.util import random_hex

# QR code generation
import qrcode
import qrcode.image.svg
from io import BytesIO

# Two factor authentication
from two_factor.forms import TOTPDeviceForm
from two_factor.utils import get_otpauth_url
from two_factor.views import SetupView

from rest_framework import viewsets, status, permissions, authentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.authtoken.models import Token

from .models import (
    Process, Service, Network, CPUUsage, MemoryUsage, NetworkUsage,
    UserProfile, AuditLog, Role
    )
from .serializers import ProcessSerializer, ServiceSerializer, NetworkSerializer
from .secure_serializers import (
    IPBlockSerializer, PortBlockSerializer, ProcessActionSerializer,
    ServiceActionSerializer, NetworkInterfaceSerializer, SecureShellCommandSerializer
)
from .utils import (
    get_processes, stop_process, change_process_priority,
    get_services, execute_ssh_command, block_ip, unblock_ip,
    block_port, get_network_interfaces, configure_interface
    )
from .tasks import send_slack_notification, send_email_notification
from .decorators import require_permission

# Security decorators and utilities
def csp_headers(func):
    """Ajouter les en-têtes Content Security Policy"""
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if hasattr(response, 'headers'):
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdnjs.cloudflare.com; "
                "connect-src 'self' ws: wss:; "
                "frame-ancestors 'none';"
            )
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    return wrapper

def security_headers(func):
    """Décorateur pour ajouter tous les en-têtes de sécurité"""
    def wrapper(request, *args, **kwargs):
        response = func(request, *args, **kwargs)
        if hasattr(response, 'headers'):
            # En-têtes de sécurité standards
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        return response
    return wrapper

def get_client_ip(request):
    """Obtenir l'IP réelle du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
    return ip

def log_security_event(user, action, details, ip_address, success=True):
    """Journaliser un événement de sécurité"""
    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            details=details,
            ip_address=ip_address,
            success=success
        )
    except Exception as e:
        # Ne pas faire échouer la vue si la journalisation échoue
        print(f"Erreur lors de la journalisation: {e}")

# Décorateurs composés pour les vues sensibles
def secure_view(view_func):
    """Décorateur composite pour sécuriser les vues sensibles"""
    return method_decorator([
        csrf_protect,
        xframe_options_deny,
        never_cache,
        security_headers,
        ratelimit(group='sensitive_view', key='ip', rate='10/m', method='ALL', block=True)
    ], name='dispatch')(view_func)

def secure_api_view(view_func):
    """Décorateur composite pour sécuriser les vues API"""
    return method_decorator([
        csrf_protect,
        never_cache,
        security_headers,
        ratelimit(group='api_view', key='user_or_ip', rate='60/m', method='ALL', block=True)
    ], name='dispatch')(view_func)

@method_decorator([
    ratelimit(group='login', key='ip', rate='5/m', method='POST', block=True),
    csrf_protect,
    never_cache,
    security_headers
], name='dispatch')
class LoginAPIView(APIView):
    # Désactive explicitement l'authentification pour cette vue
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        # Validation des entrées
        if not request.data:
            return Response({
                'status': 'error',
                'message': 'Données manquantes'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extraire et valider les données du JSON
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')
        
        # Validation basique des entrées
        if not username or not password:
            log_security_event(
                user=None,
                action='failed_login',
                details=f'Tentative de connexion avec données manquantes',
                ip_address=get_client_ip(request),
                success=False
            )
            return Response({
                'status': 'error',
                'message': 'Nom d\'utilisateur et mot de passe requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validation de la longueur pour éviter les attaques
        if len(username) > 150 or len(password) > 128:
            log_security_event(
                user=None,
                action='failed_login',
                details=f'Tentative de connexion avec données trop longues - Username: {username[:50]}',
                ip_address=get_client_ip(request),
                success=False
            )
            return Response({
                'status': 'error',
                'message': 'Données invalides'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Déboguer les données reçues (sans afficher le mot de passe)
        print(f"Received login attempt for user: {username}")
        
        # Tentative d'authentification
        user = authenticate(username=username, password=password)
        client_ip = get_client_ip(request)
        
        if user is not None:
            # Vérifier si l'utilisateur est actif
            if not user.is_active:
                log_security_event(
                    user=user,
                    action='failed_login',
                    details='Tentative de connexion sur compte désactivé',
                    ip_address=client_ip,
                    success=False
                )
                return Response({
                    'status': 'error',
                    'message': 'Compte désactivé'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Connexion réussie
            login(request, user)
            
            # Créer ou récupérer un token
            token, _ = Token.objects.get_or_create(user=user)
            
            # Mettre à jour l'IP de dernière connexion
            try:
                profile = user.userprofile
                profile.last_login_ip = client_ip
                profile.save()
            except UserProfile.DoesNotExist:
                # Créer le profil s'il n'existe pas
                UserProfile.objects.create(user=user, last_login_ip=client_ip)
            
            # Journaliser la connexion réussie
            log_security_event(
                user=user,
                action='api_login',
                details=f'API Login successful from {client_ip}',
                ip_address=client_ip,
                success=True
            )
            
            return Response({
                'status': 'success',
                'token': token.key,
                'user_id': user.id,
                'username': user.username
            })
        else:
            # Authentification échouée
            log_security_event(
                user=None,
                action='failed_login',
                details=f'Failed login attempt for username: {username[:50]}',
                ip_address=client_ip,
                success=False
            )
    
        return Response({
            'status': 'error',
            'message': 'Identifiants invalides'
        }, status=status.HTTP_401_UNAUTHORIZED)

class ProcessSerializer(serializers.Serializer):
    pid = serializers.IntegerField()
    name = serializers.CharField()
    cpu_percent = serializers.FloatField()
    memory_percent = serializers.FloatField()
    status = serializers.CharField()
@method_decorator([
    csrf_protect,
    never_cache,
    security_headers,
    ratelimit(group='process_api', key='user', rate='30/m', method='ALL', block=True)
], name='dispatch')
class ProcessViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    serializer_class = ProcessSerializer

    def get_queryset(self):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent', 'status'])
                processes.append({
                    'pid': pinfo['pid'],
                    'name': pinfo['name'],
                    'cpu_percent': pinfo['cpu_percent'] or 0.0,
                    'memory_percent': pinfo['memory_percent'] or 0.0,
                    'status': pinfo['status'] or 'unknown'
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        return processes

    def list(self, request):
        processes = self.get_queryset()
        serializer = ProcessSerializer(processes, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            process = psutil.Process(int(pk))
            pinfo = process.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent', 'status'])
            data = {
                'pid': pinfo['pid'],
                'name': pinfo['name'],
                'cpu_percent': pinfo['cpu_percent'] or 0.0,
                'memory_percent': pinfo['memory_percent'] or 0.0,
                'status': pinfo['status'] or 'unknown'
            }
            serializer = ProcessSerializer(data)
            return Response(serializer.data)
        except psutil.NoSuchProcess:
            return Response(status=status.HTTP_404_NOT_FOUND)

@method_decorator([
    csrf_protect,
    never_cache,
    security_headers,
    ratelimit(group='service_api', key='user', rate='20/m', method='ALL', block=True)
], name='dispatch')
class ServiceViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]
    
    def list(self, request):
        # Validation de l'utilisateur et journalisation
        log_security_event(
            user=request.user,
            action='service_list',
            details='Liste des services demandée',
            ip_address=get_client_ip(request)
        )
        
        services = get_services()
        return Response(services)

@method_decorator([
    csrf_protect,
    never_cache,
    security_headers,
    ratelimit(group='network_api', key='user', rate='15/m', method='ALL', block=True)
], name='dispatch')
class NetworkViewSet(viewsets.ModelViewSet):
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication]

    @action(detail=False, methods=['post'])
    @method_decorator([
        ratelimit(group='block_ip', key='user', rate='5/m', method='POST', block=True),
        require_permission('manage_network')
    ])
    def block_ip(self, request):
        # Utiliser le sérializer sécurisé pour la validation
        serializer = IPBlockSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Données invalides',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        ip_address = validated_data['ip_address']
        reason = validated_data.get('reason', '')
        
        # Empêcher de se bloquer soi-même
        client_ip = get_client_ip(request)
        if ip_address == client_ip:
            log_security_event(
                user=request.user,
                action='self_ip_block_attempt',
                details=f'Tentative de blocage de sa propre IP: {ip_address}',
                ip_address=client_ip,
                success=False
            )
            return Response({
                'error': 'Impossible de bloquer votre propre adresse IP'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Bloquer l'IP
        if block_ip(ip_address):
            log_security_event(
                user=request.user,
                action='ip_blocked',
                details=f'IP bloquée: {ip_address}. Raison: {reason}',
                ip_address=client_ip
            )
            return Response({
                'status': 'IP bloquée avec succès',
                'ip': ip_address,
                'reason': reason
            })
        
        return Response({
            'error': 'Échec du blocage de l\'IP'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    @method_decorator([
        ratelimit(group='unblock_ip', key='user', rate='10/m', method='POST', block=True),
        require_permission('manage_network')
    ])
    def unblock_ip(self, request):
        # Validation stricte des entrées
        ip_address = request.data.get('ip_address', '').strip()
        
        if not ip_address:
            return Response({
                'error': 'Adresse IP requise'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validation du format IP
        import ipaddress
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            return Response({
                'error': 'Format d\'adresse IP invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if unblock_ip(ip_address):
            log_security_event(
                user=request.user,
                action='ip_unblocked',
                details=f'IP débloquée: {ip_address}',
                ip_address=get_client_ip(request)
            )
            return Response({'status': 'IP débloquée avec succès'})
        
        return Response({
            'error': 'Échec du déblocage de l\'IP'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    @method_decorator([
        ratelimit(group='block_port', key='user', rate='5/m', method='POST', block=True),
        require_permission('manage_network')
    ])
    def block_port(self, request):
        # Utiliser le sérializer sécurisé pour la validation
        serializer = PortBlockSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Données invalides',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        port = validated_data['port']
        protocol = validated_data['protocol']
        reason = validated_data.get('reason', '')
        
        # Empêcher de bloquer des ports critiques
        critical_ports = [22, 80, 443, 8000]  # SSH, HTTP, HTTPS, Django dev
        if port in critical_ports:
            log_security_event(
                user=request.user,
                action='critical_port_block_attempt',
                details=f'Tentative de blocage du port critique {port}',
                ip_address=get_client_ip(request),
                success=False
            )
            return Response({
                'error': f'Impossible de bloquer le port critique {port}'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if block_port(port, protocol):
            log_security_event(
                user=request.user,
                action='port_blocked',
                details=f'Port {port}/{protocol} bloqué. Raison: {reason}',
                ip_address=get_client_ip(request)
            )
            return Response({
                'status': f'Port {port}/{protocol} bloqué avec succès',
                'port': port,
                'protocol': protocol,
                'reason': reason
            })
        
        return Response({
            'error': 'Échec du blocage du port'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def interfaces(self, request):
        interfaces = get_network_interfaces()
        return Response(interfaces)

    @action(detail=False, methods=['post'])
    def configure_interface(self, request):
        interface = request.data.get('interface')
        config = request.data.get('config', {})
        if configure_interface(interface, config):
            return Response({'status': 'Interface configured'})
        return Response({'error': 'Failed to configure interface'}, status=400)

class SlackNotificationView(APIView):
    def post(self, request):
        message = request.data.get('message')
        if message:
            send_slack_notification.delay(message)
            return Response({'status': 'Notification sent'}, status=status.HTTP_200_OK)
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

class EmailNotificationView(APIView):
    def post(self, request):
        subject = request.data.get('subject')
        message = request.data.get('message')
        recipient_list = request.data.get('recipient_list')
        if subject and message and recipient_list:
            send_email_notification.delay(subject, message, recipient_list)
            return Response({'status': 'Email sent'}, status=status.HTTP_200_OK)
        return Response({'error': 'Subject, message, and recipient_list are required'}, status=status.HTTP_400_BAD_REQUEST)
    
class SSHCommandView(APIView):
    def post(self, request):
        host = request.data.get('host')
        port = request.data.get('port', 22)
        username = request.data.get('username')
        password = request.data.get('password')
        command = request.data.get('command')
        if host and username and password and command:
            try:
                result = execute_ssh_command(host, port, username, password, command)
                return Response({'result': result}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

@login_required
@csrf_protect
@xframe_options_deny
@never_cache
@security_headers
@ratelimit(group='dashboard', key='user', rate='60/h', method='GET', block=True)
def dashboard(request):
    """Vue sécurisée du tableau de bord avec contrôles d'accès"""
    
    # Journaliser l'accès au dashboard
    log_security_event(
        user=request.user,
        action='dashboard_access',
        details='Accès au tableau de bord principal',
        ip_address=get_client_ip(request)
    )
    
    try:
        # Limiter les données selon les permissions de l'utilisateur
        user_profile = getattr(request.user, 'userprofile', None)
        
        # Données de base (toujours accessibles)
        context = {
            'cpu_usage': '[]',
            'memory_usage': '[]',
            'network_usage': '[]',
        }
        
        # Vérifier les permissions pour les données sensibles
        if user_profile and user_profile.role:
            role = user_profile.role
            
            # Données CPU - permission view_analytics requise
            if role.has_permission('view_analytics'):
                cpu_usage = list(CPUUsage.objects.values()[:100])  # Limiter à 100 entrées
                context['cpu_usage'] = json.dumps(cpu_usage, default=str)
            
            # Données mémoire - permission view_analytics requise
            if role.has_permission('view_analytics'):
                memory_usage = list(MemoryUsage.objects.values()[:100])
                context['memory_usage'] = json.dumps(memory_usage, default=str)
            
            # Données réseau - permission view_network requise
            if role.has_permission('view_analytics'):
                network_usage = list(NetworkUsage.objects.values()[:100])
                context['network_usage'] = json.dumps(network_usage, default=str)
        
        # Ajouter des informations sur l'utilisateur (sécurisées)
        context.update({
            'user_permissions': list(user_profile.role.permission_list) if user_profile and user_profile.role else [],
            'is_admin': user_profile.is_admin if user_profile else False,
            'username': request.user.username,
            'last_login': request.user.last_login.strftime('%Y-%m-%d %H:%M') if request.user.last_login else 'Jamais',
        })
        
        return render(request, 'dashboard.html', context)
        
    except Exception as e:
        # Journaliser l'erreur sans exposer de détails sensibles
        log_security_event(
            user=request.user,
            action='dashboard_error',
            details=f'Erreur lors de l\'accès au dashboard: {type(e).__name__}',
            ip_address=get_client_ip(request),
            success=False
        )
        
        # Retourner une erreur générique
        return render(request, 'dashboard.html', {
            'error': 'Une erreur s\'est produite lors du chargement du dashboard',
            'cpu_usage': '[]',
            'memory_usage': '[]',
            'network_usage': '[]',
        })

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, 'registration/login.html')

    def post(self, request):
        # Change request.data to request.POST
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if hasattr(user, 'userprofile') and user.userprofile.two_factor_enabled:
                # Store user ID in session for 2FA verification
                request.session['pre_2fa_user_id'] = user.id
                return redirect('2fa-verify')
            
            login(request, user)
            # Log the successful login
            AuditLog.objects.create(
                user=user,
                action='login',
                details=f'Login from {request.META.get("REMOTE_ADDR")}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return redirect('dashboard')
        
        return render(request, 'registration/login.html', {
            'error_message': 'Invalid username or password'
        })
        
class LogoutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            # Log the logout action
            AuditLog.objects.create(
                user=request.user,
                action='logout',
                details=f'Logout from {request.META.get("REMOTE_ADDR")}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            logout(request)
        return redirect('login')

class TOTPDeviceForm(forms.Form):
    token = forms.CharField(max_length=6)

    def __init__(self, key, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = key
        self.user = user

class TwoFactorSetupView(LoginRequiredMixin, FormView):
    template_name = 'two_factor/setup.html'
    form_class = TOTPDeviceForm
    success_url = reverse_lazy('dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Generate a new secret key if we don't have one
        if not hasattr(self, 'device'):
            self.device = TOTPDevice(user=self.request.user, confirmed=False)
            self.device.key = random_hex()

        kwargs['key'] = self.device.key
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not hasattr(self, 'device'):
            self.device = TOTPDevice(user=self.request.user, confirmed=False)
            self.device.key = random_hex()
            
        # Generate provisioning URI for QR code
        provisioning_uri = f"otpauth://totp/Hyperion:{self.request.user.username}?secret={self.device.key}&issuer=Hyperion"
        
        # Generate QR code
        img = qrcode.make(
            provisioning_uri,
            image_factory=qrcode.image.svg.SvgImage,
            box_size=10,
            border=5
        )
        
        # Convert QR code to string
        context['qr_code'] = img.to_string().decode('utf-8')
        return context

    def form_valid(self, form):
        self.device.confirmed = True
        self.device.save()
        
        # Update user profile
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        profile.two_factor_enabled = True
        profile.two_factor_secret = self.device.key
        profile.save()
        
        return super().form_valid(form)

class TwoFactorVerifyView(View):
    def get(self, request):
        if not request.session.get('pre_2fa_user_id'):
            return redirect('login')
        return render(request, 'registration/2fa_verify.html')

    def post(self, request):
        token = request.POST.get('token')
        user_id = request.session.get('pre_2fa_user_id')
        
        try:
            user = User.objects.get(id=user_id)
            device = TOTPDevice.objects.get(user=user)
            
            if device.verify_token(token):
                login(request, user)
                del request.session['pre_2fa_user_id']
                AuditLog.objects.create(
                    user=user,
                    action='2fa_success',
                    details=f'2FA verification from {request.META.get("REMOTE_ADDR")}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                return redirect('dashboard')
            
            AuditLog.objects.create(
                user=user,
                action='2fa_failed',
                details=f'Failed 2FA attempt from {request.META.get("REMOTE_ADDR")}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return render(request, 'registration/2fa_verify.html', {'error': 'Invalid token'})
            
        except (User.DoesNotExist, TOTPDevice.DoesNotExist):
            return redirect('login')
        
class TwoFactorManageView(LoginRequiredMixin, View):
    template_name = 'two_factor/manage.html'
    
    def get(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        context = {
            'two_factor_enabled': profile.two_factor_enabled
        }
        return render(request, 'two_factor/manage.html', context)

    def post(self, request):
        action = request.POST.get('action')
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        if action == 'disable':
            # Disable 2FA
            profile.two_factor_enabled = False
            profile.two_factor_secret = ''
            profile.save()
            
            # Delete TOTP device
            TOTPDevice.objects.filter(user=request.user).delete()
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action='2fa_disabled',
                details=f'2FA disabled from {request.META.get("REMOTE_ADDR")}',
                ip_address=request.META.get('REMOTE_ADDR')
            )
        
        return redirect('dashboard')
    
class RoleManagementView(LoginRequiredMixin, View):
    template_name = 'admin/role_management.html'
    
    @require_permission('manage_roles')
    def get(self, request):
        roles = Role.objects.all()
        return render(request, self.template_name, {
            'roles': roles,
            'available_permissions': Role.AVAILABLE_PERMISSIONS
        })
    
    @require_permission('manage_roles')
    def post(self, request):
        action = request.POST.get('action')
        
        if action == 'create':
            name = request.POST.get('name')
            description = request.POST.get('description')
            permissions = request.POST.getlist('permissions')
            
            role = Role.objects.create(
                name=name,
                description=description,
                permissions={p: True for p in permissions}
            )
            
            AuditLog.objects.create(
                user=request.user,
                action='role_created',
                details=f'Role {name} created'
            )
            
        elif action == 'delete':
            role_id = request.POST.get('role_id')
            role = Role.objects.get(id=role_id)
            role_name = role.name
            role.delete()
            
            AuditLog.objects.create(
                user=request.user,
                action='role_deleted',
                details=f'Role {role_name} deleted'
            )
            
        return redirect('role-management')
    
def ssh_terminal(request):
    return render(request, 'ssh_terminal.html')

@method_decorator(login_required, name='dispatch')
class CustomSetupView(SetupView):
    template_name = 'two_factor/core/setup.html'
    success_url = 'two_factor:setup_complete'
    
@method_decorator(login_required, name='dispatch')
class TwoFactorQRView(View):
    def get(self, request, *args, **kwargs):
        # Get or create TOTP device
        device, created = TOTPDevice.objects.get_or_create(
            user=request.user,
            defaults={
                'name': 'default',
                'key': random_hex(),
                'confirmed': False
            }
        )
        
        # Generate QR code
        provisioning_uri = get_otpauth_url(
            accountname=request.user.username,
            secret=device.key,
            issuer="Hyperion"
        )
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        # Generate image
        img_buffer = BytesIO()
        qr.make_image().save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return HttpResponse(
            img_buffer.getvalue(),
            content_type='image/png'
        )
        
@method_decorator(login_required, name='dispatch')
class TwoFactorBackupTokensView(TemplateView):
    template_name = 'two_factor/core/backup_tokens.html'

    def get(self, request, *args, **kwargs):
        device = self._get_or_create_device(request.user)
        tokens = [token.token for token in device.token_set.all()]
        return JsonResponse({
            'backup_tokens': tokens,
            'tokens_count': len(tokens)
        })

    def post(self, request, *args, **kwargs):
        device = self._get_or_create_device(request.user)
        device.token_set.all().delete()
        
        # Generate new backup tokens
        tokens = []
        for _ in range(10):  # Generate 10 backup tokens
            token = device.generate_token()
            tokens.append(token.token)

        return JsonResponse({
            'backup_tokens': tokens,
            'tokens_count': len(tokens)
        })

    def _get_or_create_device(self, user):
        """Get or create a static device for backup tokens"""
        device, _ = StaticDevice.objects.get_or_create(
            user=user,
            name='backup'
        )
        return device