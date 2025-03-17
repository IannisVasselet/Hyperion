# hyperion/asgi.py
import os

# Définir DJANGO_SETTINGS_MODULE AVANT les autres imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyperion.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from api.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hyperion.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})