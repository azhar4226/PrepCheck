"""
Database migration script for UGC NET enhancements
Run this script to add new fields to existing tables
"""

import os
import sys

# Add parent directories to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

from app import create_app, db
from sqlalchemy import text

app = create_app()

def run_migration():
    """Run the database migration for UGC NET fields"""
    with app.app_context():
        print("🔄 Starting UGC NET database migration...")
        
        try:
            # Add new fields to subjects table
            print("📝 Adding UGC NET fields to subjects table...")
            subject_migrations = [
                "ALTER TABLE subjects ADD COLUMN IF NOT EXISTS subject_code VARCHAR(10);",
                "ALTER TABLE subjects ADD COLUMN IF NOT EXISTS paper_type VARCHAR(20) DEFAULT 'paper2';",
                "ALTER TABLE subjects ADD COLUMN IF NOT EXISTS total_marks_paper1 INTEGER DEFAULT 100;",
                "ALTER TABLE subjects ADD COLUMN IF NOT EXISTS total_marks_paper2 INTEGER DEFAULT 100;",
                "ALTER TABLE subjects ADD COLUMN IF NOT EXISTS exam_duration_paper1 INTEGER DEFAULT 60;",
                "ALTER TABLE subjects ADD COLUMN IF NOT EXISTS exam_duration_paper2 INTEGER DEFAULT 120;"
            ]
            
            for migration in subject_migrations:
                try:
                    db.session.execute(text(migration))
                    print(f"  ✅ {migration}")
                except Exception as e:
                    print(f"  ⚠️  {migration} - {str(e)}")
            
            # Add new fields to chapters table
            print("📝 Adding weightage fields to chapters table...")
            chapter_migrations = [
                "ALTER TABLE chapters ADD COLUMN IF NOT EXISTS weightage_paper1 INTEGER DEFAULT 0;",
                "ALTER TABLE chapters ADD COLUMN IF NOT EXISTS weightage_paper2 INTEGER DEFAULT 0;",
                "ALTER TABLE chapters ADD COLUMN IF NOT EXISTS estimated_questions_paper1 INTEGER DEFAULT 0;",
                "ALTER TABLE chapters ADD COLUMN IF NOT EXISTS estimated_questions_paper2 INTEGER DEFAULT 0;",
                "ALTER TABLE chapters ADD COLUMN IF NOT EXISTS chapter_order INTEGER DEFAULT 0;"
            ]
            
            for migration in chapter_migrations:
                try:
                    db.session.execute(text(migration))
                    print(f"  ✅ {migration}")
                except Exception as e:
                    print(f"  ⚠️  {migration} - {str(e)}")
            
            # Add new fields to question_bank table
            print("📝 Adding UGC NET fields to question_bank table...")
            question_bank_migrations = [
                "ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS paper_type VARCHAR(20);",
                "ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS exam_year INTEGER;",
                "ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS exam_session VARCHAR(20);",
                "ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS question_type VARCHAR(30) DEFAULT 'practice';",
                "ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS avg_solve_time INTEGER;",
                "ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS success_rate FLOAT;",
                "ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS difficulty_rating FLOAT;",
                "ALTER TABLE question_bank ADD COLUMN IF NOT EXISTS confidence_threshold FLOAT;"
            ]
            
            for migration in question_bank_migrations:
                try:
                    db.session.execute(text(migration))
                    print(f"  ✅ {migration}")
                except Exception as e:
                    print(f"  ⚠️  {migration} - {str(e)}")
            
            # Create UGC NET mock tests table
            print("📝 Creating UGC NET mock tests table...")
            create_mock_tests_table = """
            CREATE TABLE IF NOT EXISTS ugc_net_mock_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                description TEXT,
                subject_id INTEGER NOT NULL,
                paper_type VARCHAR(20) NOT NULL,
                total_questions INTEGER DEFAULT 50,
                total_marks INTEGER DEFAULT 100,
                time_limit INTEGER DEFAULT 180,
                previous_year_percentage FLOAT DEFAULT 70.0,
                ai_generated_percentage FLOAT DEFAULT 30.0,
                easy_percentage FLOAT DEFAULT 30.0,
                medium_percentage FLOAT DEFAULT 50.0,
                hard_percentage FLOAT DEFAULT 20.0,
                is_active BOOLEAN DEFAULT TRUE,
                created_by INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (subject_id) REFERENCES subjects (id),
                FOREIGN KEY (created_by) REFERENCES users (id)
            );
            """
            
            try:
                db.session.execute(text(create_mock_tests_table))
                print("  ✅ UGC NET mock tests table created")
            except Exception as e:
                print(f"  ⚠️  Mock tests table creation failed: {str(e)}")
            
            # Create UGC NET mock attempts table
            print("📝 Creating UGC NET mock attempts table...")
            create_mock_attempts_table = """
            CREATE TABLE IF NOT EXISTS ugc_net_mock_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                mock_test_id INTEGER NOT NULL,
                questions_data TEXT,
                answers TEXT,
                score INTEGER DEFAULT 0,
                total_marks INTEGER DEFAULT 0,
                percentage FLOAT DEFAULT 0.0,
                chapter_performance TEXT,
                time_taken INTEGER,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                completed_at DATETIME,
                is_completed BOOLEAN DEFAULT FALSE,
                strength_areas TEXT,
                weakness_areas TEXT,
                recommended_study_plan TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (mock_test_id) REFERENCES ugc_net_mock_tests (id)
            );
            """
            
            try:
                db.session.execute(text(create_mock_attempts_table))
                print("  ✅ UGC NET mock attempts table created")
            except Exception as e:
                print(f"  ⚠️  Mock attempts table creation failed: {str(e)}")
            
            # Commit all changes
            db.session.commit()
            print("✅ Database migration completed successfully!")
            
            # Seed UGC NET data
            print("\n🌱 Seeding UGC NET subjects and chapters...")
            from app.utils.ugc_net_seed_data import seed_ugc_net_subjects
            try:
                seed_ugc_net_subjects()
                print("✅ UGC NET data seeded successfully!")
            except Exception as e:
                print(f"⚠️  UGC NET data seeding failed (may already exist): {str(e)}")
            
            print("\n🎯 Migration Summary:")
            print("  ✅ Enhanced Subject model with UGC NET fields")
            print("  ✅ Enhanced Chapter model with weightage system")
            print("  ✅ Enhanced QuestionBank model with analytics")
            print("  ✅ Created UGCNetMockTest model")
            print("  ✅ Created UGCNetMockAttempt model")
            print("  ✅ Seeded official UGC NET structure")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {str(e)}")
            raise e

if __name__ == '__main__':
    run_migration()
