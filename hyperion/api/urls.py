# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProcessViewSet, ServiceViewSet, NetworkViewSet

router = DefaultRouter()
router.register(r'processes', ProcessViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'networks', NetworkViewSet)

urlpatterns = [
    path('', include(router.urls)),
]