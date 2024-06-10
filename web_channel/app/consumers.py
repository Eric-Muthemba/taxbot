import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.http import SimpleCookie
from asgiref.sync import sync_to_async,async_to_sync
from jobs.utilities import state_machine
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        headers = dict(self.scope['headers'])
        if b'cookie' in headers:
            cookie_header = headers[b'cookie'].decode()
            cookies = SimpleCookie(cookie_header)
        else:
            cookies = {}

        channel_id = cookies.get('channel_id').value if 'channel_id' in cookies else None

        if channel_id is not None:
            self.room_name = channel_id
            self.room_group_name = 'chat_%s' % channel_id
            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.channel_layer.group_send(self.room_group_name, {'type': 'chat_message', 'message': message })

    async def chat_message(self, event):
        message = event['message']
        response = await (await self.itax(message))
        # Send message to WebSocket
        await self.send(text_data=json.dumps(response))

    @database_sync_to_async
    async def itax(self, message):
        return state_machine(channel="Web",message=message,channel_id=self.room_name)
