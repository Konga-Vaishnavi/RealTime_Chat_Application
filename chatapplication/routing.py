from django.urls import re_path
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chatapplication.users import consumers
from users.consumers import ChatConsumer

websocket_urlpatterns = [
    
    re_path(r'ws/users/(?P<user_id>\d+)/(?P<other_user_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
]


application = ProtocolTypeRouter({
    # HTTP protocol will be handled by Django ASGI application in asgi.py
    'websocket': AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})
