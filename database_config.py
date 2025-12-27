import sqlite3
import os
from dbconfig import DB_FILE

def initialize_database():
    """
    Inicializa la base de datos creando todas las tablas necesarias si no existen
    """
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
        # Tabla de siniestros
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS siniestros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_siniestro TEXT UNIQUE NOT NULL,
                poliza_id INTEGER NOT NULL,
                cliente_id INTEGER,
                tipo_siniestro TEXT NOT NULL,  -- 'Vehicular' o 'Vida/Salud'
                fecha_siniestro DATE NOT NULL,
                fecha_registro DATE DEFAULT CURRENT_DATE,
                estado TEXT DEFAULT 'En Proceso',  -- 'En Proceso', 'En Reparación', 'Cerrado', 'Rechazado', 'En Revisión', 'Aprobado', 'Pagado'
                
                -- Campos específicos para siniestros vehiculares
                placa_vehiculo TEXT,
                lugar_siniestro TEXT,
                tipo_dano TEXT,  -- 'Choque', 'Robo', 'Incendio', 'Vandalismo', 'Otro'
                taller_id INTEGER,
                
                -- Campos específicos para siniestros de vida/salud
                tipo_cobertura TEXT,  -- 'Hospitalización', 'Cirugía', 'Emergencia', 'Consulta', 'Fallecimiento'
                centro_medico TEXT,
                diagnostico TEXT,
                
                -- Campos comunes
                descripcion TEXT,
                monto_estimado REAL,
                monto_reclamado REAL,
                monto_aprobado REAL,
                observaciones TEXT,
                documentos_adjuntos TEXT,  -- JSON con rutas de archivos
                
                -- Usuario que registró el siniestro
                usuario_registro_id INTEGER,
                
                -- Timestamps
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (poliza_id) REFERENCES polizas(id) ON DELETE CASCADE,
                FOREIGN KEY (cliente_id) REFERENCES clients(id),
                FOREIGN KEY (usuario_registro_id) REFERENCES users(id)
            )
        ''')
        # Tabla de talleres
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS talleres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                ruc TEXT,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                ciudad TEXT,
                especialidad TEXT,
                estado TEXT DEFAULT 'Activo',  -- 'Activo', 'Inactivo'
                observaciones TEXT,
                fecha_registro DATE DEFAULT CURRENT_DATE
            )
        ''')
        # Tabla de clinicas_hospitales
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clinicas_hospitales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                ruc TEXT,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                ciudad TEXT,
                tipo TEXT,  -- 'Clínica', 'Hospital', 'Centro Médico'
                especialidades TEXT,  -- JSON con lista de especialidades
                estado TEXT DEFAULT 'Activo',  -- 'Activo', 'Inactivo'
                observaciones TEXT,
                fecha_registro DATE DEFAULT CURRENT_DATE
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
