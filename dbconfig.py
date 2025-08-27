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
            nombres VARCHAR(50),
            apellidos VARCHAR(50),
            razon_social TEXT,
            tipo_documento TEXT,
            numero_documento TEXT,
            fecha_nacimiento TEXT,
            nacionalidad TEXT,
            sexo TEXT,
            estado_civil TEXT,
            correo_electronico TEXT CHECK (correo_electronico LIKE '%@%' AND correo_electronico LIKE '%.%'),
            correo_empresa TEXT,
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
            -- columnas adicionales se agregan abajo si no existen
        )
    ''')
    # Añadir columnas si no existen (para migraciones en bases ya creadas)
    cursor.execute("PRAGMA table_info(clients)")
    columns = [row[1] for row in cursor.fetchall()]
    if "correo_empresa" not in columns:
        cursor.execute("ALTER TABLE clients ADD COLUMN correo_empresa TEXT")
    if "sector_mercado" not in columns:
        cursor.execute("ALTER TABLE clients ADD COLUMN sector_mercado TEXT")
    if "tipo_empresa_categoria" not in columns:
        cursor.execute("ALTER TABLE clients ADD COLUMN tipo_empresa_categoria TEXT")
    if "tipo_persona_juridica" not in columns:
        cursor.execute("ALTER TABLE clients ADD COLUMN tipo_persona_juridica TEXT")
    if "subactividad_economica" not in columns:
        cursor.execute("ALTER TABLE clients ADD COLUMN subactividad_economica TEXT")
    if "pagina_web" not in columns:
        cursor.execute("ALTER TABLE clients ADD COLUMN pagina_web TEXT")
    if "fecha_aniversario" not in columns:
        cursor.execute("ALTER TABLE clients ADD COLUMN fecha_aniversario TEXT")
    if "contacto_autorizado_id" not in columns:
        cursor.execute("ALTER TABLE clients ADD COLUMN contacto_autorizado_id TEXT")
    conn.commit()
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

    # Añadir columna observaciones si no existe
    cursor.execute("PRAGMA table_info(polizas)")
    polizas_columns = [row[1] for row in cursor.fetchall()]
    if "observaciones" not in polizas_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN observaciones TEXT")
        print("Added 'observaciones' column to polizas.")

    # Crear tabla poliza_ramos si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS poliza_ramos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            poliza_id INTEGER NOT NULL,
            nro_ramo INTEGER NOT NULL,
            ramo_id INTEGER NOT NULL,
            suma_asegurada TEXT,
            prima TEXT,
            observaciones TEXT,
            FOREIGN KEY (poliza_id) REFERENCES polizas (id),
            FOREIGN KEY (ramo_id) REFERENCES ramos_seguros (id)
        )
    ''')
    print("Poliza_Ramos table ensured.")

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

    # Create aseguradora_ramos table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aseguradora_ramos (
            aseguradora_id INTEGER NOT NULL,
            ramo_id INTEGER NOT NULL,
            PRIMARY KEY (aseguradora_id, ramo_id),
            FOREIGN KEY (aseguradora_id) REFERENCES aseguradoras (id),
            FOREIGN KEY (ramo_id) REFERENCES ramos_seguros (id)
        )
    ''')
    print("Aseguradora-Ramos table ensured.")

    # Crear tabla movimientos_poliza si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos_poliza (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_movimiento TEXT UNIQUE,
            poliza_id INTEGER,
            cliente_id INTEGER,
            fecha_movimiento TEXT,
            tipo_movimiento TEXT,
            estado TEXT DEFAULT 'Proceso',
            suma_asegurada_nueva REAL,
            prima_nueva REAL,
            direccion_nueva TEXT,
            pdf_documento TEXT,
            observaciones TEXT,
            usuario_id INTEGER,
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(poliza_id) REFERENCES polizas(id),
            FOREIGN KEY(cliente_id) REFERENCES clients(id),
            FOREIGN KEY(usuario_id) REFERENCES users(id)
        )
    ''')
    print("Movimientos_Poliza table ensured.")

    conn.commit()
    conn.close()
    print("Database initialization complete.")