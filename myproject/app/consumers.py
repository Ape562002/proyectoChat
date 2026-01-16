import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import Conversation, Message

class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("🔥 WebSocket connect llamado")
        print("URL:", self.scope["path"])

        self.user_id = int(self.scope["url_route"]["kwargs"]["sender_id"])
        self.other_user_id = int(self.scope["url_route"]["kwargs"]["receiver_id"])

        self.room_group_name = f"private_chat_{min(self.user_id, self.other_user_id)}_{max(self.user_id, self.other_user_id)}"

        self.conversation = await self.get_or_create_conversation(
            self.user_id,
            self.other_user_id
        )
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        print("🔥 CONNECT OK", self.room_group_name)

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        print("❌ DISCONNECT")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data["message"]

            print("📩 receive:", text_data)

            await self.save_message(self.conversation.id, self.user_id, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "sender_id": self.user_id
                }
            )
        except Exception as e:
            print("❌ ERROR EN receive:", e)
            await self.close()

    async def chat_message(self, event):
        try:
            print("📤 chat_message:", event)
            await self.send(text_data=json.dumps({
                "message": event["message"],
                "sender_id": event["sender_id"],
            }))
        except Exception as e:
            print("❌ ERROR EN chat_message:", e)
    
    @sync_to_async
    def get_or_create_conversation(self,user_id, other_user_id):
        users = User.objects.filter(id__in=[user_id, other_user_id])
        conversation = (
            Conversation.objects
            .filter(participants=users[0])
            .filter(participants=users[1])
            .first()
        )
        
        if not conversation:
            conversation = Conversation.objects.create()
            conversation.participants.add(*users)


        return conversation
    
    @sync_to_async
    def save_message(self,conversation,user_id,content):
        message = Message.objects.create(
            conversation_id=conversation,
            sender_id=user_id,
            content=content,
        )