"""Users app configuration."""
"""
Users app configuration.
"""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for users application."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'User Management'
    
    def ready(self):
        """
        Import signal handlers when app is ready.
        """
        import users.signals  # noqa: F401


    def ready(self):
        import users.signals
