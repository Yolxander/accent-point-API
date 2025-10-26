#!/usr/bin/env python3
"""
Database schema migration script for OpenVoice API
Applies the Supabase schema to the local or remote database
"""

import os
import sys
import psycopg2
from pathlib import Path
from typing import Optional

def get_database_url() -> str:
    """Get database URL from environment variables"""
    # Try different environment variable names
    db_url = os.getenv('DATABASE_URL')
    if db_url:
        return db_url
    
    # Fallback to local Supabase defaults
    host = os.getenv('SUPABASE_DB_HOST', '127.0.0.1')
    port = os.getenv('SUPABASE_DB_PORT', '54322')
    user = os.getenv('SUPABASE_DB_USER', 'postgres')
    password = os.getenv('SUPABASE_DB_PASSWORD', 'postgres')
    database = os.getenv('SUPABASE_DB_NAME', 'postgres')
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"

def read_schema_file() -> str:
    """Read the SQL schema file"""
    schema_file = Path(__file__).parent / "supabase_schema_updated.sql"
    
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")
    
    return schema_file.read_text()

def apply_schema(db_url: str, schema_sql: str) -> bool:
    """Apply the schema to the database"""
    try:
        print(f"Connecting to database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("Applying schema...")
        cursor.execute(schema_sql)
        
        print("Schema applied successfully!")
        
        # Verify tables were created
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('voice_conversions', 'text_to_speech_conversions', 'batch_processing_jobs', 'api_usage_stats')
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        print(f"Created tables: {[table[0] for table in tables]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main migration function"""
    print("OpenVoice API Database Schema Migration")
    print("=" * 50)
    
    try:
        # Get database URL
        db_url = get_database_url()
        print(f"Database URL: {db_url.split('@')[1] if '@' in db_url else 'local'}")
        
        # Read schema file
        print("Reading schema file...")
        schema_sql = read_schema_file()
        
        # Apply schema
        success = apply_schema(db_url, schema_sql)
        
        if success:
            print("\n✅ Migration completed successfully!")
            print("The database is now ready for the OpenVoice API.")
        else:
            print("\n❌ Migration failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
