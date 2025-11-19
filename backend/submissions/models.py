"""
Submission models for manuscript management.

Models:
- Submission: Main manuscript submission with versioning
- Authorship: Authors (both registered users and external)
- ManuscriptFile: File metadata with S3 pointers
- Revision: Version history and reviewer responses
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
import uuid

User = get_user_model()


class SubmissionStatus(models.TextChoices):
    """
    Submission workflow states.
    PostgreSQL stores these as VARCHAR with CHECK constraint.
    """
    DRAFT = 'DRAFT', _('Draft')
    SUBMITTED = 'SUBMITTED', _('Submitted')
    UNDER_REVIEW = 'UNDER_REVIEW', _('Under Review')
    REVISION_NEEDED = 'REVISION_NEEDED', _('Revision Needed')
    REVISION_SUBMITTED = 'REVISION_SUBMITTED', _('Revision Submitted')
    ACCEPTED = 'ACCEPTED', _('Accepted')
    REJECTED = 'REJECTED', _('Rejected')


class FileType(models.TextChoices):
    """
    Manuscript file types.
    """
    MANUSCRIPT = 'MANUSCRIPT', _('Manuscript Document')
    COVER_LETTER = 'COVER_LETTER', _('Cover Letter')
    SUPPLEMENTARY = 'SUPPLEMENTARY', _('Supplementary Material')
    FIGURE = 'FIGURE', _('Figure')
    TABLE = 'TABLE', _('Table')
    REVISION = 'REVISION', _('Revision Document')
    RESPONSE = 'RESPONSE', _('Response to Reviewers')


class Submission(models.Model):
    """
    Main manuscript submission model.
    
    Features:
    - UUID primary key for security
    - Full-text search on title/abstract (GIN index)
    - Versioning via current_revision FK
    - Optimized queries with select_related/prefetch_related
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text=_('Unique submission identifier')
    )
    
    title = models.TextField(
        _('title'),
        help_text=_('Manuscript title')
    )
    
    abstract = models.TextField(
        _('abstract'),
        help_text=_('Manuscript abstract')
    )
    
    submitting_author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='submissions',
        verbose_name=_('submitting author'),
        help_text=_('User who submitted the manuscript')
    )
    
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.DRAFT,
        db_index=True,
        help_text=_('Current submission status')
    )
    
    # Versioning
    current_revision = models.ForeignKey(
        'Revision',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name=_('current revision'),
        help_text=_('Latest revision of this submission')
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        db_index=True,
        help_text=_('When draft was created')
    )
    
    submitted_at = models.DateTimeField(
        _('submitted at'),
        null=True,
        blank=True,
        db_index=True,
        help_text=_('When manuscript was first submitted')
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('Last modification time')
    )
    
    # Full-text search vector (populated by trigger or update)
    search_vector = SearchVectorField(
        null=True,
        blank=True,
        help_text=_('Full-text search index')
    )
    
    class Meta:
        db_table = 'submissions'
        verbose_name = _('submission')
        verbose_name_plural = _('submissions')
        ordering = ['-created_at']
        indexes = [
            # B-tree indexes for filtering
            models.Index(fields=['submitting_author', 'status'], name='sub_author_status_idx'),
            models.Index(fields=['status', '-created_at'], name='sub_status_created_idx'),
            models.Index(fields=['-submitted_at'], name='sub_submitted_idx'),
            
            # GIN index for full-text search on title + abstract
            GinIndex(fields=['search_vector'], name='sub_search_vector_idx'),
        ]
    
    def __str__(self):
        return f"{self.title[:50]} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Auto-set submitted_at when status changes to SUBMITTED."""
        if self.status == SubmissionStatus.SUBMITTED and not self.submitted_at:
            from django.utils import timezone
            self.submitted_at = timezone.now()
        super().save(*args, **kwargs)


