from django.urls import path
from .views import SignInView

urlpatterns = [
    path('auth/signin', SignInView.as_view(), name='sign-in'),
]
