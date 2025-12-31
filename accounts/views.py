# accounts/views.py
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework.views import APIView

class LoginView(APIView):
    def post(self, request):
        identifier = request.data.get("identifier")
        password = request.data.get("password")

        user = authenticate(username=identifier, password=password)

        if user:
            return Response({
                "id": user.id,
                "username": user.username,
                "avatar": user.avatar.url if user.avatar else None
            })
        return Response({"error": "Invalid credentials"}, status=400)
class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)
