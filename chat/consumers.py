from datetime import datetime
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import CustomUser, Message


class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def save_message(self, message, username):
        """Save given message to the database."""
        if message:
            room_id = int(self.room_id)
            user = CustomUser.objects.get(username=username).pk
            Message.objects.create(
                room_id=room_id,
                sender_id=user,
                content=message
            )
        content = {
            'message': message,
            'sender': username,
            'date': datetime.now().strftime('%b. %d, %Y, %H:%M %p')
        }
        return content

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['sender']
        new_message = await self.save_message(message, username)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': new_message['message'],
                'sender': new_message['sender'],
                'date': new_message['date']
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
