import sqlite3
import os
from dbconfig import DB_FILE

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # Tabla de clientes
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
        # Tabla de roles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        # Tabla de logs de roles
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS role_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_name TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Tabla de usuarios
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
                company_id INTEGER
            )
        ''')
        # Tabla de empresas/agrupadores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT
            )
        ''')
        # Tabla de aseguradoras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aseguradoras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_contribuyente TEXT,
                tipo_identificacion TEXT,
                identificacion TEXT,
                razon_social TEXT,
                nombre_comercial TEXT,
                pais TEXT,
                representante_legal TEXT,
                aniversario TEXT,
                web TEXT,
                correo_electronico TEXT
            )
        ''')
        # Tabla de ramos de seguros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ramos_seguros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                descripcion TEXT
            )
        ''')
        # Tabla de relación aseguradora-ramos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aseguradora_ramos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aseguradora_id INTEGER,
                ramo_id INTEGER,
                FOREIGN KEY (aseguradora_id) REFERENCES aseguradoras(id),
                FOREIGN KEY (ramo_id) REFERENCES ramos_seguros(id)
            )
        ''')
        # Tabla de pólizas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS polizas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_poliza TEXT UNIQUE NOT NULL,
                cliente_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                aseguradora_id INTEGER,
                ramo_id INTEGER,
                tipo_poliza TEXT NOT NULL,
                cobertura TEXT,
                prima TEXT,
                fecha_inicio TEXT NOT NULL,
                fecha_fin TEXT NOT NULL,
                estado TEXT NOT NULL,
                fecha_emision TEXT,
                suma_asegurada TEXT,
                deducible TEXT,
                sucursal TEXT,
                tipo_facturacion TEXT,
                linea_negocio TEXT,
                numero_factura TEXT,
                numero_anexo TEXT,
                tipo_anexo TEXT,
                ejecutivo_comercial_id INTEGER
            )
        ''')
        conn.commit()
    finally:
        conn.close()

def reset_database():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    initialize_database()

def initialize_clients_table():
    # Deprecated: use initialize_database instead
    pass

def initialize_users_table():
    # Deprecated: use initialize_database instead
    pass
