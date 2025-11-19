"""
Comprehensive database verification script.
Checks connection, tables, indexes, constraints, and data integrity.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from submissions.models import Submission, Authorship, Revision, ManuscriptFile

User = get_user_model()

def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_database_connection():
    """Verify PostgreSQL connection."""
    print_header("DATABASE CONNECTION")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✓ PostgreSQL Connected")
            print(f"  Version: {version.split(',')[0]}")
            
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
            print(f"  Database: {db_name}")
            
            cursor.execute("SELECT current_user;")
            db_user = cursor.fetchone()[0]
            print(f"  User: {db_user}")
            
            cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
            db_size = cursor.fetchone()[0]
            print(f"  Size: {db_size}")
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        sys.exit(1)


def check_tables():
    """List all tables in the database."""
    print_header("DATABASE TABLES")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            ORDER BY tablename;
        """)
        
        tables = cursor.fetchall()
        print(f"\nTotal tables: {len(tables)}\n")
        
        for schema, table, size in tables:
            print(f"  {schema}.{table:<40} {size:>10}")


def check_indexes():
    """List all indexes with their types."""
    print_header("DATABASE INDEXES")
    
    with connection.cursor() as cursor:
        # Submissions indexes
        cursor.execute("""
            SELECT 
                indexname,
                indexdef,
                pg_size_pretty(pg_relation_size(indexname::regclass)) as size
            FROM pg_indexes
            WHERE tablename = 'submissions'
            ORDER BY indexname;
        """)
        
        print("\nSubmissions table indexes:")
        for idx_name, idx_def, size in cursor.fetchall():
            idx_type = "GIN" if "gin" in idx_def.lower() else "B-tree"
            print(f"  [{idx_type:6}] {idx_name:<40} {size:>8}")
        
        # Authorships indexes
        cursor.execute("""
            SELECT 
                indexname,
                indexdef,
                pg_size_pretty(pg_relation_size(indexname::regclass)) as size
            FROM pg_indexes
            WHERE tablename = 'authorships'
            ORDER BY indexname;
        """)
        
        print("\nAuthorships table indexes:")
        for idx_name, idx_def, size in cursor.fetchall():
            print(f"  [B-tree] {idx_name:<40} {size:>8}")
        
        # Revisions indexes
        cursor.execute("""
            SELECT 
                indexname,
                pg_size_pretty(pg_relation_size(indexname::regclass)) as size
            FROM pg_indexes
            WHERE tablename = 'revisions'
            ORDER BY indexname;
        """)
        
        print("\nRevisions table indexes:")
        for idx_name, size in cursor.fetchall():
            print(f"  [B-tree] {idx_name:<40} {size:>8}")
        
        # Files indexes
        cursor.execute("""
            SELECT 
                indexname,
                pg_size_pretty(pg_relation_size(indexname::regclass)) as size
            FROM pg_indexes
            WHERE tablename = 'manuscript_files'
            ORDER BY indexname;
        """)
        
        print("\nManuscript Files table indexes:")
        for idx_name, size in cursor.fetchall():
            print(f"  [B-tree] {idx_name:<40} {size:>8}")


def check_constraints():
    """List all constraints (PK, FK, UNIQUE, CHECK)."""
    print_header("DATABASE CONSTRAINTS")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                conrelid::regclass AS table_name,
                conname AS constraint_name,
                CASE contype
                    WHEN 'p' THEN 'PRIMARY KEY'
                    WHEN 'f' THEN 'FOREIGN KEY'
                    WHEN 'u' THEN 'UNIQUE'
                    WHEN 'c' THEN 'CHECK'
                END AS constraint_type
            FROM pg_constraint
            WHERE conrelid::regclass::text IN (
                'submissions', 'authorships', 'revisions', 'manuscript_files', 'users_user', 'users_userprofile'
            )
            ORDER BY table_name, constraint_type, constraint_name;
        """)
        
        current_table = None
        for table, name, ctype in cursor.fetchall():
            if table != current_table:
                print(f"\n{table}:")
                current_table = table
            print(f"  [{ctype:12}] {name}")


def check_triggers():
    """List all triggers."""
    print_header("DATABASE TRIGGERS")
    
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                event_object_table AS table_name,
                trigger_name,
                event_manipulation,
                action_timing
            FROM information_schema.triggers
            WHERE event_object_schema = 'public'
            ORDER BY table_name, trigger_name;
        """)
        
        triggers = cursor.fetchall()
        if triggers:
            for table, name, event, timing in triggers:
                print(f"  {table}.{name}")
                print(f"    → {timing} {event}")
        else:
            print("  No custom triggers found")


def check_data_counts():
    """Show row counts for all main tables."""
    print_header("TABLE ROW COUNTS")
    
    counts = {
        'Users': User.objects.count(),
        'User Profiles': User.objects.filter(profile__isnull=False).count(),
        'Submissions': Submission.objects.count(),
        'Authorships': Authorship.objects.count(),
        'Revisions': Revision.objects.count(),
        'Manuscript Files': ManuscriptFile.objects.count(),
    }
    
    print()
    for table, count in counts.items():
        print(f"  {table:<25} {count:>6} rows")


