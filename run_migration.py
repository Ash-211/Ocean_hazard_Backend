# run_migration.py
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

def run_migration():
    # Get database connection details
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:Idkthepass@localhost:5432/incois_db")
    
    try:
        # Parse the connection string
        if DATABASE_URL.startswith("postgresql://"):
            parts = DATABASE_URL.split("://")[1].split("@")
            user_pass = parts[0].split(":")
            host_port_db = parts[1].split("/")
            host_port = host_port_db[0].split(":")
            
            dbname = host_port_db[1]
            user = user_pass[0]
            password = user_pass[1] if len(user_pass) > 1 else ""
            host = host_port[0]
            port = host_port[1] if len(host_port) > 1 else "5432"
        else:
            # Use default values if parsing fails
            dbname = "incois_db"
            user = "postgres"
            password = "Idkthepass"
            host = "localhost"
            port = "5432"
        
        # Connect to the database
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("Connected to database successfully")
        
        # Check if user_id column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'hazard_reports' AND column_name = 'user_id'
        """)
        
        if cursor.fetchone() is None:
            print("Adding user_id column to hazard_reports table...")
            cursor.execute("""
                ALTER TABLE hazard_reports 
                ADD COLUMN user_id UUID REFERENCES users(id)
            """)
            print("Added user_id column")
        else:
            print("user_id column already exists")
        
        # Check if media table exists
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'media'
        """)
        
        if cursor.fetchone() is None:
            print("Creating media table...")
            cursor.execute("""
                CREATE TABLE media (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL REFERENCES users(id),
                    hazard_report_id UUID REFERENCES hazard_reports(id),
                    filename VARCHAR NOT NULL,
                    file_path VARCHAR NOT NULL,
                    file_type VARCHAR NOT NULL,
                    file_size INTEGER NOT NULL,
                    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX idx_media_user_id ON media(user_id)")
            cursor.execute("CREATE INDEX idx_media_hazard_report_id ON media(hazard_report_id)")
            cursor.execute("CREATE INDEX idx_hazard_reports_user_id ON hazard_reports(user_id)")
            
            print("Created media table and indexes")
        else:
            print("media table already exists")
        
        cursor.close()
        conn.close()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        print("Make sure PostgreSQL is running and the database exists")

if __name__ == "__main__":
    run_migration()
