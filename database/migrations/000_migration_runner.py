#!/usr/bin/env python3

import os
import psycopg

def create_migrations_table(conn):
    """Create migrations table if it doesn't exist"""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) NOT NULL UNIQUE,
                applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def get_applied_migrations(conn):
    """Get list of already applied migrations"""
    with conn.cursor() as cur:
        cur.execute("SELECT migration_name FROM migrations")
        return {row[0] for row in cur.fetchall()}

def apply_migration(conn, migration_file):
    """Apply a single migration file"""
    print(f"Applying migration: {migration_file}")
    
    with open(os.path.join(migration_dir, migration_file), 'r', encoding='utf-8') as f:
        sql = f.read()
    
    with conn.cursor() as cur:
        try:
            # Execute migration
            cur.execute(sql)
            
            # Record migration
            cur.execute(
                "INSERT INTO migrations (migration_name) VALUES (%s)",
                (migration_file,)
            )
            conn.commit()
            print(f"✅ Successfully applied: {migration_file}")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error applying {migration_file}: {str(e)}")
            raise

def main():
    """Main migration runner"""
    try:
        # Database connection details - UPDATE THESE WITH YOUR ACTUAL VALUES
        db_config = {
            'host': 'vibe-charting-db.c9qmo8w2y0a1.us-east-2.rds.amazonaws.com',  # Replace with your RDS endpoint
            'port': 5432,
            'database': 'vibe_charting',
            'user': 'vibecharting',
            'password': 'your-actual-password'  # Replace with your actual password
        }
        
        # Connect to database
        print("Connecting to database...")
        print(f"Host: {db_config['host']}")
        print(f"Database: {db_config['database']}")
        print(f"User: {db_config['user']}")
        
        conn = psycopg.connect(**db_config)
        conn.autocommit = True
        
        print("Database connection successful!")
        
        # Ensure migrations table exists
        create_migrations_table(conn)
        
        # Get applied migrations
        applied = get_applied_migrations(conn)
        
        # Get all migration files
        migration_dir = os.path.dirname(os.path.abspath(__file__))
        migration_files = [
            f for f in os.listdir(migration_dir)
            if f.endswith('.sql') and not f.startswith('.')
        ]
        
        # Sort migrations by number prefix
        migration_files.sort()
        
        print(f"Found {len(migration_files)} migration files")
        
        # Apply new migrations
        for migration_file in migration_files:
            if migration_file not in applied:
                apply_migration(conn, migration_file)
            else:
                print(f"⏭️  Skipping {migration_file} (already applied)")
        
        print("\n✨ All migrations completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    main() 