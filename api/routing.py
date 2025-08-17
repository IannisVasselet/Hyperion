# api/routing.py
from django.urls import path, re_path
from . import consumers
from .consumers import (
    ProcessConsumer, ServiceConsumer, NetworkConsumer,
    CPUConsumer, MemoryConsumer, FileSystemConsumer,
    ShellConsumer, StorageConsumer, TemperatureConsumer,
    SSHConsumer
    )

websocket_urlpatterns = [
    path('ws/processes/', ProcessConsumer.as_asgi()),
    path('ws/services/', ServiceConsumer.as_asgi()),
    path('ws/networks/', NetworkConsumer.as_asgi()),
    path('ws/cpu/', CPUConsumer.as_asgi()),
    path('ws/memory/', MemoryConsumer.as_asgi()),
    path('ws/files/', FileSystemConsumer.as_asgi()),
    path('ws/shell/', ShellConsumer.as_asgi()),
    path('ws/storage/', StorageConsumer.as_asgi()),
    path('ws/temperature/', TemperatureConsumer.as_asgi()),
    re_path('ws/ssh/$', consumers.SSHConsumer.as_asgi()),
]