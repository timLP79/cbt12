"""
Database Migration Script: Add Assessment State Tracking

This script adds two columns to the assessment_attempts table:
- question_order (JSON): Stores the list of question IDs in order
- current_question_index (INTEGER): Tracks the user's progress through the assessment

This migration supports Issue #32: Session-Based Assessment State is Fragile

Usage:
    python migrate_add_assessment_state.py

For production (AWS RDS):
    Run these SQL commands manually via AWS RDS console or psql:

    ALTER TABLE assessment_attempts
    ADD COLUMN question_order JSON,
    ADD COLUMN current_question_index INTEGER DEFAULT 0 NOT NULL;

Note: SQLite uses TEXT for JSON columns, PostgreSQL uses JSON type.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect

# Get database URL from environment or use local SQLite
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('DATABASE_URI') or \
               'sqlite:///instance/cbt_assessment.db'

print("=" * 80)
print("Database Migration: Add Assessment State Tracking (Issue #32)")
print("=" * 80)
print(f"\nDatabase: {DATABASE_URL.split('@')[0] if '@' in DATABASE_URL else DATABASE_URL}")
print("\nThis migration adds two columns to assessment_attempts table:")
print("  - question_order (JSON)")
print("  - current_question_index (INTEGER, default 0)")
print("\n" + "=" * 80)

def main():
    """Run the migration"""
    try:
        # Create engine
        engine = create_engine(DATABASE_URL)

        # Check if columns already exist
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('assessment_attempts')]

        if 'question_order' in columns and 'current_question_index' in columns:
            print("\n✅ Migration already applied!")
            print("   Columns 'question_order' and 'current_question_index' already exist.")
            return 0

        # Detect database type
        db_type = 'postgresql' if 'postgresql' in DATABASE_URL else 'sqlite'

        print(f"\n📊 Database type detected: {db_type}")
        print("\n🔨 Applying migration...")

        with engine.connect() as conn:
            # Use appropriate JSON type for each database
            if db_type == 'postgresql':
                # PostgreSQL supports JSON type
                conn.execute(text("""
                    ALTER TABLE assessment_attempts
                    ADD COLUMN question_order JSON
                """))
                conn.execute(text("""
                    ALTER TABLE assessment_attempts
                    ADD COLUMN current_question_index INTEGER DEFAULT 0 NOT NULL
                """))
            else:
                # SQLite uses TEXT for JSON
                conn.execute(text("""
                    ALTER TABLE assessment_attempts
                    ADD COLUMN question_order TEXT
                """))
                conn.execute(text("""
                    ALTER TABLE assessment_attempts
                    ADD COLUMN current_question_index INTEGER DEFAULT 0 NOT NULL
                """))

            conn.commit()

        print("\n✅ Migration completed successfully!")
        print("\nColumns added:")
        print("   - question_order: Stores list of question IDs in order")
        print("   - current_question_index: Tracks progress (default: 0)")
        print("\n💡 Benefits:")
        print("   - Assessment state now persists across session expiration")
        print("   - Users can resume assessments after logout/timeout")
        print("   - Question order preserved for randomized assessments")
        return 0

    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        print("\nIf you're using PostgreSQL in production, you may need to run:")
        print("   ALTER TABLE assessment_attempts ADD COLUMN question_order JSON;")
        print("   ALTER TABLE assessment_attempts ADD COLUMN current_question_index INTEGER DEFAULT 0 NOT NULL;")
        return 1

if __name__ == '__main__':
    sys.exit(main())
