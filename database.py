"""
Módulo de base de datos para ORION.
Maneja la persistencia de contexto, historial y preferencias usando SQLite.
"""
import sqlite3
from datetime import datetime

DB_NAME = "orion.db"

def get_connection():
    """Establece conexión con la base de datos."""
    return sqlite3.connect(DB_NAME)

def init_db():
    """Inicializa las tablas de la base de datos si no existen."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de Contexto (Key-Value store para el estado actual)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS context (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabla de Historial de Comandos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT,
            result TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabla de Preferencias de Usuario
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS preferences (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# --- Operaciones de Contexto ---

def save_context(context_data: dict):
    """Guarda el diccionario de contexto en la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()

    for key, value in context_data.items():
        if value is not None:
            cursor.execute('''
                INSERT OR REPLACE INTO context (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, str(value), datetime.now()))

    conn.commit()
    conn.close()

def load_context() -> dict:
    """Carga el contexto guardado."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT key, value FROM context')
    rows = cursor.fetchall()

    context = {}
    for key, value in rows:
        context[key] = value

    conn.close()
    return context

# --- Operaciones de Historial ---

def add_history(command: str, result: str):
    """Registra un comando ejecutado en el historial."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO history (command, result, timestamp)
        VALUES (?, ?, ?)
    ''', (command, str(result), datetime.now()))

    conn.commit()
    conn.close()

def get_last_command():
    """Obtiene el último comando ejecutado."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT command, timestamp FROM history
        ORDER BY id DESC LIMIT 1
    ''')
    row = cursor.fetchone()
    conn.close()

    if row:
        return {"command": row[0], "timestamp": row[1]}
    return None

# --- Operaciones de Preferencias ---

def set_preference(key: str, value: str):
    """Guarda una preferencia de usuario."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO preferences (key, value, updated_at)
        VALUES (?, ?, ?)
    ''', (key, value, datetime.now()))

    conn.commit()
    conn.close()

def get_preference(key: str):
    """Obtiene una preferencia por su clave."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT value FROM preferences WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None
