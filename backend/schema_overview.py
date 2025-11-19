"""
Database schema visualization and relationship checker.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps

def print_schema_overview():
    """Print a visual overview of all models and their relationships."""
    
    print("\n" + "╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "DATABASE SCHEMA OVERVIEW" + " " * 34 + "║")
    print("╚" + "═" * 78 + "╝\n")
    
    # Users app
    print("┌─ users (Authentication)")
    print("│")
    print("│  ┌─ User (UUID pk)")
    print("│  │   Fields: email*, full_name, affiliation, bio, orcid_id, role, verified")
    print("│  │   Indexes: email (unique), orcid_id (unique)")
    print("│  │")
    print("│  └─ UserProfile (OneToOne → User)")
    print("│      Fields: phone, country, research_interests (JSONB), profile_completed")
    print("│      Indexes: user_id (unique)")
    print("│")
    
    # Submissions app
    print("├─ submissions (Manuscript Management)")
    print("│")
    print("│  ┌─ Submission (UUID pk)")
    print("│  │   Fields: title, abstract, status (ENUM), submitting_author → User")
    print("│  │   Timestamps: created_at, submitted_at, updated_at")
    print("│  │   Indexes: GIN(search_vector), B-tree(status, author, dates)")
    print("│  │   Special: search_vector (auto-updated via trigger)")
    print("│  │")
    print("│  │   ┌─ current_revision → Revision (optional)")
    print("│  │   │")
    print("│  │   ├─ Authorship (Many-to-One)")
    print("│  │   │   Fields: full_name, email, affiliation, orcid_id")
    print("│  │   │   Fields: is_corresponding, author_order")
    print("│  │   │   Optional: user → User (for registered authors)")
    print("│  │   │   Unique: (submission, author_order)")
    print("│  │   │   Check: author_order >= 1")
    print("│  │   │")
    print("│  │   ├─ Revision (Many-to-One)")
    print("│  │   │   Fields: revision_number, response_to_reviewers")
    print("│  │   │   FKs: submission → Submission, created_by → User")
    print("│  │   │   Unique: (submission, revision_number)")
    print("│  │   │   Check: revision_number >= 1")
    print("│  │   │")
    print("│  │   └─ ManuscriptFile (Many-to-One)")
    print("│  │       Fields: file_path (S3 key), original_filename, file_type")
    print("│  │       Fields: file_size, mime_type, file_order")
    print("│  │       FKs: submission → Submission, revision → Revision")
    print("│  │       FKs: uploaded_by → User")
    print("│  │       Check: file_size > 0, file_order >= 1")
    print("│  │")
    print("│  └─ Status Flow:")
    print("│      DRAFT → SUBMITTED → UNDER_REVIEW → REVISION_NEEDED →")
    print("│      REVISION_SUBMITTED → [ACCEPTED | REJECTED]")
    print("│")
    
    print("└─ Relationships Summary")
    print()
    print("   User (1) ──< (N) Submission [submitting_author]")
    print("   User (1) ──< (N) Authorship [optional: registered author]")
    print("   User (1) ──< (N) Revision [creator]")
    print("   User (1) ──< (N) ManuscriptFile [uploader]")
    print()
    print("   Submission (1) ──< (N) Authorship")
    print("   Submission (1) ──< (N) Revision")
    print("   Submission (1) ──< (N) ManuscriptFile")
    print("   Submission (1) ──> (1) Revision [current_revision, optional]")
    print()
    print("   Revision (1) ──< (N) ManuscriptFile")
    print()
    
    print("\n" + "=" * 80)
    print("OPTIMIZATION FEATURES")
    print("=" * 80)
    print()
    print("✓ GIN Index on search_vector (Full-text search on title + abstract)")
    print("✓ Composite B-tree indexes for common query patterns")
    print("✓ PostgreSQL trigger for automatic search_vector updates")
    print("✓ SELECT_RELATED optimization for FK joins")
    print("✓ PREFETCH_RELATED optimization for reverse relations")
    print("✓ CHECK constraints for data validation")
    print("✓ UNIQUE constraints for business rules")
    print()
    
    print("=" * 80)
    print("STORAGE STRATEGY")
    print("=" * 80)
    print()
    print("Files: S3 storage with database metadata only")
    print("  Format: submissions/{uuid}/revisions/{uuid}/{type}/{filename}")
    print("  Database stores: path, size, mime_type, order")
    print("  S3 stores: actual file binary data")
    print()
    
    print("Search: PostgreSQL full-text search")
    print("  Vector: Weighted (title=A, abstract=B)")
    print("  Language: English")
    print("  Update: Automatic via trigger")
    print()


if __name__ == '__main__':
    print_schema_overview()
