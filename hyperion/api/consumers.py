# hyperion/api/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils import get_processes, get_services, get_network_usage, stop_process, start_service, stop_service, restart_service

class ProcessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_processes()

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
        
        await self.send_processes()

    async def send_processes(self):
        processes = get_processes()
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
        await self.send_network_usage()

    async def disconnect(self, close_code):
        pass

    async def send_network_usage(self):
        network_usage = get_network_usage()
        await self.send(text_data=json.dumps(network_usage))