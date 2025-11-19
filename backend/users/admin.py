"""
Django admin configuration for User models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin for User model with email-based authentication.
    """
    
    # List display
    list_display = (
        'email',
        'full_name',
        'role',
        'is_active',
        'email_verified',
        'orcid_verified',
        'date_joined'
    )
    
    list_filter = (
        'role',
        'is_active',
        'is_staff',
        'is_superuser',
        'email_verified',
        'orcid_verified',
        'date_joined'
    )
    
    search_fields = ('email', 'full_name', 'orcid_id', 'affiliation')
    
    ordering = ('-date_joined',)
    
    # Fieldsets for detail view
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal Info'), {
            'fields': ('full_name', 'affiliation', 'bio', 'profile_picture_url')
        }),
        (_('ORCID Integration'), {
            'fields': (
                'orcid_id',
                'orcid_verified',
                'orcid_access_token',
                'orcid_refresh_token',
                'orcid_token_expires_at'
            ),
            'classes': ('collapse',)
        }),
        (_('Permissions'), {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'email_verified',
                'groups',
                'user_permissions'
            )
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    # Fieldsets for add view
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'role', 'is_active')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')
    
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for UserProfile model.
    """
    
    list_display = (
        'user',
        'country',
        'publications_count',
        'email_notifications',
        'public_profile'
    )
    
    list_filter = (
        'country',
        'email_notifications',
        'public_profile',
        'newsletter_subscription'
    )
    
    search_fields = ('user__email', 'user__full_name', 'phone', 'country')
    
    fieldsets = (
        (_('User'), {
            'fields': ('user',)
        }),
        (_('Contact Information'), {
            'fields': ('phone', 'country')
        }),
        (_('Research Profile'), {
            'fields': ('research_interests', 'expertise_areas', 'publications_count')
        }),
        (_('Notification Preferences'), {
            'fields': (
                'email_notifications',
                'submission_updates',
                'review_reminders',
                'newsletter_subscription'
            )
        }),
        (_('Privacy Settings'), {
            'fields': ('public_profile', 'show_email')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    readonly_fields = ('created_at', 'updated_at')
