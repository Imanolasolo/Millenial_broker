# Configuración inicial del proyecto
DB_FILE = "database.db"
SECRET_KEY = "supersecreto"

import sqlite3

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Crear tabla de clientes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL
        )
    """)
    conn.commit()

    # Crear tabla de roles
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()

    # Insertar roles predeterminados si no existen
    cursor.execute("SELECT COUNT(*) FROM roles")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO roles (name) VALUES (?)", [("admin",), ("user",)])
        conn.commit()

    conn.close()