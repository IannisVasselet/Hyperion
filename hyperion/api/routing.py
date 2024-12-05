# api/routing.py
from django.urls import path
from .consumers import ProcessConsumer, ServiceConsumer, NetworkConsumer, CPUConsumer

websocket_urlpatterns = [
    path('ws/processes/', ProcessConsumer.as_asgi()),
    path('ws/services/', ServiceConsumer.as_asgi()),
    path('ws/networks/', NetworkConsumer.as_asgi()),
    path('ws/cpu/', CPUConsumer.as_asgi()),
]