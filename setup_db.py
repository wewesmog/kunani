"""
Database setup script for Kunani
"""
import os
from pathlib import Path
from app.shared_services.db import get_postgres_connection
from app.shared_services.logger_setup import setup_logger

from langfuse import get_client


logger = setup_logger()


def setup_database():
    """Set up the database tables"""
    try:
        conn = get_postgres_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        # Read and execute the SQL file
        sql_file_path = Path(__file__).parent / 'db.sql'
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        try:
            cursor.execute(sql_content)
            conn.commit()
            logger.info("Successfully set up database tables")
            print("✓ Database setup completed successfully!")
        except Exception as e:
            conn.rollback()
            logger.error(f"Error executing SQL: {e}")
            print(f"✗ Error: {e}")
            raise

    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        print(f"✗ Database setup failed: {e}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    print("Setting up Kunani database...")
    setup_database()

