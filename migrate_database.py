"""
Database migration script
Adds priority_score column to existing crisis_case table
"""

import sqlite3
from datetime import datetime


def calculate_priority(severity, people_affected, urgency, available_resources):
    """Calculate priority score"""
    return (severity * 3) + (people_affected * 2) + (urgency * 4) - (available_resources * 2)


def migrate_database(db_path='impactbridge.db'):
    """
    Migrate existing database to new schema
    
    Args:
        db_path: Path to SQLite database file
    """
    print(f'Starting database migration for {db_path}...')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if priority_score column exists
        cursor.execute("PRAGMA table_info(crisis_case)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'priority_score' in columns:
            print('✓ priority_score column already exists')
        else:
            print('Adding priority_score column...')
            cursor.execute('ALTER TABLE crisis_case ADD COLUMN priority_score INTEGER')
            print('✓ priority_score column added')
        
        # Calculate and update priority scores for existing records
        print('Calculating priority scores for existing records...')
        cursor.execute('''
            SELECT id, severity, people_affected, urgency, available_resources
            FROM crisis_case
            WHERE priority_score IS NULL
        ''')
        
        records = cursor.fetchall()
        updated_count = 0
        
        for record in records:
            case_id, severity, people_affected, urgency, available_resources = record
            priority = calculate_priority(severity, people_affected, urgency, available_resources)
            
            cursor.execute('''
                UPDATE crisis_case
                SET priority_score = ?
                WHERE id = ?
            ''', (priority, case_id))
            
            updated_count += 1
        
        print(f'✓ Updated {updated_count} records with priority scores')
        
        # Create indexes if they don't exist
        print('Creating indexes...')
        
        try:
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_priority_created
                ON crisis_case(priority_score, created_at)
            ''')
            print('✓ Created idx_priority_created')
        except Exception as e:
            print(f'  Index idx_priority_created: {e}')
        
        try:
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_severity_urgency
                ON crisis_case(severity, urgency)
            ''')
            print('✓ Created idx_severity_urgency')
        except Exception as e:
            print(f'  Index idx_severity_urgency: {e}')
        
        try:
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_registered_at
                ON volunteer(registered_at)
            ''')
            print('✓ Created idx_registered_at')
        except Exception as e:
            print(f'  Index idx_registered_at: {e}')
        
        try:
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_availability
                ON volunteer(availability)
            ''')
            print('✓ Created idx_availability')
        except Exception as e:
            print(f'  Index idx_availability: {e}')
        
        # Commit changes
        conn.commit()
        print('\n✓ Migration completed successfully!')
        
        # Show statistics
        cursor.execute('SELECT COUNT(*) FROM crisis_case')
        case_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM volunteer')
        volunteer_count = cursor.fetchone()[0]
        
        print(f'\nDatabase statistics:')
        print(f'  Crisis cases: {case_count}')
        print(f'  Volunteers: {volunteer_count}')
        
    except Exception as e:
        print(f'\n✗ Migration failed: {e}')
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    import os
    
    # Check if database exists
    if os.path.exists('impactbridge.db'):
        migrate_database()
    else:
        print('No existing database found. Migration not needed.')
        print('The new schema will be created automatically when you run the application.')
