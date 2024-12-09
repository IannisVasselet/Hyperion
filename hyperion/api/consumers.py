# hyperion/api/consumers.py
import asyncio
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.apps import apps


from .utils import (
    get_processes, get_services, stop_process, start_service, stop_service, restart_service,
    block_ip, unblock_ip, block_port, list_directory, get_storage_info, get_system_temperatures,
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
        self.is_connected = True
        asyncio.create_task(self.send_periodic_updates())

    async def disconnect(self, close_code):
        self.is_connected = False

    async def send_periodic_updates(self):
        while self.is_connected:
            await self.send_services()
            await asyncio.sleep(1)  # Update every second

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

    @sync_to_async
    def get_service_data(self):
        return get_services()

    async def send_services(self):
        services = await self.get_service_data()
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


class CPUConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.is_connected = True
        asyncio.create_task(self.send_periodic_updates())

    async def disconnect(self, close_code):
        self.is_connected = False

    @sync_to_async
    def get_cpu_data(self):
        CPUUsage = apps.get_model('api', 'CPUUsage')
        return [
            {
                'recorded_at': usage.recorded_at.isoformat(),
                'usage': usage.usage
            }
            for usage in CPUUsage.objects.order_by('-recorded_at')[:50]
        ]

    async def send_periodic_updates(self):
        while self.is_connected:
            await self.send_cpu_data()
            await asyncio.sleep(1)  # Update every second

    async def send_cpu_data(self):
        cpu_data = await self.get_cpu_data()
        await self.send(text_data=json.dumps({
            'type': 'cpu_usage',
            'data': cpu_data
        }))


class MemoryConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.is_connected = True
        asyncio.create_task(self.send_periodic_updates())

    async def disconnect(self, close_code):
        self.is_connected = False

    @sync_to_async
    def get_memory_data(self):
        MemoryUsage = apps.get_model('api', 'MemoryUsage')
        return [
            {
                'recorded_at': usage.recorded_at.isoformat(),
                'usage': usage.usage
            }
            for usage in MemoryUsage.objects.order_by('-recorded_at')[:50]
        ]

    async def send_periodic_updates(self):
        while self.is_connected:
            await self.send_memory_data()
            await asyncio.sleep(1)  # Update every second

    async def send_memory_data(self):
        memory_data = await self.get_memory_data()
        await self.send(text_data=json.dumps({
            'type': 'memory_usage',
            'data': memory_data
        }))


class FileSystemConsumer(AsyncWebsocketConsumer):
    async def execute_command(self, command):
        try:
            self.shell.stdin.write(f"{command}\n".encode())
            await self.shell.stdin.drain()
            stdout, stderr = await self.shell.communicate()

            # Create new shell process after command execution
            self.shell = await asyncio.create_subprocess_shell(
                '/bin/bash',
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            return stdout.decode() if stdout else stderr.decode()
        except Exception as e:
            return str(e)

    async def connect(self):
        await self.accept()
        self.current_path = '/'
        self.shell = await asyncio.create_subprocess_shell(
            '/bin/bash',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await self.send_file_list()

    @sync_to_async
    def get_directory_contents(self, path='/'):
        return list_directory(path)

    async def send_file_list(self, path='/'):
        files = await self.get_directory_contents(path)
        await self.send(text_data=json.dumps({
            'type': 'file_list',
            'data': files,
            'current_path': path
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'list':
            path = data.get('path', '/')
            self.current_path = path
            output = await self.execute_command(f"ls -la {path}")
            await self.send_file_list(path)

        elif action == 'cd':
            path = data.get('path', '/')
            self.current_path = path
            output = await self.execute_command(f"cd {path}")
            await self.send_file_list(path)

        elif action == 'delete':
            path = data.get('path')
            output = await self.execute_command(f"rm -rf {path}")
            await self.send_file_list(self.current_path)


class ShellConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.shell = await asyncio.create_subprocess_shell(
            '/bin/bash',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    async def disconnect(self, close_code):
        if hasattr(self, 'shell'):
            self.shell.terminate()
            await self.shell.wait()

    async def receive(self, text_data):
        data = json.loads(text_data)
        command = data.get('command')
        if command:
            try:
                # Write command to stdin
                self.shell.stdin.write(f"{command}\n".encode())
                await self.shell.stdin.drain()

                # Execute command and get complete output
                stdout, stderr = await self.shell.communicate(input=None)
                output = []

                if stdout:
                    output.extend(stdout.decode().splitlines())
                if stderr:
                    output.extend(stderr.decode().splitlines())

                # Recreate shell process for next command
                self.shell = await asyncio.create_subprocess_shell(
                    '/bin/bash',
                    stdin=asyncio.subprocess.PIPE,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

                # Send combined output
                await self.send(text_data=json.dumps({
                    'type': 'shell_output',
                    'output': '\n'.join(output)
                }))

            except Exception as e:
                await self.send(text_data=json.dumps({
                    'type': 'shell_output',
                    'output': f"Error: {str(e)}"
                }))


class StorageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.is_connected = True
        asyncio.create_task(self.send_periodic_updates())

    async def disconnect(self, close_code):
        self.is_connected = False

    @sync_to_async
    def get_storage_data(self):
        return get_storage_info()

    async def send_periodic_updates(self):
        while self.is_connected:
            data = await self.get_storage_data()
            await self.send(text_data=json.dumps({
                'type': 'storage_info',
                'data': data
            }))
            await asyncio.sleep(30)  # Update every 30 seconds

class TemperatureConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.is_connected = True
        asyncio.create_task(self.send_periodic_updates())

    async def disconnect(self, close_code):
        self.is_connected = False

    @sync_to_async
    def get_temperature_data(self):
        return get_system_temperatures()

    async def send_periodic_updates(self):
        while self.is_connected:
            data = await self.get_temperature_data()
            await self.send(text_data=json.dumps({
                'type': 'temperature_info',
                'data': data
            }))
            await asyncio.sleep(5)  # Update every 5 seconds
