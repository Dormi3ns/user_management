from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser

class SignInView(APIView):
    def post(self, request):
        email_or_username = request.data.get('emailOrUsername')
        password = request.data.get('password')

        # Try to fetch by username first, then by email
        user = authenticate(username=email_or_username, password=password)

        if user is None:
            try:
                user_obj = CustomUser.objects.get(email=email_or_username)
                user = authenticate(username=user_obj.username, password=password)
            except CustomUser.DoesNotExist:
                pass

        if user is None:
            return Response({
                "status": "error",
                "message": "Invalid credentials"
            }, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)

        return Response({
            "status": "success",
            "message": "Login successful",
            "data": {
                "userId": str(user.id),
                "firstName": user.first_name,
                "lastName": user.last_name,
                "email": user.email,
                "role": user.role if hasattr(user, 'role') else "",
                "group": [g.name for g in user.groups.all()],
                "token": str(refresh.access_token),
                "expiresIn": 3600,
                "firstLogin": getattr(user, 'first_login', False)
            }
        })
