from django.urls import path
from channels.routing import URLRouter, ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from .consumers import NotificationConsumer

application = ProtocolTypeRouter({
	'websocket': AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter([
		path('notify', NotificationConsumer.as_asgi()),

	])))
})