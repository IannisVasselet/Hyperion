# hyperion/api/consumers.py
import json
import asyncio

from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps
from asgiref.sync import sync_to_async
from .utils import (
    get_processes, get_services, get_network_usage, 
    stop_process, start_service, stop_service, restart_service,
    block_ip, unblock_ip, block_port, get_network_interfaces
)

class ProcessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.is_connected = True
        asyncio.create_task(self.send_periodic_updates())

    async def disconnect(self, close_code):
        self.is_connected = False

    async def send_periodic_updates(self):
        while self.is_connected:
            await self.send_processes()
            await asyncio.sleep(1)  # Mise à jour toutes les secondes

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        pid = data.get('pid')
        
        if action == 'stop':
            success = stop_process(pid)
            await self.send(text_data=json.dumps({
                'status': 'success' if success else 'error',
                'action': 'stop',
                'pid': pid
            }))

    @sync_to_async
    def get_process_data(self):
        return get_processes()

    async def send_processes(self):
        processes = await self.get_process_data()
        await self.send(text_data=json.dumps(processes))

class ServiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_services()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        service_name = data.get('service')
        
        success = False
        if action == 'start':
            success = start_service(service_name)
        elif action == 'stop':
            success = stop_service(service_name)
        elif action == 'restart':
            success = restart_service(service_name)
            
        await self.send(text_data=json.dumps({
            'status': 'success' if success else 'error',
            'action': action,
            'service': service_name
        }))
        
        await self.send_services()

    async def send_services(self):
        services = get_services()
        await self.send(text_data=json.dumps(services))

class NetworkConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_network_status()

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')
        
        if action == 'block_ip':
            ip = data.get('ip_address')
            success = block_ip(ip)
        elif action == 'unblock_ip':
            ip = data.get('ip_address')
            success = unblock_ip(ip)
        elif action == 'block_port':
            port = data.get('port')
            protocol = data.get('protocol', 'tcp')
            success = block_port(port, protocol)
            
        await self.send(text_data=json.dumps({
            'status': 'success' if success else 'error',
            'action': action
        }))
        
        await self.send_network_status()

    @sync_to_async
    def get_network_usage_data(self):
        NetworkUsage = apps.get_model('api', 'NetworkUsage')
        return [
            {
                'recorded_at': network.recorded_at.isoformat(),
                'received': network.received,
                'sent': network.sent
            }
            for network in NetworkUsage.objects.order_by('-recorded_at')[:50]
        ]

    async def send_network_status(self):
        network_data = {
            'usage': await self.get_network_usage_data()
        }
        await self.send(text_data=json.dumps(network_data))