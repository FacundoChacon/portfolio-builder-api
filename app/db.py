"""Acceso a SQLite con stdlib (sin ORM).

La ruta de la DB se lee del env DATABASE_PATH en cada conexión para que los
tests puedan aislarla con un archivo temporal (monkeypatch) sin recargar el
módulo. Todas las queries usan placeholders (?) — nunca concatenación.
"""

import os
import sqlite3

DEFAULT_DATABASE_PATH = "./leads.db"

_CREATE_LEADS_TABLE = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    project_type_id TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    service_ids TEXT NOT NULL,
    payment_method_id TEXT NOT NULL,
    discount_code TEXT,
    subtotal REAL NOT NULL,
    discount_amount REAL NOT NULL,
    total REAL NOT NULL
)
"""


def get_database_path() -> str:
    return os.environ.get("DATABASE_PATH", DEFAULT_DATABASE_PATH)


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(get_database_path())
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(_CREATE_LEADS_TABLE)
