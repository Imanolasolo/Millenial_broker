# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS - dbconfig.py
# ============================================================================
# Define constantes globales y funciones para inicializar la base de datos SQLite
# Este archivo es el núcleo de la configuración de almacenamiento de datos
# ============================================================================

# ============================================================================
# CONSTANTES DE CONFIGURACIÓN GLOBAL
# ============================================================================
DB_FILE = "database.db"  # Nombre del archivo de base de datos SQLite
SECRET_KEY = "supersecreto"  # Clave secreta para firmar tokens JWT (CAMBIAR EN PRODUCCIÓN)

# Importaciones necesarias
import sqlite3  # Librería para manejar SQLite
import os  # Para operaciones del sistema de archivos

# ============================================================================
# FUNCIÓN: initialize_database
# Crea todas las tablas necesarias para la aplicación
# ============================================================================
def initialize_database():
    """
    Inicializa la base de datos creando todas las tablas necesarias
    Si las tablas ya existen, no hace nada (CREATE TABLE IF NOT EXISTS)
    También realiza migraciones agregando columnas faltantes a tablas existentes
    """
    # Conectar a la base de datos (se crea el archivo si no existe)
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Registrar el inicio del proceso de inicialización
    print("Initializing database...")

    # ============================================================================
    # TABLA: aseguradoras
    # Almacena información de las compañías aseguradoras
    # ============================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aseguradoras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único autoincrementable
            tipo_contribuyente TEXT,  -- Tipo de contribuyente fiscal
            tipo_identificacion TEXT,  -- Tipo de documento (RUC, Cédula, etc.)
            identificacion TEXT UNIQUE,  -- Número de identificación (único)
            razon_social TEXT,  -- Nombre legal de la empresa
            nombre_comercial TEXT,  -- Nombre comercial
            pais TEXT,  -- País de origen
            representante_legal TEXT,  -- Nombre del representante legal
            aniversario TEXT,  -- Fecha de aniversario
            web TEXT,  -- Sitio web
            correo_electronico TEXT  -- Email de contacto
        )
    ''')
    print("Aseguradoras table ensured.")

    # ============================================================================
    # TABLA: clients
    # Almacena información completa de los clientes (personas y empresas)
    # ============================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único del cliente
            tipo_cliente TEXT,  -- Persona Natural o Jurídica
            nombres VARCHAR(50),  -- Nombres del cliente
            apellidos VARCHAR(50),  -- Apellidos del cliente
            razon_social TEXT,  -- Razón social (para empresas)
            tipo_documento TEXT,  -- Tipo de documento de identidad
            numero_documento TEXT,  -- Número de documento
            fecha_nacimiento TEXT,  -- Fecha de nacimiento
            nacionalidad TEXT,  -- Nacionalidad
            sexo TEXT,  -- Sexo (M/F/Otro)
            estado_civil TEXT,  -- Estado civil
            correo_electronico TEXT CHECK (correo_electronico LIKE '%@%' AND correo_electronico LIKE '%.%'),  -- Email con validación
            correo_empresa TEXT,  -- Email corporativo
            telefono_movil TEXT,  -- Teléfono móvil
            telefono_fijo TEXT,  -- Teléfono fijo
            direccion_domicilio TEXT,  -- Dirección completa
            provincia TEXT,  -- Provincia
            ciudad TEXT,  -- Ciudad
            codigo_postal TEXT,  -- Código postal
            ocupacion_profesion TEXT,  -- Ocupación o profesión
            empresa_trabajo TEXT,  -- Empresa donde trabaja
            tipo_empresa TEXT,  -- Tipo de empresa
            ingresos_mensuales TEXT,  -- Rango de ingresos mensuales
            nivel_educacion TEXT,  -- Nivel educativo
            fumador TEXT,  -- Si es fumador (Sí/No)
            actividades_riesgo TEXT,  -- Actividades de riesgo que realiza
            historial_medico TEXT,  -- Historial médico relevante
            historial_siniestros TEXT,  -- Historial de siniestros previos
            vehiculos_registrados TEXT,  -- Vehículos registrados
            propiedades TEXT,  -- Propiedades que posee
            tipo_contribuyente TEXT,  -- Tipo de contribuyente
            numero_ruc TEXT,  -- Número RUC
            representante_legal_id INTEGER,  -- ID del representante legal
            observaciones_legales TEXT,  -- Observaciones legales
            canal_preferido_contacto TEXT,  -- Canal preferido de contacto
            notas_adicionales TEXT,  -- Notas adicionales
            fecha_registro TEXT,  -- Fecha de registro en el sistema
            ultima_actualizacion TEXT  -- Última fecha de actualización
            -- columnas adicionales se agregan abajo si no existen
        )
    ''')
    # ============================================================================
    # MIGRACIÓN: Agregar columnas adicionales si no existen
    # Esto permite actualizar la estructura sin perder datos existentes
    # ============================================================================
    cursor.execute("PRAGMA table_info(clients)")  # Obtener información de columnas existentes
    columns = [row[1] for row in cursor.fetchall()]  # Lista de nombres de columnas
    
    # Agregar columnas una por una si no existen (evita errores en bases antiguas)
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
    
    conn.commit()  # Guardar cambios en la base de datos
    print("Clients table ensured.")

    # ============================================================================
    # TABLA: roles
    # Define los roles disponibles en el sistema
    # ============================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único del rol
            name TEXT UNIQUE NOT NULL  -- Nombre del rol (único)
        )
    ''')
    print("Roles table ensured.")

    # ============================================================================
    # INSERCIÓN DE ROLES POR DEFECTO
    # Si la tabla está vacía, inserta roles admin y user
    # ============================================================================
    cursor.execute("SELECT COUNT(*) FROM roles")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO roles (name) VALUES (?)", [("admin",), ("user",)])
        print("Default roles inserted.")

    # ============================================================================
    # TABLA: users
    # Almacena información de los usuarios del sistema
    # ============================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único del usuario
            username TEXT UNIQUE,  -- Nombre de usuario (único)
            password TEXT,  -- Contraseña encriptada con bcrypt
            role TEXT,  -- Rol del usuario
            correo TEXT,  -- Email del usuario
            nombres TEXT,  -- Nombres del usuario
            apellidos TEXT,  -- Apellidos del usuario
            telefono TEXT,  -- Teléfono de contacto
            fecha_registro TEXT,  -- Fecha de registro
            ultima_actualizacion TEXT,  -- Última actualización
            company_id INTEGER REFERENCES companies(id)  -- Relación con empresa
        )
    ''')
    print("Users table ensured.")

    # ============================================================================
    # TABLA: polizas
    # Almacena las pólizas de seguro
    # ============================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS polizas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único de la póliza
            numero_poliza TEXT UNIQUE NOT NULL,  -- Número de póliza (único)
            cliente_id INTEGER NOT NULL,  -- ID del cliente (clave foránea)
            usuario_id INTEGER NOT NULL,  -- ID del usuario que creó la póliza
            tipo_poliza TEXT NOT NULL,  -- Tipo de póliza
            cobertura TEXT NOT NULL,  -- Descripción de cobertura
            prima TEXT NOT NULL,  -- Monto de la prima
            fecha_inicio TEXT NOT NULL,  -- Fecha de inicio de vigencia
            fecha_fin TEXT NOT NULL,  -- Fecha de fin de vigencia
            direccion TEXT,  -- Dirección de la propiedad/bien asegurado
            contenido TEXT,  -- Descripción del contenido asegurado
            estado TEXT NOT NULL,  -- Estado actual (Activa, Cancelada, etc.)
            beneficiario TEXT,  -- Beneficiario de la póliza
            FOREIGN KEY (cliente_id) REFERENCES clients (id),  -- Relación con clientes
            FOREIGN KEY (usuario_id) REFERENCES users (id)  -- Relación con usuarios
        )
    ''')
    print("Polizas table ensured.")

    # Añadir columna observaciones si no existe
    cursor.execute("PRAGMA table_info(polizas)")
    polizas_columns = [row[1] for row in cursor.fetchall()]
    if "observaciones" not in polizas_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN observaciones TEXT")
        print("Added 'observaciones' column to polizas.")
    # Añadir columna beneficiario si no existe (para migraciones)
    if "beneficiario" not in polizas_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN beneficiario TEXT")
        print("Added 'beneficiario' column to polizas.")
    # Añadir columna direccion si no existe (localización donde se maneja la póliza)
    if "direccion" not in polizas_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN direccion TEXT")
        print("Added 'direccion' column to polizas.")
    # Añadir columna contenido si no existe (contenido asegurado)
    if "contenido" not in polizas_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN contenido TEXT")
        print("Added 'contenido' column to polizas.")

    # ============================================================================
    # TABLA: poliza_ramos
    # Relación entre pólizas y ramos de seguro (muchos a muchos)
    # ============================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS poliza_ramos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único
            poliza_id INTEGER NOT NULL,  -- ID de la póliza
            nro_ramo INTEGER NOT NULL,  -- Número de ramo
            ramo_id INTEGER NOT NULL,  -- ID del ramo de seguro
            suma_asegurada TEXT,  -- Suma asegurada para este ramo
            prima TEXT,  -- Prima específica del ramo
            observaciones TEXT,  -- Observaciones específicas
            FOREIGN KEY (poliza_id) REFERENCES polizas (id),
            FOREIGN KEY (ramo_id) REFERENCES ramos_seguros (id)
        )
    ''')
    print("Poliza_Ramos table ensured.")

    # ============================================================================
    # TABLA: companies
    # Almacena información de las empresas/agencias
    # ============================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único
            name TEXT UNIQUE NOT NULL,  -- Nombre de la empresa (único)
            address TEXT,  -- Dirección
            phone TEXT,  -- Teléfono
            email TEXT  -- Email
        )
    ''')
    print("Companies table ensured.")

    # ============================================================================
    # TABLA: aseguradora_ramos
    # Relación entre aseguradoras y ramos que ofrecen
    # ============================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aseguradora_ramos (
            aseguradora_id INTEGER NOT NULL,  -- ID de la aseguradora
            ramo_id INTEGER NOT NULL,  -- ID del ramo
            PRIMARY KEY (aseguradora_id, ramo_id),  -- Clave primaria compuesta
            FOREIGN KEY (aseguradora_id) REFERENCES aseguradoras (id),
            FOREIGN KEY (ramo_id) REFERENCES ramos_seguros (id)
        )
    ''')
    print("Aseguradora-Ramos table ensured.")

    # ============================================================================
    # TABLA: movimientos_poliza
    # Registra todos los movimientos/cambios en las pólizas
    # ============================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos_poliza (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único del movimiento
            codigo_movimiento TEXT UNIQUE,  -- Código único del movimiento
            poliza_id INTEGER,  -- ID de la póliza afectada
            cliente_id INTEGER,  -- ID del cliente
            fecha_movimiento TEXT,  -- Fecha del movimiento
            tipo_movimiento TEXT,  -- Tipo (Aumento, Disminución, Cancelación, etc.)
            estado TEXT DEFAULT 'Proceso',  -- Estado del movimiento
            suma_asegurada_nueva REAL,  -- Nueva suma asegurada (si aplica)
            prima_nueva REAL,  -- Nueva prima (si aplica)
            direccion_nueva TEXT,  -- Nueva dirección (si aplica)
            pdf_documento TEXT,  -- Ruta del documento PDF generado
            observaciones TEXT,  -- Observaciones adicionales
            usuario_id INTEGER,  -- Usuario que realizó el movimiento
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,  -- Fecha de registro
            FOREIGN KEY(poliza_id) REFERENCES polizas(id),
            FOREIGN KEY(cliente_id) REFERENCES clients(id),
            FOREIGN KEY(usuario_id) REFERENCES users(id)
        )
    ''')
    print("Movimientos_Poliza table ensured.")

    # ============================================================================
    # TABLA: facturas
    # Almacena las facturas generadas
    # ============================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único de la factura
            numero_factura TEXT UNIQUE,  -- Número de factura (único)
            poliza_id INTEGER,  -- ID de la póliza relacionada
            movimiento_id INTEGER,  -- ID del movimiento relacionado
            cliente_id INTEGER,  -- ID del cliente
            fecha_emision TEXT,  -- Fecha de emisión
            monto_neto REAL,  -- Monto neto
            impuestos REAL,  -- Impuestos
            iva REAL,  -- IVA
            total REAL,  -- Total a pagar
            estado TEXT DEFAULT 'Emitida',  -- Estado de la factura
            pdf_documento TEXT,  -- Ruta del PDF de la factura
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,  -- Fecha de registro
            FOREIGN KEY(poliza_id) REFERENCES polizas(id),
            FOREIGN KEY(movimiento_id) REFERENCES movimientos_poliza(id),
            FOREIGN KEY(cliente_id) REFERENCES clients(id)
        )
    ''')
    print("Facturas table ensured.")

    # ============================================================================
    # TABLA: notas_de_credito
    # Almacena las notas de crédito emitidas
    # ============================================================================
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notas_de_credito (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único
            numero_nota TEXT UNIQUE,  -- Número de nota de crédito (único)
            factura_id INTEGER,  -- ID de la factura relacionada
            poliza_id INTEGER,  -- ID de la póliza
            movimiento_id INTEGER,  -- ID del movimiento
            cliente_id INTEGER,  -- ID del cliente
            fecha_emision TEXT,  -- Fecha de emisión
            monto_neto REAL,  -- Monto neto
            impuestos REAL,  -- Impuestos
            iva REAL,  -- IVA
            total REAL,  -- Total
            motivo TEXT,  -- Motivo de la nota de crédito
            estado TEXT DEFAULT 'Emitida',  -- Estado
            pdf_documento TEXT,  -- Ruta del PDF
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,  -- Fecha de registro
            FOREIGN KEY(factura_id) REFERENCES facturas(id),
            FOREIGN KEY(poliza_id) REFERENCES polizas(id),
            FOREIGN KEY(movimiento_id) REFERENCES movimientos_poliza(id),
            FOREIGN KEY(cliente_id) REFERENCES clients(id)
        )
    ''')
    print("Notas_de_Credito table ensured.")

    # ============================================================================
    # FINALIZACIÓN: Guardar cambios y cerrar conexión
    # ============================================================================
    conn.commit()  # Confirmar todos los cambios en la base de datos
    conn.close()  # Cerrar la conexión
    print("Database initialization complete.")