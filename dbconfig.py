# Configuración inicial del proyecto
DB_FILE = "database.db"
SECRET_KEY = "supersecreto"

import sqlite3
import os

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Log the initialization process
    print("Initializing database...")

    # Create aseguradoras table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aseguradoras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_contribuyente TEXT,
            tipo_identificacion TEXT,
            identificacion TEXT UNIQUE,
            razon_social TEXT,
            nombre_comercial TEXT,
            pais TEXT,
            representante_legal TEXT,
            aniversario TEXT,
            web TEXT,
            correo_electronico TEXT
        )
    ''')
    print("Aseguradoras table ensured.")

    # Create clients table if it doesn't exist
    cursor.execute('''
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
    ''')
    print("Clients table ensured.")

    # Create roles table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    print("Roles table ensured.")

    # Insert default roles if they don't exist
    cursor.execute("SELECT COUNT(*) FROM roles")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO roles (name) VALUES (?)", [("admin",), ("user",)])
        print("Default roles inserted.")

    # Create users table if it doesn't exist
    cursor.execute('''
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
            ultima_actualizacion TEXT,
            company_id INTEGER REFERENCES companies(id)
        )
    ''')
    print("Users table ensured.")

    # Create polizas table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS polizas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_poliza TEXT UNIQUE NOT NULL,
            cliente_id INTEGER NOT NULL,
            usuario_id INTEGER NOT NULL,
            tipo_poliza TEXT NOT NULL,
            cobertura TEXT NOT NULL,
            prima TEXT NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            estado TEXT NOT NULL,
            FOREIGN KEY (cliente_id) REFERENCES clients (id),
            FOREIGN KEY (usuario_id) REFERENCES users (id)
        )
    ''')
    print("Polizas table ensured.")

    # Create companies table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            address TEXT,
            phone TEXT,
            email TEXT
        )
    ''')
    print("Companies table ensured.")

    conn.commit()
    conn.close()
    print("Database initialization complete.")