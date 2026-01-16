from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from .serializers import UserListSerializer
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.shortcuts import get_object_or_404

from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

from django.contrib.auth.models import User
from rest_framework.generics import ListAPIView

@api_view(['POST'])
def login(resquest):
    user = get_object_or_404(User, username=resquest.data['username'])

    if not user.check_password(resquest.data['password']):
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
    
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)

    return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def register(resquest):
    serielizer = UserSerializer(data=resquest.data)

    if serielizer.is_valid():
        serielizer.save()
        
        user = User.objects.get(username=serielizer.data['username'])
        user.set_password(resquest.data['password'])
        user.save()

        token = Token.objects.create(user=user)
        return Response({'token': token.key, 'user': serielizer.data}, status=status.HTTP_201_CREATED)

    return Response(serielizer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def profile(resquest):

    print(resquest.user.id)
    serializer = UserSerializer(instance=resquest.user)

    return Response(serializer.data, status=status.HTTP_200_OK)

class UserListView(ListAPIView):
    serializer_class = UserListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        token = Token.objects.get(user=request.user)
        token.delete()
        return Response({"message":"Logout exitoso"}, status=status.HTTP_200_OK)
    except:
        return Response({"error":"No se encontro un token activo"}, status=status.HTTP_400_BAD_REQUEST)