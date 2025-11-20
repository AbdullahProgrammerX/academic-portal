"""
Submission API Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .models import Submission, Authorship, ManuscriptFile
from .serializers import (
    SubmissionListSerializer,
    SubmissionDetailSerializer,
    SubmissionCreateSerializer,
    AuthorshipSerializer,
    ManuscriptFileSerializer,
    MetadataExtractionResultSerializer
)
from tasks.tasks import extract_metadata_task


class SubmissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Submission CRUD operations
    
    list: Get all submissions for current user
    retrieve: Get single submission detail
    create: Create new DRAFT submission
    update: Update submission (only if DRAFT)
    partial_update: Partial update
    destroy: Delete submission (only if DRAFT)
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'manuscript_type', 'subject_area']
    
    def get_queryset(self):
        """Return submissions for current user"""
        return Submission.objects.filter(
            submitting_author=self.request.user
        ).select_related('submitting_author', 'current_revision').prefetch_related('authorships')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return SubmissionListSerializer
        elif self.action == 'create':
            return SubmissionCreateSerializer
        return SubmissionDetailSerializer
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser, JSONParser])
    def start(self, request):
        """
        POST /api/submissions/start/
        
        Start new submission with DOCX file upload and metadata extraction
        """
        try:
            # Get file or S3 key
            uploaded_file = request.FILES.get('file')
            s3_key = request.data.get('s3_key')
            
            if not uploaded_file and not s3_key:
                return Response(
                    {'error': 'Either file or s3_key must be provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create DRAFT submission
            submission = Submission.objects.create(
                submitting_author=request.user,
                status='DRAFT',
                title='Extracting...',  # Temporary
                manuscript_type=request.data.get('manuscript_type', 'RESEARCH_ARTICLE')
            )
            
            # Handle file upload
            manuscript_file = None
            temp_file_path = None
            
            if uploaded_file:
                # Validate file type
                if not uploaded_file.name.endswith('.docx'):
                    submission.delete()
                    return Response(
                        {'error': 'Only .docx files are supported'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Save file temporarily for extraction
                import os
                from django.conf import settings
                
                # Create temp directory if not exists
                temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', str(submission.id))
                os.makedirs(temp_dir, exist_ok=True)
                
                # Save file temporarily
                temp_file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_file_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # Create ManuscriptFile record
                manuscript_file = ManuscriptFile.objects.create(
                    submission=submission,
                    revision=None,  # Will be set after first revision
                    file_type='MANUSCRIPT',
                    file_path=temp_file_path,  # Local path for now
                    file_size=uploaded_file.size,
                    is_current_version=True
                )
            
            # Trigger Celery task for metadata extraction
            task = extract_metadata_task.delay(
                submission_id=str(submission.id),
                file_id=str(manuscript_file.id) if manuscript_file else None,
                s3_key=s3_key
            )
            
            return Response({
                'submission_id': str(submission.id),
                'task_id': task.id,
                'message': 'Metadata extraction started'
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            import traceback
            print("="*80)
            print("ERROR in start() view:")
            print(traceback.format_exc())
            print("="*80)
            return Response(
                {'error': str(e), 'traceback': traceback.format_exc()},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        """
        POST /api/submissions/start/
        
        Start new submission with DOCX file upload and metadata extraction
        
        Input:
            - file: DOCX file (multipart upload) OR
            - s3_key: S3 key (if pre-uploaded to S3)
        
        Output:
            {
                'submission_id': UUID,
                'task_id': Celery task ID,
                'message': 'Extraction started'
            }
        
        Flow:
            1. Create DRAFT Submission
            2. Upload file to S3 (or use existing s3_key)
            3. Trigger extract_metadata_task (Celery)
            4. Return immediately with task_id
            5. Frontend polls /api/submissions/extraction-status/{task_id}/
        """
        # Get file or S3 key
        uploaded_file = request.FILES.get('file')
        s3_key = request.data.get('s3_key')
        
        if not uploaded_file and not s3_key:
            return Response(
                {'error': 'Either file or s3_key must be provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create DRAFT submission
        submission = Submission.objects.create(
            submitting_author=request.user,
            status='DRAFT',
            title='Extracting...',  # Temporary
            manuscript_type=request.data.get('manuscript_type', 'RESEARCH_ARTICLE')
        )
        
        # Handle file upload
        manuscript_file = None
        temp_file_path = None
        
        if uploaded_file:
            # Validate file type
            if not uploaded_file.name.endswith('.docx'):
                submission.delete()
                return Response(
                    {'error': 'Only .docx files are supported'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save file temporarily for extraction
            import os
            from django.conf import settings
            
            # Create temp directory if not exists
            temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp', str(submission.id))
            os.makedirs(temp_dir, exist_ok=True)
            
            # Save file temporarily
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Create ManuscriptFile record
            manuscript_file = ManuscriptFile.objects.create(
                submission=submission,
                revision=None,  # Will be set after first revision
                file_type='MANUSCRIPT',
                file_path=temp_file_path,  # Local path for now
                file_size=uploaded_file.size,
                is_current_version=True
            )
        
        # Trigger Celery task for metadata extraction
        task = extract_metadata_task.delay(
            submission_id=str(submission.id),
            file_id=str(manuscript_file.id) if manuscript_file else None,
            s3_key=s3_key
        )
        
        return Response({
            'submission_id': str(submission.id),
            'task_id': task.id,
            'message': 'Metadata extraction started'
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'], url_path='extraction-status/(?P<task_id>[^/.]+)')
    def extraction_status(self, request, task_id=None):
        """
        GET /api/submissions/extraction-status/{task_id}/
        
        Check status of metadata extraction task
        
        Returns:
            {
                'state': 'PENDING' | 'SUCCESS' | 'FAILURE',
                'result': {...} if SUCCESS,
                'error': str if FAILURE
            }
        """
        from celery.result import AsyncResult
        
        task_result = AsyncResult(task_id)
        
        if task_result.state == 'PENDING':
            return Response({
                'state': 'PENDING',
                'message': 'Extraction in progress...'
            })
        elif task_result.state == 'SUCCESS':
            return Response({
                'state': 'SUCCESS',
                'result': task_result.result
            })
        else:
            return Response({
                'state': 'FAILURE',
                'error': str(task_result.info)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        POST /api/submissions/{id}/submit/
        
        Submit a DRAFT submission (change status to SUBMITTED)
        
        Validation:
            - Must be DRAFT
            - Must have title, abstract
            - Must have at least one author
        """
        submission = self.get_object()
        
        # Validate
        if submission.status != 'DRAFT':
            return Response(
                {'error': 'Only DRAFT submissions can be submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not submission.title or not submission.abstract:
            return Response(
                {'error': 'Title and abstract are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not submission.authorships.exists():
            return Response(
                {'error': 'At least one author is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Change status to SUBMITTED
        submission.status = 'SUBMITTED'
        submission.save()
        
        # TODO: Create initial Revision
        # TODO: Send notification email
        
        serializer = self.get_serializer(submission)
        return Response(serializer.data)


class AuthorshipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing authors on a submission
    
    list: Get all authors for a submission
    create: Add author to submission
    update: Update author details
    destroy: Remove author from submission
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = AuthorshipSerializer
    
    def get_queryset(self):
        """Return authorships for submissions owned by current user"""
        return Authorship.objects.filter(
            submission__submitting_author=self.request.user
        ).select_related('author', 'submission')
    
    def perform_create(self, serializer):
        """Create authorship with automatic author_order"""
        submission = serializer.validated_data['submission']
        
        # Verify user owns this submission
        if submission.submitting_author != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You don't have permission to modify this submission")
        
        # Set author_order to next available number
        max_order = submission.authorships.count()
        serializer.save(author_order=max_order + 1)

