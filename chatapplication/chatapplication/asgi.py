"""
ASGI config for chatapplication project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatapplication.settings')

# If channels is installed, try to use Channels' ProtocolTypeRouter and include websocket routing.
try:
	from channels.routing import ProtocolTypeRouter # type: ignore
	from channels.auth import AuthMiddlewareStack # type: ignore
	from django.urls import re_path,path
	from ..routing import websocket_urlpatterns

	application = ProtocolTypeRouter({
		'http': get_asgi_application(),
		'websocket': AuthMiddlewareStack(URLRouter(websocket_urlpatterns)), # type: ignore
	})
except Exception:
	# Channels not installed or routing issue — fallback to standard ASGI app
	application = get_asgi_application()
