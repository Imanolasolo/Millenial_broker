# Configuración inicial del proyecto
DB_FILE = "database.db"
SECRET_KEY = "supersecreto"

import sqlite3
import os

def initialize_database():
    if not os.path.exists(DB_FILE):  # Check if the database file already exists
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Crear tabla de clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_cliente TEXT,
                nombres TEXT,
                apellidos TEXT,
                razon_social TEXT,
                tipo_documento TEXT,
                numero_documento TEXT,
                fecha_nacimiento TEXT,
                nacionalidad TEXT,
                sexo TEXT,
                estado_civil TEXT,
                correo_electronico TEXT,
                telefono_movil TEXT,
                telefono_fijo TEXT,
                direccion_domicilio TEXT,
                provincia TEXT,
                ciudad TEXT,
                codigo_postal TEXT,
                ocupacion_profesion TEXT,
                empresa_trabajo TEXT,
                tipo_empresa TEXT,
                ingresos_mensuales TEXT,
                nivel_educacion TEXT,
                fumador TEXT,
                actividades_riesgo TEXT,
                historial_medico TEXT,
                historial_siniestros TEXT,
                vehiculos_registrados TEXT,
                propiedades TEXT,
                tipo_contribuyente TEXT,
                numero_ruc TEXT,
                representante_legal_id INTEGER,
                observaciones_legales TEXT,
                canal_preferido_contacto TEXT,
                notas_adicionales TEXT,
                fecha_registro TEXT,
                ultima_actualizacion TEXT
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

        # Crear tabla de usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                correo TEXT,
                nombres TEXT,
                apellidos TEXT,
                telefono TEXT,
                fecha_registro TEXT,
                ultima_actualizacion TEXT
            )
        """)
        conn.commit()

        conn.close()