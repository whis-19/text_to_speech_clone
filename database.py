"""
Database module for Quran Reciter application.
Handles SQLite operations for storing and retrieving recordings.
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path
import hashlib


DATABASE_PATH = "quran_reciter.db"
RECORDINGS_DIR = "recordings"


def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the database with required tables."""
    os.makedirs(RECORDINGS_DIR, exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create recordings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recordings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_session_id TEXT NOT NULL,
            surah_number INTEGER NOT NULL,
            surah_name TEXT NOT NULL,
            ayah_start INTEGER NOT NULL,
            ayah_end INTEGER NOT NULL,
            voice_sample_hash TEXT NOT NULL,
            audio_file_path TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration_seconds REAL,
            file_size_bytes INTEGER
        )
    ''')
    
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_session_surah 
        ON recordings(user_session_id, surah_number)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_created_at 
        ON recordings(created_at DESC)
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")


def get_voice_hash(voice_file_path: str) -> str:
    """Generate a hash for the voice sample file."""
    with open(voice_file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()[:12]


def save_recording(
    user_session_id: str,
    surah_number: int,
    surah_name: str,
    ayah_start: int,
    ayah_end: int,
    voice_sample_hash: str,
    audio_file_path: str,
    duration_seconds: float = None,
    file_size_bytes: int = None
) -> int:
    """
    Save a recording entry to the database.
    
    Returns:
        int: The ID of the inserted recording
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO recordings (
            user_session_id, surah_number, surah_name, ayah_start, ayah_end,
            voice_sample_hash, audio_file_path, duration_seconds, file_size_bytes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_session_id, surah_number, surah_name, ayah_start, ayah_end,
        voice_sample_hash, audio_file_path, duration_seconds, file_size_bytes
    ))
    
    recording_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return recording_id


def get_recordings_by_session(user_session_id: str, limit: int = 50) -> list:
    """Get all recordings for a specific session."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM recordings 
        WHERE user_session_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    ''', (user_session_id, limit))
    
    recordings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return recordings


def get_all_recordings(limit: int = 100) -> list:
    """Get all recordings, most recent first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM recordings 
        ORDER BY created_at DESC
        LIMIT ?
    ''', (limit,))
    
    recordings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return recordings


def get_recording_by_id(recording_id: int) -> dict:
    """Get a specific recording by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM recordings WHERE id = ?', (recording_id,))
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def delete_recording(recording_id: int) -> bool:
    """Delete a recording and its audio file."""
    recording = get_recording_by_id(recording_id)
    if not recording:
        return False
    
    # Delete audio file if it exists
    audio_path = recording['audio_file_path']
    if os.path.exists(audio_path):
        os.remove(audio_path)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM recordings WHERE id = ?', (recording_id,))
    conn.commit()
    conn.close()
    
    return True


def get_recording_stats() -> dict:
    """Get statistics about recordings."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            COUNT(*) as total_recordings,
            COUNT(DISTINCT user_session_id) as unique_sessions,
            COUNT(DISTINCT surah_number) as unique_surahs,
            SUM(duration_seconds) as total_duration,
            SUM(file_size_bytes) as total_size
        FROM recordings
    ''')
    
    stats = dict(cursor.fetchone())
    conn.close()
    
    return stats


# Initialize database on module import
init_database()
