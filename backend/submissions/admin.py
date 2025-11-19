"""
Admin configuration for Submission models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Submission, Authorship, Revision, ManuscriptFile


class AuthorshipInline(admin.TabularInline):
    """Inline admin for authors."""
    model = Authorship
    extra = 1
    fields = ['author_order', 'full_name', 'email', 'affiliation', 'is_corresponding', 'user']
    autocomplete_fields = ['user']


class ManuscriptFileInline(admin.TabularInline):
    """Inline admin for files."""
    model = ManuscriptFile
    extra = 0
    fields = ['file_type', 'original_filename', 'file_size', 'uploaded_at']
    readonly_fields = ['uploaded_at']


class RevisionInline(admin.TabularInline):
    """Inline admin for revisions."""
    model = Revision
    extra = 0
    fields = ['revision_number', 'created_by', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """Admin interface for Submission model."""
    
    list_display = [
        'title_short',
        'submitting_author',
        'status_badge',
        'author_count',
        'file_count',
        'created_at',
        'submitted_at'
    ]
    
    list_filter = [
        'status',
        'created_at',
        'submitted_at'
    ]
    
    search_fields = [
        'title',
        'abstract',
        'submitting_author__email',
        'submitting_author__full_name'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'submitted_at'
    ]
    
    fieldsets = [
        ('Basic Information', {
            'fields': ['id', 'title', 'abstract', 'submitting_author']
        }),
        ('Status', {
            'fields': ['status', 'current_revision']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'submitted_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    inlines = [AuthorshipInline, RevisionInline, ManuscriptFileInline]
    
    autocomplete_fields = ['submitting_author']
    
    date_hierarchy = 'created_at'
    
    def title_short(self, obj):
        """Truncated title for list display."""
        return obj.title[:60] + '...' if len(obj.title) > 60 else obj.title
    title_short.short_description = 'Title'
    
    def status_badge(self, obj):
        """Colored status badge."""
        colors = {
            'DRAFT': '#6c757d',
            'SUBMITTED': '#007bff',
            'UNDER_REVIEW': '#17a2b8',
            'REVISION_NEEDED': '#ffc107',
            'REVISION_SUBMITTED': '#28a745',
            'ACCEPTED': '#28a745',
            'REJECTED': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def author_count(self, obj):
        """Number of authors."""
        return obj.authorship_set.count()
    author_count.short_description = 'Authors'
    
    def file_count(self, obj):
        """Number of files."""
        return obj.files.count()
    file_count.short_description = 'Files'


@admin.register(Authorship)
class AuthorshipAdmin(admin.ModelAdmin):
    """Admin interface for Authorship model."""
    
    list_display = [
        'full_name',
        'email',
        'submission_short',
        'author_order',
        'is_corresponding',
        'has_user'
    ]
    
    list_filter = [
        'is_corresponding',
        'created_at'
    ]
    
    search_fields = [
        'full_name',
        'email',
        'affiliation',
        'submission__title'
    ]
    
    autocomplete_fields = ['submission', 'user']
    
    def submission_short(self, obj):
        """Truncated submission title."""
        return obj.submission.title[:40] + '...' if len(obj.submission.title) > 40 else obj.submission.title
    submission_short.short_description = 'Submission'
    
    def has_user(self, obj):
        """Whether author is a registered user."""
        return '✓' if obj.user else '✗'
    has_user.short_description = 'Registered'


@admin.register(Revision)
class RevisionAdmin(admin.ModelAdmin):
    """Admin interface for Revision model."""
    
    list_display = [
        'submission_short',
        'revision_number',
        'created_by',
        'created_at',
        'has_response'
    ]
    
    list_filter = [
        'created_at',
        'revision_number'
    ]
    
    search_fields = [
        'submission__title',
        'created_by__email',
        'response_to_reviewers'
    ]
    
    readonly_fields = ['id', 'created_at']
    
    autocomplete_fields = ['submission', 'created_by']
    
    date_hierarchy = 'created_at'
    
    def submission_short(self, obj):
        """Truncated submission title."""
        return obj.submission.title[:40] + '...' if len(obj.submission.title) > 40 else obj.submission.title
    submission_short.short_description = 'Submission'
    
    def has_response(self, obj):
        """Whether revision has reviewer response."""
        return '✓' if obj.response_to_reviewers else '✗'
    has_response.short_description = 'Has Response'


@admin.register(ManuscriptFile)
class ManuscriptFileAdmin(admin.ModelAdmin):
    """Admin interface for ManuscriptFile model."""
    
    list_display = [
        'original_filename',
        'file_type',
        'submission_short',
        'revision_number',
        'file_size_mb',
        'uploaded_at'
    ]
    
    list_filter = [
        'file_type',
        'uploaded_at',
        'mime_type'
    ]
    
    search_fields = [
        'original_filename',
        'submission__title',
        'file_path'
    ]
    
    readonly_fields = [
        'id',
        'uploaded_at',
        'file_size_mb'
    ]
    
    autocomplete_fields = ['submission', 'revision', 'uploaded_by']
    
    date_hierarchy = 'uploaded_at'
    
    def submission_short(self, obj):
        """Truncated submission title."""
        return obj.submission.title[:30] + '...' if len(obj.submission.title) > 30 else obj.submission.title
    submission_short.short_description = 'Submission'
    
    def revision_number(self, obj):
        """Revision number."""
        return obj.revision.revision_number
    revision_number.short_description = 'Rev #'
    
    def file_size_mb(self, obj):
        """File size in MB."""
        return f"{obj.file_size / (1024 * 1024):.2f} MB"
    file_size_mb.short_description = 'Size'