def check_submission_status_distribution():
    """Show distribution of submission statuses."""
    print_header("SUBMISSION STATUS DISTRIBUTION")
    
    from django.db.models import Count
    
    status_dist = Submission.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    if status_dist:
        print()
        for item in status_dist:
            status_display = dict(Submission._meta.get_field('status').choices).get(item['status'], item['status'])
            print(f"  {str(status_display):<25} {item['count']:>6}")
    else:
        print("\n  No submissions yet")


def check_foreign_key_integrity():
    """Verify foreign key relationships."""
    print_header("FOREIGN KEY INTEGRITY")
    
    checks = [
        ("Submissions → Users", 
         Submission.objects.filter(submitting_author__isnull=True).count()),
        ("Authorships → Submissions", 
         Authorship.objects.filter(submission__isnull=True).count()),
        ("Revisions → Submissions", 
         Revision.objects.filter(submission__isnull=True).count()),
        ("Manuscript Files → Submissions", 
         ManuscriptFile.objects.filter(submission__isnull=True).count()),
        ("Manuscript Files → Revisions", 
         ManuscriptFile.objects.filter(revision__isnull=True).count()),
    ]
    
    print()
    all_ok = True
    for check_name, orphan_count in checks:
        if orphan_count == 0:
            print(f"  ✓ {check_name:<35} OK")
        else:
            print(f"  ✗ {check_name:<35} {orphan_count} orphaned records!")
            all_ok = False
    
    if all_ok:
        print("\n  All foreign key relationships are valid ✓")


def check_search_vector():
    """Test full-text search functionality."""
    print_header("FULL-TEXT SEARCH TEST")
    
    # Check if search trigger exists
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*)
            FROM information_schema.triggers
            WHERE trigger_name = 'submissions_search_vector_trigger';
        """)
        trigger_exists = cursor.fetchone()[0] > 0
    
    if trigger_exists:
        print("\n  ✓ Search trigger installed")
    else:
        print("\n  ✗ Search trigger NOT found!")
        return
    
    # Check search_vector population
    total_submissions = Submission.objects.count()
    populated = Submission.objects.filter(search_vector__isnull=False).count()
    
    print(f"  ✓ Search vectors populated: {populated}/{total_submissions}")
    
    # Test search functionality
    if populated > 0:
        from django.contrib.postgres.search import SearchQuery, SearchRank
        
        query = SearchQuery('machine | learning | bioinformatics')
        results = Submission.objects.filter(
            search_vector=query
        ).annotate(
            rank=SearchRank('search_vector', query)
        ).order_by('-rank')[:3]
        
        if results:
            print(f"\n  Search test ('machine | learning | bioinformatics'):")
            for i, result in enumerate(results, 1):
                print(f"    {i}. {result.title[:50]}... (rank: {result.rank:.4f})")
        else:
            print("\n  No search results (expected if no matching content)")


def check_performance_indexes():
    """Verify critical performance indexes exist."""
    print_header("PERFORMANCE INDEX VERIFICATION")
    
    required_indexes = [
        ('submissions', 'sub_author_status_idx', 'Submission author+status lookup'),
        ('submissions', 'sub_status_created_idx', 'Submission status+date filtering'),
        ('submissions', 'sub_search_vector_idx', 'Full-text search'),
        ('authorships', 'auth_sub_order_idx', 'Author ordering'),
        ('revisions', 'rev_sub_num_idx', 'Revision lookup'),
        ('manuscript_files', 'file_sub_rev_idx', 'File lookup by submission+revision'),
    ]
    
    with connection.cursor() as cursor:
        print()
        for table, idx_name, description in required_indexes:
            cursor.execute("""
                SELECT COUNT(*)
                FROM pg_indexes
                WHERE tablename = %s AND indexname = %s;
            """, [table, idx_name])
            
            exists = cursor.fetchone()[0] > 0
            status = "✓" if exists else "✗"
            print(f"  {status} {idx_name:<30} {description}")


def check_model_meta_options():
    """Verify model Meta configurations."""
    print_header("MODEL META OPTIONS")
    
    models = [
        (Submission, 'submissions'),
        (Authorship, 'authorships'),
        (Revision, 'revisions'),
        (ManuscriptFile, 'manuscript_files'),
    ]
    
    print()
    for model, expected_table in models:
        meta = model._meta
        print(f"{model.__name__}:")
        print(f"  db_table: {meta.db_table} {'✓' if meta.db_table == expected_table else '✗'}")
        print(f"  ordering: {meta.ordering}")
        if hasattr(meta, 'unique_together') and meta.unique_together:
            print(f"  unique_together: {meta.unique_together}")
        if hasattr(meta, 'indexes') and meta.indexes:
            print(f"  custom indexes: {len(meta.indexes)}")
        print()


def run_all_checks():
    """Execute all verification checks."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "DATABASE VERIFICATION REPORT" + " " * 25 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        check_database_connection()
        check_tables()
        check_indexes()
        check_constraints()
        check_triggers()
        check_data_counts()
        check_submission_status_distribution()
        check_foreign_key_integrity()
        check_search_vector()
        check_performance_indexes()
        check_model_meta_options()
        
        print("\n" + "=" * 70)
        print("  ✓ ALL CHECKS COMPLETED SUCCESSFULLY")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n✗ ERROR during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    run_all_checks()
