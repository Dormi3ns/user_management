from django.urls import path
from .views import (
    CreateAccountView,
    SignInView,
    UserListView,
    LockUserView,
    ResetPasswordView,
    SetNewPasswordView,
)

urlpatterns = [
    path('createAccount', CreateAccountView.as_view(), name='create-account'),
    path('auth/signin', SignInView.as_view(), name='signin'),
    path('users', UserListView.as_view(), name='user-list'),
    path('users/<str:user_id>/lock', LockUserView.as_view(), name='lock-user'),
    path('users/<str:user_id>/reset-password', ResetPasswordView.as_view(), name='reset-password'),
    path('auth/set-new-password', SetNewPasswordView.as_view(), name='set-new-password'),
]
