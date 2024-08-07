# import json
# from channels.generic.websocket import AsyncWebsocketConsumer


# class NotificationConsumer(AsyncWebsocketConsumer):
#     # async def connect(self):
#     #     self.group_name = "notifications_notifications"
#     #     await self.accept()

#     # async def disconnect(self, close_code):
#     #     pass

#     # async def receive(self, text_data):
#     #     data = json.loads(text_data)
#     #     await self.send(text_data=json.dumps({"message": "Notification received"}))
#     async def connect(self):
#         self.group_name = "notifications"
#         await self.channel_layer.group_add(self.group_name, self.channel_name)
#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.group_name, self.channel_name)

#     async def send_notification(self, event):
#         await self.send(text_data=json.dumps({"message": event["message"]}))


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Services


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.service_provider_id = self.scope["url_route"]["kwargs"][
            "service_provider_id"
        ]
        self.group_name = f"service_provider_{self.service_provider_id}"

        # Add this WebSocket connection to the group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove this WebSocket connection from the group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "send_notification",
                "message": message,
            },
        )

    async def send_notification(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
