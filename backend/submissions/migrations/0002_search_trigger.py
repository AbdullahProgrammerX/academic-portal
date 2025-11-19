# Generated manually for full-text search trigger

from django.contrib.postgres.search import SearchVector
from django.db import migrations


def create_search_trigger(apps, schema_editor):
    """
    Create PostgreSQL trigger to automatically update search_vector.
    Trigger updates on INSERT or UPDATE of title/abstract.
    """
    schema_editor.execute("""
        CREATE OR REPLACE FUNCTION submissions_search_vector_update() RETURNS TRIGGER AS $$
        BEGIN
            NEW.search_vector := 
                setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
                setweight(to_tsvector('english', COALESCE(NEW.abstract, '')), 'B');
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER submissions_search_vector_trigger
        BEFORE INSERT OR UPDATE OF title, abstract
        ON submissions
        FOR EACH ROW
        EXECUTE FUNCTION submissions_search_vector_update();
    """)


def drop_search_trigger(apps, schema_editor):
    """Drop search trigger and function."""
    schema_editor.execute("""
        DROP TRIGGER IF EXISTS submissions_search_vector_trigger ON submissions;
        DROP FUNCTION IF EXISTS submissions_search_vector_update();
    """)


def populate_search_vectors(apps, schema_editor):
    """Populate search_vector for existing rows."""
    Submission = apps.get_model('submissions', 'Submission')
    
    # Use raw SQL for efficiency
    schema_editor.execute("""
        UPDATE submissions
        SET search_vector = 
            setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(abstract, '')), 'B')
        WHERE search_vector IS NULL;
    """)


class Migration(migrations.Migration):

    dependencies = [
        ('submissions', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_search_trigger,
            reverse_code=drop_search_trigger
        ),
        migrations.RunPython(
            populate_search_vectors,
            reverse_code=migrations.RunPython.noop
        ),
    ]
