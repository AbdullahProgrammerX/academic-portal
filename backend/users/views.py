"""
Authentication views for user registration, login, and ORCID OAuth.

Endpoints:
- POST /api/auth/register/ - User registration
- POST /api/auth/login/ - User login (returns JWT tokens)
- POST /api/auth/logout/ - User logout (blacklist refresh token)
- POST /api/auth/refresh/ - Refresh access token
- GET /api/auth/me/ - Get current user profile
- PUT /api/auth/me/ - Update current user profile
- POST /api/auth/change-password/ - Change password
- GET /api/auth/orcid/authorize/ - ORCID OAuth authorization URL
- POST /api/auth/orcid/callback/ - ORCID OAuth callback handler
"""
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import transaction
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
import logging
import secrets

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserProfileUpdateSerializer,
    ChangePasswordSerializer,
    ORCIDConnectSerializer
)
from .orcid_service import orcid_service

User = get_user_model()
logger = logging.getLogger(__name__)


@method_decorator(ratelimit(key='ip', rate='3/h', method='POST', block=True), name='dispatch')
class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    Rate limited to 3 registrations per hour per IP.
    
    POST /api/auth/register/
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            with transaction.atomic():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                user_serializer = UserSerializer(user)
                
                logger.info(f"User registered: {user.email}")
                
                response = Response({
                    'user': user_serializer.data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    },
                    'message': 'Registration successful.'
                }, status=status.HTTP_201_CREATED)
                
                # Set refresh token as HTTP-only cookie
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),
                    httponly=True,
                    secure=False,  # Set to True in production with HTTPS
                    samesite='Lax',
                    max_age=60 * 60 * 24 * 7,  # 7 days
                    domain=None  # Allow localhost and 127.0.0.1
                )
                
                return response
                
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            return Response({
                'error': 'Registration failed.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(ratelimit(key='ip', rate='5/15m', method='POST', block=True), name='dispatch')
class LoginView(APIView):
    """
    User login endpoint.
    Rate limited to 5 attempts per 15 minutes per IP.
    
    POST /api/auth/login/
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        user_serializer = UserSerializer(user)
        
        response = Response({
            'user': user_serializer.data,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_200_OK)
        
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='Lax',
            max_age=60 * 60 * 24 * 7,  # 7 days
            domain=None  # Allow localhost and 127.0.0.1
        )
        
        logger.info(f"User logged in: {user.email}")
        return response


class LogoutView(APIView):
    """User logout endpoint."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh') or request.COOKIES.get('refresh_token')
            
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            response = Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
            response.delete_cookie('refresh_token')
            
            logger.info(f"User logged out: {request.user.email}")
            return response
            
        except (TokenError, InvalidToken):
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    """
    Refresh access token using refresh token from HTTP-only cookie.
    
    POST /api/auth/refresh/
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        # Get refresh token from cookie or request body
        refresh_token = request.COOKIES.get('refresh_token') or request.data.get('refresh')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token not found.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            
            response = Response({
                'access': access_token
            }, status=status.HTTP_200_OK)
            
            # If rotation is enabled, update the cookie with new refresh token
            if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
                response.set_cookie(
                    key='refresh_token',
                    value=str(refresh),
                    httponly=True,
                    secure=False,  # Set to True in production with HTTPS
                    samesite='Lax',
                    max_age=60 * 60 * 24 * 7,  # 7 days
                    domain=None  # Allow localhost and 127.0.0.1
                )
            
            return response
            
        except (TokenError, InvalidToken) as e:
            return Response({
                'error': 'Invalid or expired refresh token.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """Get or update current user profile."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return UserProfileUpdateSerializer
        return UserSerializer
    
    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """Change user password."""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        logger.info(f"Password changed: {request.user.email}")
        return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)


class ORCIDAuthorizeView(APIView):
    """Generate ORCID OAuth authorization URL."""
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        state = secrets.token_urlsafe(32)
        request.session['orcid_state'] = state
        auth_url = orcid_service.get_authorization_url(state=state)
        
        return Response({'authorization_url': auth_url, 'state': state})


class ORCIDCallbackView(APIView):
    """Handle ORCID OAuth callback."""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = ORCIDConnectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        state = serializer.validated_data.get('state')
        
        session_state = request.session.get('orcid_state')
        if state and session_state and state != session_state:
            return Response({'error': 'Invalid state.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token_response = orcid_service.exchange_code_for_token(code)
            orcid_id = token_response.get('orcid')
            
            if not orcid_id:
                raise ValueError('ORCID iD not found')
            
            try:
                profile_data = orcid_service.get_user_profile(orcid_id, token_response['access_token'])
            except Exception:
                profile_data = None
            
            user_data = orcid_service.parse_user_data(token_response, profile_data)
            
            with transaction.atomic():
                user, created = User.objects.get_or_create(orcid_id=orcid_id, defaults=user_data)
                
                if not created:
                    for key, value in user_data.items():
                        if key.startswith('orcid_'):
                            setattr(user, key, value)
                    user.save()
                
                refresh = RefreshToken.for_user(user)
                user_serializer = UserSerializer(user)
                
                logger.info(f"ORCID login: {user.email}, new={created}")
                
                return Response({
                    'user': user_serializer.data,
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    },
                    'is_new_user': created
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            logger.error(f"ORCID callback failed: {str(e)}")
            return Response({'error': 'ORCID authentication failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileView(APIView):
    """
    GET /api/profile/ - Get current user's profile
    PUT /api/profile/ - Update current user's profile
    
    Returns profile data with completion percentage.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Retrieve current user profile with completion percentage.
        """
        user = request.user
        serializer = UserProfileUpdateSerializer(user)
        
        # Calculate profile completion percentage
        completion = self._calculate_completion(user)
        
        return Response({
            'user': serializer.data,
            'completion_percentage': completion['percentage'],
            'missing_fields': completion['missing']
        }, status=status.HTTP_200_OK)
    
    @method_decorator(ratelimit(key='user', rate='10/m', method='PUT'))
    def put(self, request):
        """
        Update current user profile.
        Soft validation: allows partial updates.
        """
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        
        # Recalculate profile completion
        completion = self._calculate_completion(user)
        
        # Update profile_completed flag if 100%
        if completion['percentage'] == 100 and user.profile:
            user.profile.profile_completed = True
            user.profile.save(update_fields=['profile_completed'])
        
        logger.info(f"Profile updated: {user.email}, completion={completion['percentage']}%")
        
        return Response({
            'user': serializer.data,
            'completion_percentage': completion['percentage'],
            'missing_fields': completion['missing'],
            'message': 'Profile updated successfully.'
        }, status=status.HTTP_200_OK)
    
    def _calculate_completion(self, user):
        """
        Calculate profile completion percentage.
        
        Required fields for 100% completion:
        - full_name
        - affiliation
        - bio (at least 50 chars)
        - country
        - research_interests (at least 1)
        - orcid_id
        """
        required_fields = {
            'full_name': bool(user.full_name),
            'affiliation': bool(user.affiliation),
            'bio': bool(user.bio and len(user.bio) >= 50),
            'country': bool(user.profile and user.profile.country),
            'research_interests': bool(user.profile and user.profile.research_interests and len(user.profile.research_interests) > 0),
            'orcid_id': bool(user.orcid_id)
        }
        
        completed = sum(required_fields.values())
        total = len(required_fields)
        percentage = int((completed / total) * 100)
        
        missing = [field for field, is_complete in required_fields.items() if not is_complete]
        
        return {
            'percentage': percentage,
            'missing': missing
        }

