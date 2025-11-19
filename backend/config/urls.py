"""
URL configuration for editorial_system project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from django.http import JsonResponse

def api_root(request):
    """API root endpoint"""
    return JsonResponse({
        'message': 'Editorial System API',
        'version': '1.0',
        'status': 'operational',
        'endpoints': {
            'admin': '/admin/',
            'auth': '/api/auth/',
            'submissions': '/api/submissions/',
            'files': '/api/files/',
            'revisions': '/api/revisions/',
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/auth/', include('users.urls')),
    path('api/submissions/', include('submissions.urls')),
    path('api/revisions/', include('revisions.urls')),
    path('api/files/', include('files.urls')),
    
    # JWT token refresh
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
