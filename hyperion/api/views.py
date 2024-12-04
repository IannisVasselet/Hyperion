# api/views.py
from django.shortcuts import render
from django.core.serializers import serialize
import json

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Process, Service, Network, CPUUsage, MemoryUsage, NetworkUsage
from .serializers import ProcessSerializer, ServiceSerializer, NetworkSerializer
from .utils import get_processes, stop_process, change_process_priority, get_services, execute_ssh_command
from .tasks import send_slack_notification, send_email_notification

class ProcessViewSet(viewsets.ViewSet):
    def list(self, request):
        processes = get_processes()
        return Response(processes)

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