# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProcessViewSet, ServiceViewSet, NetworkViewSet, SlackNotificationView, EmailNotificationView, SSHCommandView

router = DefaultRouter()
router.register(r'processes', ProcessViewSet, basename='process')
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'networks', NetworkViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('notify/slack/', SlackNotificationView.as_view(), name='slack-notify'),
    path('notify/email/', EmailNotificationView.as_view(), name='email-notify'),
    path('ssh/command/', SSHCommandView.as_view(), name='ssh-command'),

]