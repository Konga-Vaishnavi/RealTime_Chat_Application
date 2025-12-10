from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json

from chatapplication.users.models import Chats


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = int(self.scope['url_route']['kwargs']['user_id'])
        self.other_user_id = int(self.scope['url_route']['kwargs']['other_user_id'])

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Create a group name that is unique and consistent for both users
        user_ids = sorted([self.user_id, self.other_user_id])
        self.group_name = f'chat_{user_ids[0]}_{user_ids[1]}'

        # Join group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, 
                                               self.channel_name,
                                                self.room_group_name,
                                               )

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
        except Exception:
            return
        username = data['username']
        content = data.get('content')
        sender_id = data.get('user_id')

        if not content or not sender_id:
            return

        # Save message to DB
        chat = await sync_to_async(Chats.objects.create)(username_id=sender_id, content=content, activity_status=True)

        message = {
            'id': chat.id,
            'user_id': sender_id,
            'content': chat.content,
            'timestamp': chat.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }

        # Broadcast to group (both users will get this message)
        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat_message',
            'message': message,
            'username': username,
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'username':event['username'],
            'message':event['message']

        }))
