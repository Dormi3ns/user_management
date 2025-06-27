from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

from users.models import CustomUser
from users.serializers import CreateUserSerializer, UserSerializer


# ✅ Create Account View
class CreateAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateUserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            if CustomUser.objects.filter(email=email).exists():
                return Response({
                    "status": "error",
                    "message": "Email already exists"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response({
                "status": "success",
                "message": "Account successfully created"
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# ✅ Sign In View
class SignInView(APIView):
    def post(self, request):
        email_or_username = request.data.get('emailOrUsername')
        password = request.data.get('password')

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


# ✅ Get All Users View
class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({"status": "success", "data": serializer.data}, status=200)


# ✅ Lock User Account
class LockUserView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.is_active = False
            user.save()
            return Response({
                "status": "success",
                "message": "User account has been locked"
            })
        except CustomUser.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User not found or unauthorized action"
            }, status=status.HTTP_404_NOT_FOUND)


# ✅ Reset Password
class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            new_password = get_random_string(length=12)
            user.set_password(new_password)
            user.first_login = True
            user.save()

            send_mail(
                subject="Your password has been reset",
                message=f"Your new password is: {new_password}",
                from_email=None,
                recipient_list=[user.email]
            )

            return Response({
                "status": "success",
                "message": "Password has been reset"
            })
        except CustomUser.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User not found or unauthorized action"
            }, status=status.HTTP_404_NOT_FOUND)


# ✅ Set New Password on First Login
class SetNewPasswordView(APIView):
    def patch(self, request):
        user_id = request.data.get("userId")
        temp_pass = request.data.get("temporaryPassword")
        new_pass = request.data.get("newPassword")

        try:
            user = CustomUser.objects.get(id=user_id)
            if not user.check_password(temp_pass):
                return Response({
                    "status": "error",
                    "message": "Temporary password is incorrect or expired"
                }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_pass)
            user.first_login = False
            user.save()

            return Response({
                "status": "success",
                "message": "Password has been set successfully"
            })
        except CustomUser.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)
