"""
Serializers for user authentication and profile management.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    """
    
    class Meta:
        model = UserProfile
        fields = [
            'phone',
            'country',
            'research_interests',
            'expertise_areas',
            'publications_count',
            'email_notifications',
            'submission_updates',
            'review_reminders',
            'newsletter_subscription',
            'public_profile',
            'show_email'
        ]
        read_only_fields = ['publications_count']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (read-only for profile display).
    """
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'orcid_id',
            'affiliation',
            'bio',
            'profile_picture_url',
            'role',
            'email_verified',
            'orcid_verified',
            'date_joined',
            'profile'
        ]
        read_only_fields = [
            'id',
            'email',
            'role',
            'email_verified',
            'orcid_verified',
            'date_joined'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Validates:
    - Email uniqueness
    - Password strength
    - Password confirmation match
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'password_confirm', 'affiliation']
        extra_kwargs = {
            'email': {'required': True},
            'full_name': {'required': True}
        }
    
    def validate_email(self, value):
        """
        Validate email uniqueness (case-insensitive).
        """
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this email address already exists."
            )
        return value.lower()
    
    def validate(self, attrs):
        """
        Validate password confirmation match.
        """
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm': "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create user with hashed password.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            affiliation=validated_data.get('affiliation', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Authenticates user with email and password.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """
        Validate credentials and authenticate user.
        """
        email = attrs.get('email', '').lower()
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.',
                    code='authorization'
                )
        else:
            raise serializers.ValidationError(
                'Must include "email" and "password".',
                code='authorization'
            )
        
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """
        Validate old password is correct.
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value
    
    def validate(self, attrs):
        """
        Validate new passwords match.
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "New password fields didn't match."
            })
        return attrs
    
    def save(self, **kwargs):
        """
        Update user password.
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """
    profile = UserProfileSerializer()
    
    class Meta:
        model = User
        fields = ['full_name', 'affiliation', 'bio', 'profile_picture_url', 'profile']
    
    def update(self, instance, validated_data):
        """
        Update user and profile data.
        """
        profile_data = validated_data.pop('profile', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update profile fields
        if profile_data and hasattr(instance, 'profile'):
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance


class ORCIDConnectSerializer(serializers.Serializer):
    """
    Serializer for ORCID OAuth callback.
    """
    code = serializers.CharField(required=True)
    state = serializers.CharField(required=False)
    
    def validate_code(self, value):
        """
        Validate authorization code.
        """
        if not value:
            raise serializers.ValidationError('Authorization code is required.')
        return value
