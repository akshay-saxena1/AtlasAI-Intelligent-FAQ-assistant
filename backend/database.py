"""
Database module for SQLite connection management and schema initialization.

Implements a 3NF normalized schema for FAQs, chat history, user feedback,
saved bookmarks, and system analytics. Uses WAL journal mode and
foreign key enforcement for data integrity.

Author: CodeAlpha Intern | Registration ID: Akshay Saxena
"""

import sqlite3
from pathlib import Path
from typing import Any, Optional
from contextlib import contextmanager

from backend.config import get_settings


SCHEMA_SQL: str = """
-- ============================================================
-- Categories table (1NF entity)
-- ============================================================
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    icon TEXT DEFAULT '📁',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- FAQs table (normalized with FK to categories)
-- ============================================================
CREATE TABLE IF NOT EXISTS faqs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    embedding BLOB,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- ============================================================
-- Chat history table
-- ============================================================
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    user_query TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    confidence_score REAL DEFAULT 0.0,
    matched_faq_id INTEGER,
    semantic_score REAL DEFAULT 0.0,
    lexical_score REAL DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (matched_faq_id) REFERENCES faqs(id) ON DELETE SET NULL
);

-- ============================================================
-- User feedback table (boolean helpfulness)
-- ============================================================
CREATE TABLE IF NOT EXISTS user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    is_helpful BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chat_history(id) ON DELETE CASCADE
);

-- ============================================================
-- Saved bookmarks table
-- ============================================================
CREATE TABLE IF NOT EXISTS saved_bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    faq_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (faq_id) REFERENCES faqs(id) ON DELETE CASCADE,
    UNIQUE(session_id, faq_id)
);

-- ============================================================
-- System analytics table
-- ============================================================
CREATE TABLE IF NOT EXISTS system_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    event_data TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Performance indexes
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_faqs_category ON faqs(category_id);
CREATE INDEX IF NOT EXISTS idx_faqs_question ON faqs(question);
CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_history(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_created ON chat_history(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_faq ON chat_history(matched_faq_id);
CREATE INDEX IF NOT EXISTS idx_feedback_chat ON user_feedback(chat_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_session ON saved_bookmarks(session_id);
CREATE INDEX IF NOT EXISTS idx_bookmarks_faq ON saved_bookmarks(faq_id);
CREATE INDEX IF NOT EXISTS idx_analytics_type ON system_analytics(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_created ON system_analytics(created_at);
"""


def get_db_path() -> str:
    """Get the absolute path to the SQLite database file.

    Resolves the database filename relative to the backend package directory.

    Returns:
        str: Absolute path to the database file.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    settings = get_settings()
    return str(Path(__file__).parent / settings.database_url)


@contextmanager
def get_connection():
    """Context manager for SQLite database connections.

    Yields a connection with row_factory set to sqlite3.Row for
    dictionary-like row access. Enables WAL journal mode for
    concurrent read performance and enforces foreign keys.

    Auto-commits on successful exit, rolls back on exception.

    Yields:
        sqlite3.Connection: Active database connection.

    Time Complexity: O(1) for connection open/close
    Space Complexity: O(1)
    """
    conn: sqlite3.Connection = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database() -> None:
    """Initialize the database schema by executing DDL statements.

    Creates all tables and indexes if they don't already exist.
    This operation is idempotent and safe to call multiple times.

    Time Complexity: O(T) where T is the number of tables/indexes
    Space Complexity: O(S) where S is the schema SQL string size
    """
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)
    print("[DB] Schema initialized successfully.")


def execute_query(
    query: str,
    params: tuple = (),
    fetch_one: bool = False,
) -> Any:
    """Execute a parameterized SQL query and return results.

    For SELECT queries, returns a list of row dicts (or a single dict
    if fetch_one=True). For INSERT/UPDATE/DELETE, returns lastrowid.

    Args:
        query: SQL query string with ? placeholders.
        params: Tuple of parameter values for the query.
        fetch_one: If True, return only the first row.

    Returns:
        A single row dict, list of row dicts, lastrowid int, or None.

    Time Complexity: O(R) where R is the result set size
    Space Complexity: O(R)
    """
    with get_connection() as conn:
        cursor: sqlite3.Cursor = conn.execute(query, params)
        if query.strip().upper().startswith("SELECT"):
            if fetch_one:
                row = cursor.fetchone()
                return dict(row) if row else None
            return [dict(row) for row in cursor.fetchall()]
        return cursor.lastrowid


def execute_many(query: str, params_list: list[tuple]) -> None:
    """Execute a parameterized query with multiple parameter sets.

    Uses executemany for efficient batch operations on INSERT/UPDATE.

    Args:
        query: SQL query string with ? placeholders.
        params_list: List of parameter tuples for batch execution.

    Time Complexity: O(N) where N is len(params_list)
    Space Complexity: O(1) (streaming execution)
    """
    with get_connection() as conn:
        conn.executemany(query, params_list)