class Authorship(models.Model):
    """
    Author metadata for submissions.
    Supports both registered users and external authors.
    
    Composite ordering ensures proper author sequence.
    """
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='authorship_set',
        verbose_name=_('submission')
    )
    
    # Optional FK for registered users
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authorships',
        verbose_name=_('registered user'),
        help_text=_('If author is a registered user')
    )
    
    # Required fields for all authors
    full_name = models.CharField(
        _('full name'),
        max_length=255,
        help_text=_('Author full name')
    )
    
    email = models.EmailField(
        _('email'),
        help_text=_('Author email address')
    )
    
    affiliation = models.CharField(
        _('affiliation'),
        max_length=500,
        blank=True,
        help_text=_('Author institutional affiliation')
    )
    
    orcid_id = models.CharField(
        _('ORCID iD'),
        max_length=19,
        blank=True,
        help_text=_('Author ORCID identifier (e.g., 0000-0002-1825-0097)')
    )
    
    is_corresponding = models.BooleanField(
        _('is corresponding author'),
        default=False,
        help_text=_('Whether this author is the corresponding author')
    )
    
    author_order = models.PositiveSmallIntegerField(
        _('author order'),
        validators=[MinValueValidator(1)],
        help_text=_('Author position in author list (1-based)')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    
    class Meta:
        db_table = 'authorships'
        verbose_name = _('authorship')
        verbose_name_plural = _('authorships')
        ordering = ['submission', 'author_order']
        unique_together = [
            ('submission', 'author_order'),  # Prevent duplicate positions
        ]
        indexes = [
            models.Index(fields=['submission', 'author_order'], name='auth_sub_order_idx'),
            models.Index(fields=['email'], name='auth_email_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(author_order__gte=1),
                name='auth_order_positive'
            )
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.submission.title[:30]})"


class Revision(models.Model):
    """
    Revision history for submissions.
    Tracks version numbers and reviewer responses.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='revisions',
        verbose_name=_('submission')
    )
    
    revision_number = models.PositiveSmallIntegerField(
        _('revision number'),
        validators=[MinValueValidator(1)],
        help_text=_('Revision sequence number (1 = original submission)')
    )
    
    response_to_reviewers = models.TextField(
        _('response to reviewers'),
        blank=True,
        help_text=_('Author response to reviewer comments')
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='revisions_created',
        verbose_name=_('created by'),
        help_text=_('User who created this revision')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        db_table = 'revisions'
        verbose_name = _('revision')
        verbose_name_plural = _('revisions')
        ordering = ['submission', '-revision_number']
        unique_together = [
            ('submission', 'revision_number'),
        ]
        indexes = [
            models.Index(fields=['submission', '-revision_number'], name='rev_sub_num_idx'),
        ]
    
    def __str__(self):
        return f"Rev {self.revision_number} - {self.submission.title[:30]}"


class ManuscriptFile(models.Model):
    """
    File metadata model.
    Stores only S3 pointers, not actual file data.
    
    File storage strategy:
    - S3 key format: submissions/{submission_id}/revisions/{revision_id}/{file_type}/{filename}
    - Database stores only metadata and paths
    - Actual files in S3 bucket
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    submission = models.ForeignKey(
        Submission,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_('submission')
    )
    
    revision = models.ForeignKey(
        Revision,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name=_('revision'),
        help_text=_('Revision this file belongs to')
    )
    
    file_path = models.CharField(
        _('file path'),
        max_length=500,
        help_text=_('S3 key or storage path')
    )
    
    original_filename = models.CharField(
        _('original filename'),
        max_length=255,
        help_text=_('Original uploaded filename')
    )
    
    file_type = models.CharField(
        _('file type'),
        max_length=20,
        choices=FileType.choices,
        help_text=_('Type of manuscript file')
    )
    
    file_size = models.BigIntegerField(
        _('file size'),
        help_text=_('File size in bytes')
    )
    
    mime_type = models.CharField(
        _('MIME type'),
        max_length=100,
        blank=True,
        help_text=_('File MIME type (e.g., application/pdf)')
    )
    
    file_order = models.PositiveSmallIntegerField(
        _('file order'),
        default=1,
        validators=[MinValueValidator(1)],
        help_text=_('Display order within file type')
    )
    
    uploaded_at = models.DateTimeField(
        _('uploaded at'),
        auto_now_add=True,
        db_index=True
    )
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='uploaded_files',
        verbose_name=_('uploaded by')
    )
    
    class Meta:
        db_table = 'manuscript_files'
        verbose_name = _('manuscript file')
        verbose_name_plural = _('manuscript files')
        ordering = ['submission', 'revision', 'file_type', 'file_order']
        indexes = [
            models.Index(fields=['submission', 'revision'], name='file_sub_rev_idx'),
            models.Index(fields=['file_type'], name='file_type_idx'),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(file_size__gt=0),
                name='file_size_positive'
            )
        ]
    
    def __str__(self):
        return f"{self.original_filename} ({self.get_file_type_display()})"
