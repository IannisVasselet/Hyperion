# api/views.py
from django.shortcuts import render
from django.core.serializers import serialize
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import FormView
from django.urls import reverse_lazy
from django import forms
import json

from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
import qrcode
import qrcode.image.svg
from two_factor.forms import TOTPDeviceForm

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import (
    Process, Service, Network, CPUUsage, MemoryUsage, NetworkUsage,
    UserProfile, AuditLog, Role
    )
from .serializers import ProcessSerializer, ServiceSerializer, NetworkSerializer
from .utils import (
    get_processes, stop_process, change_process_priority,
    get_services, execute_ssh_command, block_ip, unblock_ip,
    block_port, get_network_interfaces, configure_interface
    )
from .tasks import send_slack_notification, send_email_notification
from .decorators import require_permission

class ProcessViewSet(viewsets.ViewSet):
    @require_permission('view_processes')
    def list(self, request):
        processes = get_processes()
        return Response(processes)

    @require_permission('manage_processes')
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        if stop_process(int(pk)):
            return Response({'status': 'process stopped'})
        return Response({'error': 'process not found'}, status=404)

    @action(detail=True, methods=['post'])
    def priority(self, request, pk=None):
        priority = request.data.get('priority')
        if change_process_priority(int(pk), int(priority)):
            return Response({'status': 'priority changed'})
        return Response({'error': 'process not found'}, status=404)

class ServiceViewSet(viewsets.ViewSet):
    def list(self, request):
        services = get_services()
        return Response(services)

class NetworkViewSet(viewsets.ModelViewSet):
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer

    @action(detail=False, methods=['post'])
    def block_ip(self, request):
        ip_address = request.data.get('ip_address')
        if block_ip(ip_address):
            return Response({'status': 'IP blocked'})
        return Response({'error': 'Failed to block IP'}, status=400)

    @action(detail=False, methods=['post'])
    def unblock_ip(self, request):
        ip_address = request.data.get('ip_address')
        if unblock_ip(ip_address):
            return Response({'status': 'IP unblocked'})
        return Response({'error': 'Failed to unblock IP'}, status=400)

    @action(detail=False, methods=['post'])
    def block_port(self, request):
        port = request.data.get('port')
        protocol = request.data.get('protocol', 'tcp')
        if block_port(port, protocol):
            return Response({'status': 'Port blocked'})
        return Response({'error': 'Failed to block port'}, status=400)

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

def dashboard(request):
    cpu_usage = list(CPUUsage.objects.values())
    memory_usage = list(MemoryUsage.objects.values())
    network_usage = list(NetworkUsage.objects.values())
    context = {
        'cpu_usage': json.dumps(cpu_usage, default=str),
        'memory_usage': json.dumps(memory_usage, default=str),
        'network_usage': json.dumps(network_usage, default=str),
    }
    return render(request, 'dashboard.html', context)

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
            profile.two_factor_enabled = False
            profile.two_factor_secret = ''
            profile.save()
            
            TOTPDevice.objects.filter(user=request.user).delete()
            
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
            
            Role.objects.create(
                name=name,
                description=description,
                permissions={p: True for p in permissions}
            )
            
        elif action == 'delete':
            role_id = request.POST.get('role_id')
            Role.objects.filter(id=role_id).delete()
        
        return redirect('role-management')