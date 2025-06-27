from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import serializers

User = get_user_model()

# Serializer for creating a user
class CreateUserSerializer(serializers.Serializer):
    firstName = serializers.CharField()
    lastName = serializers.CharField()
    userName = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()
    group = serializers.ListField(child=serializers.CharField(), required=False)

    def create(self, validated_data):
        from django.utils.crypto import get_random_string
        from django.core.mail import send_mail

        password = get_random_string(length=12)
        user = User.objects.create_user(
            username=validated_data['userName'],
            first_name=validated_data['firstName'],
            last_name=validated_data['lastName'],
            email=validated_data['email'],
            role=validated_data['role'],
            password=password
        )

        groups = validated_data.get('group', [])
        for group_name in groups:
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

        subject = "Your Account Credentials"
        message = f"""Hi {user.first_name},

Your account has been created.

Username: {user.username}
Password: {password}

Please login and change your password if this is your first time.

Regards,
Admin
"""
        send_mail(subject, message, None, [user.email])
        return user

# Serializer for retrieving user info
class UserSerializer(serializers.ModelSerializer):
    group = serializers.SerializerMethodField()
    userId = serializers.SerializerMethodField()
    firstName = serializers.CharField(source='first_name')
    lastName = serializers.CharField(source='last_name')
    userName = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ['userId', 'firstName', 'lastName', 'userName', 'email', 'role', 'group', 'date_joined']

    def get_group(self, obj):
        return [g.name for g in obj.groups.all()]

    def get_userId(self, obj):
        return str(obj.id)
