"""
Celery tasks for async processing.
"""
import os
import tempfile
from celery import shared_task
from django.core.files.storage import default_storage

from submissions.docx_extractor import extract_metadata_from_docx as extract_docx_metadata
from submissions.models import Submission, Authorship, ManuscriptFile
from users.models import User


@shared_task(bind=True, max_retries=3)
def extract_metadata_task(self, submission_id: str, file_id: str = None, s3_key: str = None):
    """
    Extract metadata from uploaded DOCX file (async)
    
    Args:
        submission_id: UUID of DRAFT Submission
        file_id: ManuscriptFile UUID (if already uploaded)
        s3_key: S3 key (if using direct S3 upload)
    
    Returns:
        {
            'submission_id': str,
            'extracted': {
                'title': str or None,
                'abstract': str or None,
                'keywords': List[str],
                'authors': List[Dict]
            },
            'errors': List[str],
            'warnings': List[str],
            'success': bool
        }
    """
    try:
        submission = Submission.objects.get(id=submission_id)
        
        # Get file path (either from ManuscriptFile or S3 key)
        if file_id:
            manuscript_file = ManuscriptFile.objects.get(id=file_id)
            file_path = manuscript_file.file_path
        elif s3_key:
            file_path = s3_key
        else:
            return {
                'submission_id': str(submission_id),
                'extracted': {},
                'errors': ['NO_FILE_PROVIDED'],
                'warnings': [],
                'success': False
            }
        
        # Download file from S3 to temporary location
        temp_file = None
        try:
            # If using S3, download to temp file
            if default_storage.exists(file_path):
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')
                
                with default_storage.open(file_path, 'rb') as f:
                    temp_file.write(f.read())
                temp_file.close()
                
                local_path = temp_file.name
            else:
                # File is already local path
                local_path = file_path
            
            # Extract metadata
            result = extract_docx_metadata(local_path)
            
            # Update submission with extracted data
            if result['success']:
                if result['title']:
                    submission.title = result['title']
                if result['abstract']:
                    submission.abstract = result['abstract']
                
                submission.save()
                
                # Create authorship entries for detected authors
                if result['authors']:
                    for order, author_data in enumerate(result['authors'], start=1):
                        # Try to find existing user by email
                        user = None
                        if author_data.get('email'):
                            user = User.objects.filter(email=author_data['email']).first()
                        
                        # Create authorship
                        Authorship.objects.create(
                            submission=submission,
                            author_order=order,
                            author=user,
                            external_author_name=author_data.get('name') if not user else None,
                            external_author_email=author_data.get('email') if not user else None,
                            affiliation=author_data.get('affiliation', ''),
                            is_corresponding=order == 1  # First author as corresponding
                        )
            
            return {
                'submission_id': str(submission_id),
                'extracted': {
                    'title': result['title'],
                    'abstract': result['abstract'],
                    'keywords': result['keywords'],
                    'authors': result['authors']
                },
                'errors': result['errors'],
                'warnings': result['warnings'],
                'success': result['success']
            }
            
        finally:
            # Cleanup temp file
            if temp_file and os.path.exists(temp_file.name):
                os.unlink(temp_file.name)
                
    except Submission.DoesNotExist:
        return {
            'submission_id': str(submission_id),
            'extracted': {},
            'errors': ['SUBMISSION_NOT_FOUND'],
            'warnings': [],
            'success': False
        }
    except Exception as e:
        # Retry on transient errors
        try:
            raise self.retry(exc=e, countdown=60)
        except self.MaxRetriesExceededError:
            return {
                'submission_id': str(submission_id),
                'extracted': {},
                'errors': ['EXTRACTION_FAILED'],
                'warnings': [str(e)],
                'success': False
            }


@shared_task
def extract_metadata_from_pdf(file_id):
    """Extract metadata from PDF document (future implementation)."""
    pass


@shared_task
def send_notification_email(user_id, subject, message):
    """Send notification email to user."""
    pass
