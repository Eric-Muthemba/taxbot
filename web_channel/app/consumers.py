import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
from jobs.utilities import state_machine
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['channel_id']
            await self.join_room(str(self.room_name))
        except:

            self.room_name = None

        await self.accept()

    async def disconnect(self, close_code):
        await self.close()
        raise StopConsumer()

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            # Assuming delimiter is "|delimiter|"
            delimiter = b"|delimiter|"
            delimiter_index = bytes_data.find(delimiter)

            # Extract JSON and file data
            json_buffer = bytes_data[:delimiter_index]
            file_buffer = bytes_data[delimiter_index + len(delimiter):]

            # Decode JSON data
            message = json.loads(json_buffer.decode('utf-8'))

            if self.room_name == None:
                await self.join_room(str(message['id']))

            await self.channel_layer.group_send(self.room_name, {'type': 'chat_message', 'message': {"message":message,"file":file_buffer}})

        else:
            data = json.loads(text_data)
            if "acknowledged" not in text_data:
                message = data['message']
                if message["is_start"]:
                    await self.join_room(str(message['id']))
                if self.room_name == None:
                    await self.join_room(str(message['id']))

                await self.channel_layer.group_send(self.room_name, {'type': 'chat_message', 'message': message})


    async def join_room(self, room_name):
        if self.room_name:
            await self.channel_layer.group_discard(
                self.room_name,
                self.channel_name
            )

        self.room_name = room_name
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

    async def chat_message(self, event):
        message = event['message']
        if "file" in message:
            response = await (await self.itax(message=message["message"],file=message["file"]))
        else:
            response = await (await self.itax(message=message))

        # Send message to WebSocket
        await self.send(text_data=json.dumps(response))


    @database_sync_to_async
    async def itax(self, message,file=None):
        return state_machine(channel="Web", message=message, file=file)
