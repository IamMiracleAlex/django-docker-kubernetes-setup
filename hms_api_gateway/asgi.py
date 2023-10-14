"""
ASGI config for hms_api_gateway project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter
from django.core.asgi import get_asgi_application
from .routing import application as websocket

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms_api_gateway.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": websocket,
    # Just HTTP for now. (We can add other protocols later.)
})
