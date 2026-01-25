import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import Conversation, Message

class PrivateChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        print("🔥 WebSocket connect llamado")
        print("URL:", self.scope["path"])

        self.user = self.scope["user"]
        print("👤 USER:", self.user)

        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.user_id = int(self.user.id)
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

        messages, _ = await self.get_chat_history(offset=0, limit=15)

        for msg in messages:
            await self.send_json({
                "type":"chat_message",
                "message": msg.content,
                "sender_id": msg.sender_id,
                "timestamp": msg.timestamp.isoformat(),
                "is_history": True,
            })

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

            print("🔍 RECEIVE_JSON LLAMADO:", data)

            if data.get("type") == "load_more":
                offset = data.get("offset",0)
                limit = data.get("limit",15)

                print(f"📦 Cargando mensajes: offset={offset}, limit={limit}")

                messages, has_more = await self.get_chat_history(offset=offset, limit=limit)

                print(f"✅ Mensajes obtenidos: {len(messages)}")
                print(f"🔍 has_more: {has_more}")

                await self.send_json({
                    "type": "history_batch",
                    "messages": [
                        {
                            "message":msg.content,
                            "sender_id": msg.sender_id,
                            "timestamp": msg.timestamp.isoformat(),
                            "id": msg.id
                        } for msg in messages
                    ],
                    "has_more": has_more
                })
                print("📤 history_batch enviado")
                return

            if "message" in data:
                message = data["message"]

                print("📩 receive:", text_data)

                saved_msg = await self.save_message(self.conversation.id, self.user_id, message)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": message,
                        "sender_id": self.user_id,
                        "timestamp": saved_msg.timestamp.isoformat(),
                        "id": saved_msg.id
                    }
                )

        except Exception as e:
            print("❌ ERROR EN receive:", e)
            await self.close()

    async def chat_message(self, event):
        try:
            print("📤 chat_message:", event)

            import datetime
            timestamp = event.get("timestamp", datetime.datetime.now().isoformat())

            await self.send(text_data=json.dumps({
                "message": event["message"],
                "sender_id": event["sender_id"],
                "timestamp": timestamp,
                "is_history": False
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
        return message

    @database_sync_to_async
    def get_chat_history(self, offset=0, limit=15):

        qs = (
            self.conversation.messages
            .select_related("sender")
            .order_by("-timestamp")
        )
        total_count = qs.count()

        message = list(qs[offset : offset + limit])

        has_more = offset + len(message) < total_count

        return message[::-1], has_more
    