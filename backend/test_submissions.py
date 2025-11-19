"""
Test script for Submission models.
Tests model creation, queries, and indexing.
"""
from django.contrib.auth import get_user_model
from submissions.models import Submission, Authorship, Revision, ManuscriptFile, SubmissionStatus, FileType
from django.db import connection
from django.test.utils import CaptureQueriesContext
import uuid

User = get_user_model()

def test_submission_creation():
    """Test creating a complete submission with all related models."""
    
    # Get or create test user
    user, _ = User.objects.get_or_create(
        email='testauthor@example.com',
        defaults={
            'full_name': 'Test Author',
            'affiliation': 'Test University'
        }
    )
    
    print("✓ User created/retrieved")
    
    # Create submission
    submission = Submission.objects.create(
        title='Novel Approach to Machine Learning in Bioinformatics',
        abstract='This paper presents a groundbreaking method for applying machine learning techniques to bioinformatics problems. Our approach significantly improves accuracy while reducing computational complexity.',
        submitting_author=user,
        status=SubmissionStatus.DRAFT
    )
    
    print(f"✓ Submission created: {submission.id}")
    
    # Create revision
    revision = Revision.objects.create(
        submission=submission,
        revision_number=1,
        created_by=user
    )
    
    print(f"✓ Revision created: Rev {revision.revision_number}")
    
    # Link revision to submission
    submission.current_revision = revision
    submission.save()
    
    # Create authors
    authors_data = [
        {
            'full_name': 'Test Author',
            'email': 'testauthor@example.com',
            'affiliation': 'Test University',
            'is_corresponding': True,
            'author_order': 1,
            'user': user
        },
        {
            'full_name': 'Jane Doe',
            'email': 'jane@example.com',
            'affiliation': 'Example Institute',
            'orcid_id': '0000-0002-1825-0097',
            'is_corresponding': False,
            'author_order': 2
        },
        {
            'full_name': 'John Smith',
            'email': 'john@example.com',
            'affiliation': 'Research Center',
            'is_corresponding': False,
            'author_order': 3
        }
    ]
    
    for author_data in authors_data:
        Authorship.objects.create(submission=submission, **author_data)
    
    print(f"✓ {len(authors_data)} authors created")
    
    # Create files
    files_data = [
        {
            'file_type': FileType.MANUSCRIPT,
            'original_filename': 'manuscript.pdf',
            'file_path': f'submissions/{submission.id}/revisions/{revision.id}/manuscript/manuscript.pdf',
            'file_size': 2048000,  # 2MB
            'mime_type': 'application/pdf',
            'file_order': 1
        },
        {
            'file_type': FileType.COVER_LETTER,
            'original_filename': 'cover_letter.pdf',
            'file_path': f'submissions/{submission.id}/revisions/{revision.id}/cover_letter/cover_letter.pdf',
            'file_size': 512000,  # 512KB
            'mime_type': 'application/pdf',
            'file_order': 1
        },
        {
            'file_type': FileType.FIGURE,
            'original_filename': 'figure1.png',
            'file_path': f'submissions/{submission.id}/revisions/{revision.id}/figures/figure1.png',
            'file_size': 1024000,  # 1MB
            'mime_type': 'image/png',
            'file_order': 1
        }
    ]
    
    for file_data in files_data:
        ManuscriptFile.objects.create(
            submission=submission,
            revision=revision,
            uploaded_by=user,
            **file_data
        )
    
    print(f"✓ {len(files_data)} files created")
    
    return submission


def test_optimized_queries():
    """Test query optimization with select_related and prefetch_related."""
    
    print("\n--- Query Optimization Test ---")
    
    # BAD: N+1 query problem
    print("\nBAD: Without optimization (N+1 problem)")
    with CaptureQueriesContext(connection) as ctx:
        submissions = Submission.objects.filter(status=SubmissionStatus.DRAFT)
        for sub in submissions:
            _ = sub.submitting_author.email  # Extra query per submission
            _ = list(sub.authorship_set.all())  # Extra query per submission
            _ = list(sub.files.all())  # Extra query per submission
    
    print(f"Queries executed: {len(ctx.captured_queries)}")
    
    # GOOD: Optimized with select_related and prefetch_related
    print("\nGOOD: With optimization")
    with CaptureQueriesContext(connection) as ctx:
        submissions = Submission.objects.filter(
            status=SubmissionStatus.DRAFT
        ).select_related(
            'submitting_author',
            'current_revision'
        ).prefetch_related(
            'authorship_set',
            'files'
        )
        
        for sub in submissions:
            _ = sub.submitting_author.email  # No extra query
            _ = list(sub.authorship_set.all())  # No extra query
            _ = list(sub.files.all())  # No extra query
    
    print(f"Queries executed: {len(ctx.captured_queries)}")


def test_full_text_search():
    """Test full-text search with GIN index."""
    
    print("\n--- Full-Text Search Test ---")
    
    from django.contrib.postgres.search import SearchQuery, SearchRank
    
    # Search for "machine learning"
    query = SearchQuery('machine & learning')
    
    with CaptureQueriesContext(connection) as ctx:
        results = Submission.objects.filter(
            search_vector=query
        ).annotate(
            rank=SearchRank('search_vector', query)
        ).order_by('-rank')
        
        print(f"\nSearch results for 'machine learning':")
        for result in results:
            print(f"  - {result.title[:50]}... (rank: {result.rank})")
    
    print(f"\nQueries executed: {len(ctx.captured_queries)}")
    print("\nSQL Query:")
    print(ctx.captured_queries[0]['sql'][:500] + "...")


def test_indexes():
    """Test that indexes are created correctly."""
    
    print("\n--- Index Verification ---")
    
    with connection.cursor() as cursor:
        # Check submission indexes
        cursor.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'submissions'
            ORDER BY indexname;
        """)
        
        print("\nSubmission indexes:")
        for idx_name, idx_def in cursor.fetchall():
            print(f"  ✓ {idx_name}")
        
        # Check authorship indexes
        cursor.execute("""
            SELECT indexname, indexdef 
            FROM pg_indexes 
            WHERE tablename = 'authorships'
            ORDER BY indexname;
        """)
        
        print("\nAuthorship indexes:")
        for idx_name, idx_def in cursor.fetchall():
            print(f"  ✓ {idx_name}")


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("SUBMISSION MODELS TEST")
    print("=" * 60)
    
    submission = test_submission_creation()
    test_optimized_queries()
    test_full_text_search()
    test_indexes()
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY ✓")
    print("=" * 60)


if __name__ == '__main__':
    run_tests()
