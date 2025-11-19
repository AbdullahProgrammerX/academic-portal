"""
Custom exception handler for DRF with detailed error messages.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': True,
            'message': str(exc),
            'details': response.data,
            'status_code': response.status_code
        }
        response.data = custom_response_data
    
    return response


def ratelimit_view(request, exception):
    """
    Custom rate limit error response.
    
    Returns HTTP 429 Too Many Requests with JSON error.
    """
    return JsonResponse({
        'error': True,
        'message': 'Too many requests. Please try again later.',
        'details': {
            'rate_limit': 'You have exceeded the rate limit for this endpoint.',
            'retry_after': '15 minutes'  # Generic message, actual time depends on endpoint
        },
        'status_code': 429
    }, status=429)

