"""
DRF Serializers for Submission Management
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Submission, Authorship, Revision, ManuscriptFile


User = get_user_model()


class AuthorshipSerializer(serializers.ModelSerializer):
    """Serializer for Authorship (registered or external authors)"""
    
    author_name = serializers.SerializerMethodField()
    author_email = serializers.SerializerMethodField()
    
    class Meta:
        model = Authorship
        fields = [
            'id',
            'author',
            'author_order',
            'author_name',
            'author_email',
            'external_author_name',
            'external_author_email',
            'affiliation',
            'orcid',
            'is_corresponding',
            'contribution_statement',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_author_name(self, obj):
        """Get author name (from User or external)"""
        if obj.author:
            return f"{obj.author.first_name} {obj.author.last_name}".strip() or obj.author.email
        return obj.external_author_name
    
    def get_author_email(self, obj):
        """Get author email (from User or external)"""
        if obj.author:
            return obj.author.email
        return obj.external_author_email


class ManuscriptFileSerializer(serializers.ModelSerializer):
    """Serializer for ManuscriptFile"""
    
    file_size_mb = serializers.SerializerMethodField()
    
    class Meta:
        model = ManuscriptFile
        fields = [
            'id',
            'file_type',
            'file_path',
            'file_size',
            'file_size_mb',
            'uploaded_at',
            'is_current_version'
        ]
        read_only_fields = ['id', 'uploaded_at']
    
    def get_file_size_mb(self, obj):
        """Convert file size to MB"""
        if obj.file_size:
            return round(obj.file_size / (1024 * 1024), 2)
        return None


class RevisionSerializer(serializers.ModelSerializer):
    """Serializer for Revision (version history)"""
    
    files = ManuscriptFileSerializer(many=True, read_only=True, source='manuscriptfile_set')
    
    class Meta:
        model = Revision
        fields = [
            'id',
            'revision_number',
            'submitted_at',
            'decision',
            'decision_date',
            'editor_notes',
            'response_to_reviewers',
            'files'
        ]
        read_only_fields = ['id', 'submitted_at']


class SubmissionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for submission list view"""
    
    submitting_author_name = serializers.SerializerMethodField()
    author_count = serializers.SerializerMethodField()
    current_revision_number = serializers.SerializerMethodField()
    
    class Meta:
        model = Submission
        fields = [
            'id',
            'title',
            'status',
            'manuscript_type',
            'submitted_at',
            'submitting_author_name',
            'author_count',
            'current_revision_number',
            'created_at',
            'updated_at'
        ]
    
    def get_submitting_author_name(self, obj):
        """Get submitting author name"""
        if obj.submitting_author:
            return f"{obj.submitting_author.first_name} {obj.submitting_author.last_name}".strip() \
                   or obj.submitting_author.email
        return None
    
    def get_author_count(self, obj):
        """Get total number of authors"""
        return obj.authorships.count()
    
    def get_current_revision_number(self, obj):
        """Get current revision number"""
        if obj.current_revision:
            return obj.current_revision.revision_number
        return None


class SubmissionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single submission view"""
    
    authors = AuthorshipSerializer(many=True, read_only=True, source='authorships')
    revisions = RevisionSerializer(many=True, read_only=True, source='revision_set')
    files = ManuscriptFileSerializer(many=True, read_only=True, source='manuscriptfile_set')
    submitting_author_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Submission
        fields = [
            'id',
            'title',
            'abstract',
            'manuscript_type',
            'subject_area',
            'status',
            'submitting_author',
            'submitting_author_name',
            'current_revision',
            'submitted_at',
            'authors',
            'revisions',
            'files',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_submitting_author_name(self, obj):
        """Get submitting author name"""
        if obj.submitting_author:
            return f"{obj.submitting_author.first_name} {obj.submitting_author.last_name}".strip() \
                   or obj.submitting_author.email
        return None


class SubmissionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new submission (DRAFT)"""
    
    class Meta:
        model = Submission
        fields = [
            'title',
            'abstract',
            'manuscript_type',
            'subject_area'
        ]
    
    def create(self, validated_data):
        """Create DRAFT submission"""
        # Set submitting author from request user
        user = self.context['request'].user
        validated_data['submitting_author'] = user
        validated_data['status'] = 'DRAFT'
        
        return super().create(validated_data)


class MetadataExtractionResultSerializer(serializers.Serializer):
    """Serializer for metadata extraction result"""
    
    submission_id = serializers.UUIDField()
    task_id = serializers.CharField()
    extracted = serializers.DictField(child=serializers.JSONField(), required=False)
    errors = serializers.ListField(child=serializers.CharField(), required=False)
    warnings = serializers.ListField(child=serializers.CharField(), required=False)
    success = serializers.BooleanField()
    
    # Preview data
    title = serializers.CharField(allow_null=True, required=False)
    abstract = serializers.CharField(allow_null=True, required=False)
    keywords = serializers.ListField(child=serializers.CharField(), required=False)
    authors = serializers.ListField(child=serializers.DictField(), required=False)
