import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = Path(__file__).parent.parent / "data" / "rustic-manager.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paths (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL UNIQUE,
            disk_table_name TEXT NOT NULL,
            backup_table_name TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()


def register_path(path: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM paths WHERE path = ?", (path,))
    row = cursor.fetchone()
    
    if row:
        path_id = row["id"]
    else:
        cursor.execute(
            "SELECT COALESCE(MAX(id), 0) + 1 FROM paths"
        )
        path_id = cursor.fetchone()[0]
        
        disk_table_name = f"disk_usage_{path_id}"
        backup_table_name = f"backup_history_{path_id}"
        
        cursor.execute(
            "INSERT INTO paths (path, disk_table_name, backup_table_name) VALUES (?, ?, ?)",
            (path, disk_table_name, backup_table_name)
        )
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {disk_table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                used_bytes INTEGER NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {backup_table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_id TEXT,
                duration_seconds REAL,
                space_change_bytes INTEGER,
                timestamp TEXT NOT NULL
            )
        """)
        
        conn.commit()
    
    conn.close()
    return path_id


def record_disk_usage(path_id: int, used_bytes: int):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT disk_table_name FROM paths WHERE id = ?", (path_id,)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return
    
    table_name = row["disk_table_name"]
    timestamp = datetime.now().isoformat()
    
    cursor.execute(
        f"INSERT INTO {table_name} (used_bytes, timestamp) VALUES (?, ?)",
        (used_bytes, timestamp)
    )
    
    conn.commit()
    conn.close()


def record_backup(path_id: int, snapshot_id: Optional[str], duration_seconds: float, space_change_bytes: int):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT backup_table_name FROM paths WHERE id = ?", (path_id,)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return
    
    table_name = row["backup_table_name"]
    timestamp = datetime.now().isoformat()
    
    cursor.execute(
        f"INSERT INTO {table_name} (snapshot_id, duration_seconds, space_change_bytes, timestamp) VALUES (?, ?, ?, ?)",
        (snapshot_id, duration_seconds, space_change_bytes, timestamp)
    )
    
    conn.commit()
    conn.close()


def get_latest_disk_usage(path_id: int) -> Optional[int]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT disk_table_name FROM paths WHERE id = ?", (path_id,)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    table_name = row["disk_table_name"]
    
    cursor.execute(
        f"SELECT used_bytes FROM {table_name} ORDER BY timestamp DESC LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()
    
    return row["used_bytes"] if row else None


def get_disk_usage_history(path_id: int, limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT disk_table_name FROM paths WHERE id = ?", (path_id,)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return []
    
    table_name = row["disk_table_name"]
    
    cursor.execute(
        f"SELECT used_bytes, timestamp FROM {table_name} ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_backup_history(path_id: int, limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT backup_table_name FROM paths WHERE id = ?", (path_id,)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return []
    
    table_name = row["backup_table_name"]
    
    cursor.execute(
        f"SELECT snapshot_id, duration_seconds, space_change_bytes, timestamp FROM {backup_table_name} ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]
