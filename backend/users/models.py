"""
User models with ORCID integration.

Custom User model using AbstractBaseUser with:
- UUID as primary key for scalability
- Email as username (unique identifier)
- ORCID ID for academic identity verification
- Secure password hashing (Argon2)
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import EmailValidator


class UserManager(BaseUserManager):
    """
    Custom user manager for email-based authentication.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        
        Args:
            email: User's email address (used as username)
            password: Raw password (will be hashed)
            **extra_fields: Additional user fields
            
        Returns:
            User instance
            
        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        
        Args:
            email: Superuser's email address
            password: Raw password (will be hashed)
            **extra_fields: Additional user fields
            
        Returns:
            User instance with superuser privileges
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email-as-username and ORCID integration.
    
    Primary Key: UUID (for distributed systems and security)
    Username: Email (unique, indexed)
    Authentication: Email + Password or ORCID OAuth2
    
    Fields:
        id: UUID primary key
        email: Unique email address (username)
        full_name: User's display name
        orcid_id: ORCID identifier (optional, unique)
        role: User role (author, reviewer, editor, admin)
        is_active: Account activation status
        is_staff: Admin panel access
        email_verified: Email verification status
        orcid_verified: ORCID verification status
    """
    
    class Role(models.TextChoices):
        """User roles with different permissions"""
        AUTHOR = 'author', _('Author')
        REVIEWER = 'reviewer', _('Reviewer')
        EDITOR = 'editor', _('Editor')
        ADMIN = 'admin', _('Administrator')
    
    # Primary key: UUID for scalability and security
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_('Unique identifier')
    )
    
    # Authentication fields
    email = models.EmailField(
        _('email address'),
        unique=True,
        db_index=True,
        validators=[EmailValidator()],
        help_text=_('Email address (used for login)')
    )
    
    # Profile fields
    full_name = models.CharField(
        _('full name'),
        max_length=255,
        blank=True,
        help_text=_('User display name')
    )
    
    # ORCID integration
    orcid_id = models.CharField(
        _('ORCID iD'),
        max_length=19,  # Format: 0000-0002-1825-0097
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text=_('ORCID identifier (e.g., 0000-0002-1825-0097)')
    )
    
    orcid_access_token = models.CharField(
        max_length=500,
        blank=True,
        help_text=_('ORCID OAuth2 access token (encrypted in production)')
    )
    
    orcid_refresh_token = models.CharField(
        max_length=500,
        blank=True,
        help_text=_('ORCID OAuth2 refresh token (encrypted in production)')
    )
    
    orcid_token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('ORCID token expiration time')
    )
    
    # Additional profile
    affiliation = models.CharField(
        _('affiliation'),
        max_length=255,
        blank=True,
        help_text=_('Current institution/organization')
    )
    
    bio = models.TextField(
        _('biography'),
        blank=True,
        help_text=_('Short biography or research interests')
    )
    
    profile_picture_url = models.URLField(
        _('profile picture'),
        blank=True,
        help_text=_('URL to profile picture')
    )
    
    # Role & Permissions
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Role.choices,
        default=Role.AUTHOR,
        db_index=True,
        help_text=_('User role in the system')
    )
    
    # Status flags
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Designates whether this user should be treated as active.')
    )
    
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into admin site.')
    )
    
    email_verified = models.BooleanField(
        _('email verified'),
        default=False,
        help_text=_('Email verification status')
    )
    
    orcid_verified = models.BooleanField(
        _('ORCID verified'),
        default=False,
        help_text=_('ORCID verification status')
    )
    
    # Timestamps
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now
    )
    
    last_login = models.DateTimeField(
        _('last login'),
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Manager
    objects = UserManager()
    
    # Authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']  # Required for createsuperuser command
    
    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email'], name='users_email_idx'),
            models.Index(fields=['orcid_id'], name='users_orcid_idx'),
            models.Index(fields=['role'], name='users_role_idx'),
            models.Index(fields=['is_active', 'email'], name='users_active_email_idx'),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """Return the full name for the user."""
        return self.full_name or self.email
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.full_name.split()[0] if self.full_name else self.email.split('@')[0]
    
    @property
    def is_orcid_authenticated(self):
        """Check if user has valid ORCID authentication."""
        if not self.orcid_id or not self.orcid_access_token:
            return False
        if self.orcid_token_expires_at and self.orcid_token_expires_at < timezone.now():
            return False
        return True
    
    @property
    def has_verified_identity(self):
        """Check if user has verified email or ORCID."""
        return self.email_verified or self.orcid_verified
    
    def can_submit_manuscript(self):
        """Check if user can submit manuscripts (requires verified identity)."""
        return self.has_verified_identity and self.is_active
    
    def can_review(self):
        """Check if user can review manuscripts."""
        return self.role in [self.Role.REVIEWER, self.Role.EDITOR, self.Role.ADMIN] and self.is_active
    
    def can_edit(self):
        """Check if user can act as editor."""
        return self.role in [self.Role.EDITOR, self.Role.ADMIN] and self.is_active


class UserProfile(models.Model):
    """
    Extended user profile information.
    
    Stores additional user data that's not critical for authentication
    but useful for personalization and analytics.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True
    )
    
    # Contact information
    phone = models.CharField(
        _('phone number'),
        max_length=20,
        blank=True,
        help_text=_('Contact phone number')
    )
    
    country = models.CharField(
        _('country'),
        max_length=100,
        blank=True,
        help_text=_('Country of residence')
    )
    
    # Research profile
    research_interests = models.JSONField(
        _('research interests'),
        default=list,
        blank=True,
        help_text=_('List of research interests/keywords')
    )
    
    expertise_areas = models.JSONField(
        _('expertise areas'),
        default=list,
        blank=True,
        help_text=_('Areas of expertise for reviewing')
    )
    
    publications_count = models.IntegerField(
        _('publications count'),
        default=0,
        help_text=_('Number of publications')
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(
        _('email notifications'),
        default=True,
        help_text=_('Receive email notifications')
    )
    
    submission_updates = models.BooleanField(
        _('submission updates'),
        default=True,
        help_text=_('Notifications for submission status changes')
    )
    
    review_reminders = models.BooleanField(
        _('review reminders'),
        default=True,
        help_text=_('Reminders for pending reviews')
    )
    
    newsletter_subscription = models.BooleanField(
        _('newsletter subscription'),
        default=False,
        help_text=_('Subscribe to newsletter')
    )
    
    # Privacy settings
    public_profile = models.BooleanField(
        _('public profile'),
        default=True,
        help_text=_('Make profile publicly visible')
    )
    
    show_email = models.BooleanField(
        _('show email'),
        default=False,
        help_text=_('Display email on public profile')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    
    def __str__(self):
        return f"Profile of {self.user.email}"
