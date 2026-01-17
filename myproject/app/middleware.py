from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from rest_framework.authtoken.models import Token

class TokenAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        scope["user"] = AnonymousUser()

        query_string = scope.get("query_string",b"").decode()
        params = parse_qs(query_string)

        token_key = params.get("token",[None])[0]

        if token_key:
            user = await self.get_user(token_key)
            if user:
                scope["user"] = user

        return await super().__call__(scope,receive,send)
    
    @database_sync_to_async
    def get_user(self,token_key):
        try:
            token = Token.objects.select_related("user").get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return None
