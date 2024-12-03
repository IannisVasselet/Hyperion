# api/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Process, Service, Network
from .serializers import ProcessSerializer, ServiceSerializer, NetworkSerializer
from .utils import get_processes, get_services

class ProcessViewSet(viewsets.ViewSet):
    def list(self, request):
        processes = get_processes()
        return Response(processes)

class ServiceViewSet(viewsets.ViewSet):
    def list(self, request):
        services = get_services()
        return Response(services)

class NetworkViewSet(viewsets.ModelViewSet):
    queryset = Network.objects.all()
    serializer_class = NetworkSerializer