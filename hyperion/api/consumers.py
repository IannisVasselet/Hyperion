# hyperion/api/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .utils import get_processes, get_services, get_network_usage

class ProcessConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_processes()

    async def disconnect(self, close_code):
        pass

    async def send_processes(self):
        processes = get_processes()
        await self.send(text_data=json.dumps(processes))

class ServiceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send_services()

    async def disconnect(self, close_code):
        pass

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