"""
File Management API Views
"""
import boto3
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings


class GetPresignedUploadView(APIView):
    """
    POST /api/files/presigned-url/
    
    Generate pre-signed URL for direct S3 upload from frontend
    
    This approach keeps large file uploads off Django server,
    improving performance and scalability.
    
    Input:
        {
            'filename': 'manuscript.docx',
            'file_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_size': 1048576  # bytes
        }
    
    Output:
        {
            'upload_url': 'https://s3.amazonaws.com/...',
            'fields': {...},  # Form fields for POST request
            's3_key': 'manuscripts/uuid/manuscript.docx'
        }
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        filename = request.data.get('filename')
        file_type = request.data.get('file_type')
        file_size = request.data.get('file_size')
        
        if not filename:
            return Response(
                {'error': 'filename is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file type
        allowed_types = [
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
            'application/pdf',
            'application/msword'  # .doc
        ]
        
        if file_type and file_type not in allowed_types:
            return Response(
                {'error': 'Unsupported file type. Only DOCX, PDF, and DOC are allowed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 50MB for now)
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size and file_size > max_size:
            return Response(
                {'error': f'File size exceeds maximum allowed size of {max_size / (1024 * 1024)}MB'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate unique S3 key
        unique_id = str(uuid.uuid4())
        s3_key = f'manuscripts/{request.user.id}/{unique_id}/{filename}'
        
        # Generate pre-signed POST URL
        # Note: This requires AWS credentials in settings
        # For development, we'll return a mock response
        
        if hasattr(settings, 'AWS_S3_BUCKET_NAME') and settings.AWS_S3_BUCKET_NAME:
            try:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )
                
                # Generate pre-signed POST
                presigned_post = s3_client.generate_presigned_post(
                    Bucket=settings.AWS_S3_BUCKET_NAME,
                    Key=s3_key,
                    Fields={'Content-Type': file_type},
                    Conditions=[
                        {'Content-Type': file_type},
                        ['content-length-range', 0, max_size]
                    ],
                    ExpiresIn=3600  # 1 hour
                )
                
                return Response({
                    'upload_url': presigned_post['url'],
                    'fields': presigned_post['fields'],
                    's3_key': s3_key,
                    'expires_in': 3600
                })
            except Exception as e:
                return Response(
                    {'error': f'Failed to generate pre-signed URL: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            # Development mode: return mock response
            # Frontend will use direct file upload instead
            return Response({
                'upload_url': None,
                'fields': None,
                's3_key': s3_key,
                'message': 'S3 not configured. Use direct file upload to /api/submissions/start/',
                'development_mode': True
            })


class DownloadFileView(APIView):
    """
    GET /api/files/download/{file_id}/
    
    Generate pre-signed URL for downloading file from S3
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, file_id):
        from .models import ManuscriptFile
        from django.shortcuts import get_object_or_404
        
        # Get file record
        manuscript_file = get_object_or_404(ManuscriptFile, id=file_id)
        
        # Verify user has permission to access this file
        if manuscript_file.submission.submitting_author != request.user:
            return Response(
                {'error': 'You do not have permission to access this file'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Generate pre-signed download URL
        if hasattr(settings, 'AWS_S3_BUCKET_NAME') and settings.AWS_S3_BUCKET_NAME:
            try:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )
                
                download_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={
                        'Bucket': settings.AWS_S3_BUCKET_NAME,
                        'Key': manuscript_file.file_path
                    },
                    ExpiresIn=3600  # 1 hour
                )
                
                return Response({
                    'download_url': download_url,
                    'filename': manuscript_file.file_path.split('/')[-1],
                    'expires_in': 3600
                })
            except Exception as e:
                return Response(
                    {'error': f'Failed to generate download URL: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response({
                'error': 'S3 not configured',
                'development_mode': True
            }, status=status.HTTP_501_NOT_IMPLEMENTED)
