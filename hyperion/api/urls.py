# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProcessViewSet, ServiceViewSet, NetworkViewSet,
    SlackNotificationView, EmailNotificationView, SSHCommandView,
    dashboard, LoginView, LogoutView, TwoFactorSetupView, TwoFactorVerifyView, TwoFactorManageView,
    RoleManagementView
    )
from . import views

router = DefaultRouter()
router.register(r'processes', ProcessViewSet, basename='process')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'networks', NetworkViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('notify/slack/', SlackNotificationView.as_view(), name='slack-notify'),
    path('notify/email/', EmailNotificationView.as_view(), name='email-notify'),
    path('ssh/command/', SSHCommandView.as_view(), name='ssh-command'),
    path('dashboard/', dashboard, name='dashboard'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/2fa/setup/', TwoFactorSetupView.as_view(), name='2fa-setup'),
    path('auth/2fa/verify/', TwoFactorVerifyView.as_view(), name='2fa-verify'),
    path('2fa/setup/', TwoFactorSetupView.as_view(), name='2fa-setup'),
    path('2fa/verify/', TwoFactorVerifyView.as_view(), name='2fa-verify'),
    path('roles/', RoleManagementView.as_view(), name='role-management'),
    path('auth/2fa/manage/', TwoFactorManageView.as_view(), name='2fa-manage'),
    path('ssh/', views.ssh_terminal, name='ssh_terminal'),
]