"""
URL configuration for user authentication.
"""
from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    RefreshTokenView,
    CurrentUserView,
    ChangePasswordView,
    ORCIDAuthorizeView,
    ORCIDCallbackView,
    ProfileView
)

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    
    # User profile
    path('me/', CurrentUserView.as_view(), name='current_user'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # ORCID OAuth
    path('orcid/authorize/', ORCIDAuthorizeView.as_view(), name='orcid_authorize'),
    path('orcid/callback/', ORCIDCallbackView.as_view(), name='orcid_callback'),
]
