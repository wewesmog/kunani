import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from datetime import datetime
import logging

load_dotenv()

logger = logging.getLogger(__name__)


def get_postgres_connection():
    """Establish and return a connection to the PostgreSQL database"""
    db_host = os.getenv("PGHOST", "localhost")
    db_password = os.getenv("PGPASSWORD", "kunani_password")
    db_port = os.getenv("PGPORT", "5432")
    db_name = os.getenv("PGDATABASE", "kunani")
    db_user = os.getenv("PGUSER", "kunani_user")
    db_ssl_mode = os.getenv("DB_SSL_MODE", "disable")

    if not all([db_host, db_password, db_user]):
        error_msg = "Missing required database credentials in environment variables"
        logger.error(error_msg)
        raise ValueError(error_msg)

    try:
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port,
            sslmode=db_ssl_mode
        )
        logger.info(f"Successfully connected to database: {db_name}")
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Unable to connect to database. Error: {e}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while connecting to database: {e}")
        raise


def save_issue(issue: Dict[str, Any]) -> Dict[str, Any]:
    """Save an issue to the database"""
    conn = None
    cursor = None
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        insert_query = """
            INSERT INTO issues (
                issue_id, title, description, status, priority, 
                category, tags, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """
        
        cursor.execute(
            insert_query,
            (
                issue["issue_id"],
                issue["title"],
                issue["description"],
                issue.get("status", "open"),
                issue.get("priority", "medium"),
                issue.get("category"),
                issue.get("tags", []),
                Json(issue.get("metadata", {}))
            )
        )
        
        result = cursor.fetchone()
        conn.commit()
        logger.info(f"Issue saved: {issue['issue_id']}")
        return dict(result)
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error saving issue: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_issue(issue_id: str) -> Optional[Dict[str, Any]]:
    """Get an issue by issue_id"""
    conn = None
    cursor = None
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT * FROM issues WHERE issue_id = %s", (issue_id,))
        result = cursor.fetchone()
        
        if result:
            return dict(result)
        return None
    except Exception as e:
        logger.error(f"Error getting issue: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_all_issues(limit: int = 100, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get all issues with optional filtering"""
    conn = None
    cursor = None
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if status:
            cursor.execute(
                "SELECT * FROM issues WHERE status = %s ORDER BY created_at DESC LIMIT %s",
                (status, limit)
            )
        else:
            cursor.execute(
                "SELECT * FROM issues ORDER BY created_at DESC LIMIT %s",
                (limit,)
            )
        
        results = cursor.fetchall()
        return [dict(row) for row in results]
    except Exception as e:
        logger.error(f"Error getting issues: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def update_issue_status(issue_id: str, status: str) -> Optional[Dict[str, Any]]:
    """Update issue status"""
    conn = None
    cursor = None
    try:
        conn = get_postgres_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        resolved_at = None
        if status in ["resolved", "closed"]:
            resolved_at = datetime.now()
        
        cursor.execute(
            """
            UPDATE issues 
            SET status = %s, resolved_at = %s 
            WHERE issue_id = %s
            RETURNING *
            """,
            (status, resolved_at, issue_id)
        )
        
        result = cursor.fetchone()
        conn.commit()
        
        if result:
            logger.info(f"Issue {issue_id} updated to status: {status}")
            return dict(result)
        return None
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Error updating issue: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

