# ============================================================================
# CRUD DE ASEGURADORAS - aseguradora_crud.py
# ============================================================================
# Operaciones CRUD para aseguradoras, sucursales y relación con ramos
# Gestiona compañías de seguros y sus puntos de atención
# ============================================================================

# Importaciones necesarias
import sqlite3  # Manejo de base de datos SQLite
import streamlit as st  # Framework de interfaz de usuario
import json  # Manejo de datos JSON
import os  # Operaciones del sistema operativo
from datetime import datetime  # Manejo de fechas y tiempos
from dbconfig import DB_FILE  # Ruta del archivo de base de datos

# ============================================================================
# FUNCIÓN: ensure_sucursales_table
# Asegura que la tabla de sucursales exista en la base de datos
# ============================================================================
def ensure_sucursales_table():
    """
    Crea la tabla sucursales si no existe
    Sucursales son puntos de atención de las aseguradoras
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Crear tabla sucursales con relación a aseguradoras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sucursales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- ID único de la sucursal
            aseguradora_id INTEGER NOT NULL,  -- ID de la aseguradora (clave foránea)
            nombre TEXT NOT NULL,  -- Nombre de la sucursal
            ciudad TEXT,  -- Ciudad donde se ubica
            direccion TEXT,  -- Dirección completa
            telefono TEXT,  -- Teléfono de contacto
            email TEXT,  -- Email de contacto
            FOREIGN KEY (aseguradora_id) REFERENCES aseguradoras(id)  -- Relación con aseguradora
        )
    ''')
    
    conn.commit()  # Confirmar cambios
    conn.close()  # Cerrar conexión

# ============================================================================
# FUNCIÓN: create_sucursal
# Crea una nueva sucursal para una aseguradora
# ============================================================================
def create_sucursal(aseguradora_id, nombre, ciudad, direccion, telefono, email):
    """
    Inserta una nueva sucursal en la base de datos
    
    Parámetros:
        aseguradora_id (int): ID de la aseguradora dueña de la sucursal
        nombre (str): Nombre de la sucursal
        ciudad (str): Ciudad
        direccion (str): Dirección completa
        telefono (str): Teléfono de contacto
        email (str): Email de contacto
    """
    # Asegurar que la tabla existe
    ensure_sucursales_table()
    
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Insertar nueva sucursal
    cursor.execute('''
        INSERT INTO sucursales (aseguradora_id, nombre, ciudad, direccion, telefono, email)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (aseguradora_id, nombre, ciudad, direccion, telefono, email))
    
    conn.commit()  # Confirmar cambios
    conn.close()  # Cerrar conexión

# ============================================================================
# FUNCIÓN: get_sucursales_by_aseguradora
# Obtiene todas las sucursales de una aseguradora específica
# ============================================================================
def get_sucursales_by_aseguradora(aseguradora_id):
    """
    Consulta las sucursales de una aseguradora
    
    Parámetros:
        aseguradora_id (int): ID de la aseguradora
    
    Retorna:
        list: Lista de tuplas con los datos de las sucursales
    """
    # Asegurar que la tabla existe
    ensure_sucursales_table()
    
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Consultar sucursales de la aseguradora
    cursor.execute(
        'SELECT id, nombre, ciudad, direccion, telefono, email FROM sucursales WHERE aseguradora_id=?', 
        (aseguradora_id,)
    )
    rows = cursor.fetchall()
    
    conn.close()  # Cerrar conexión
    return rows

# ============================================================================
# FUNCIÓN: get_ramos_options
# Obtiene todos los ramos de seguros disponibles para selección
# ============================================================================
def get_ramos_options():
    """
    Obtiene todos los ramos de seguros disponibles en el sistema
    
    Retorna:
        list: Lista de tuplas (id, nombre) de ramos ordenados alfabéticamente
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Consultar todos los ramos ordenados por nombre
        cursor.execute("SELECT id, nombre FROM ramos_seguros ORDER BY nombre")
        ramos = cursor.fetchall()
        # Retornar como lista de tuplas (id, nombre)
        return [(r[0], r[1]) for r in ramos]
    
    except Exception as e:
        # Mostrar error en la interfaz
        st.error(f"Error al obtener ramos: {str(e)}")
        return []
    
    finally:
        # Cerrar conexión
        conn.close()

# ============================================================================
# FUNCIÓN: get_aseguradora_ramos
# Obtiene los ramos asociados a una aseguradora específica
# ============================================================================
def get_aseguradora_ramos(aseguradora_id):
    """
    Consulta los ramos de seguros que ofrece una aseguradora
    
    Parámetros:
        aseguradora_id (int): ID de la aseguradora
    
    Retorna:
        list: Lista de tuplas (id, nombre) de ramos asociados
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Consultar ramos mediante JOIN con tabla de relación aseguradora_ramos
        cursor.execute('''
            SELECT r.id, r.nombre 
            FROM ramos_seguros r
            INNER JOIN aseguradora_ramos ar ON r.id = ar.ramo_id
            WHERE ar.aseguradora_id = ?
            ORDER BY r.nombre
        ''', (aseguradora_id,))
        return cursor.fetchall()
    
    except Exception:
        # En caso de error, retornar lista vacía
        return []
    
    finally:
        # Cerrar conexión
        conn.close()

def create_aseguradora(data, ramo_ids):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO aseguradoras (
                tipo_contribuyente, tipo_identificacion, identificacion, razon_social,
                nombre_comercial, pais, representante_legal, aniversario, web, correo_electronico
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        aseguradora_id = cursor.lastrowid
        for ramo_id in ramo_ids:
            cursor.execute('INSERT INTO aseguradora_ramos (aseguradora_id, ramo_id) VALUES (?, ?)', (aseguradora_id, ramo_id))
        conn.commit()
        return "Aseguradora creada exitosamente."
    except sqlite3.IntegrityError:
        return "Error: La aseguradora ya existe o los datos son inválidos."
    finally:
        conn.close()

def read_aseguradoras():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM aseguradoras")
    rows = cursor.fetchall()
    conn.close()
    return rows

def read_aseguradoras_with_sucursales():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM aseguradoras")
    aseguradoras = cursor.fetchall()
    # Obtener sucursales para cada aseguradora
    cursor.execute("SELECT aseguradora_id, nombre FROM sucursales")
    sucursales_all = cursor.fetchall()
    sucursales_dict = {}
    for aseguradora_id, nombre in sucursales_all:
        sucursales_dict.setdefault(aseguradora_id, []).append(nombre)
    conn.close()
    return aseguradoras, sucursales_dict

def update_aseguradora(id, data, ramo_ids):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE aseguradoras
            SET tipo_contribuyente=?, tipo_identificacion=?, identificacion=?, razon_social=?,
                nombre_comercial=?, pais=?, representante_legal=?, aniversario=?, web=?, correo_electronico=?
            WHERE id=?
        ''', (*data, id))
        cursor.execute('DELETE FROM aseguradora_ramos WHERE aseguradora_id=?', (id,))
        for ramo_id in ramo_ids:
            cursor.execute('INSERT INTO aseguradora_ramos (aseguradora_id, ramo_id) VALUES (?, ?)', (id, ramo_id))
        conn.commit()
        return "Aseguradora actualizada exitosamente."
    except sqlite3.IntegrityError:
        return "Error: No se pudo actualizar la aseguradora."
    finally:
        conn.close()

def delete_aseguradora(id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM aseguradoras WHERE id=?", (id,))
        conn.commit()
        return "Aseguradora eliminada exitosamente."
    except sqlite3.IntegrityError:
        return "Error: No se pudo eliminar la aseguradora."
    finally:
        conn.close()

def populate_aseguradoras_from_json():
    """Populate the database with insurance companies from the JSON file"""
    json_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "aseguradoras.json")
    
    if not os.path.exists(json_file_path):
        return "Error: No se encontró el archivo aseguradoras.json"
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            aseguradoras_data = json.load(file)
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        inserted_count = 0
        skipped_count = 0
        
        for aseguradora in aseguradoras_data:
            # Skip empty entries
            if not aseguradora.get("Razón social") or not aseguradora.get("Identificación"):
                skipped_count += 1
                continue
            
            # Prepare data with proper formatting
            tipo_contribuyente = "Persona Jurídica"  # All insurance companies are legal entities
            tipo_identificacion = "RUC"  # All use RUC
            identificacion = aseguradora.get("Identificación", "").strip()
            razon_social = aseguradora.get("Razón social", "").strip()
            nombre_comercial = aseguradora.get("Nombre comercial", "").strip()
            pais = aseguradora.get("País", "ECUADOR").strip()
            representante_legal = aseguradora.get("Representante legal", "").strip()
            
            # Handle anniversary date
            aniversario_str = aseguradora.get("Aniversario", "")
            if aniversario_str and aniversario_str != "0001-01-01" and aniversario_str != "1001-01-01":
                try:
                    aniversario = datetime.strptime(aniversario_str, "%Y-%m-%d").date()
                except:
                    aniversario = None
            else:
                aniversario = None
            
            web = aseguradora.get("Web", "").strip()
            if web in ["N/A", "pagina", ""]:
                web = ""
            
            correo_electronico = aseguradora.get("Correo electrónico", "").strip()
            if correo_electronico == "a@seguros.com" or correo_electronico == "a@alianza.com":
                correo_electronico = ""
            
            # Check if aseguradora already exists
            cursor.execute("SELECT id FROM aseguradoras WHERE identificacion = ?", (identificacion,))
            if cursor.fetchone():
                skipped_count += 1
                continue
            
            # Insert the aseguradora
            try:
                cursor.execute('''
                    INSERT INTO aseguradoras (
                        tipo_contribuyente, tipo_identificacion, identificacion, razon_social,
                        nombre_comercial, pais, representante_legal, aniversario, web, correo_electronico
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (tipo_contribuyente, tipo_identificacion, identificacion, razon_social,
                      nombre_comercial, pais, representante_legal, aniversario, web, correo_electronico))
                inserted_count += 1
            except sqlite3.IntegrityError:
                skipped_count += 1
                continue
        
        conn.commit()
        conn.close()
        
        return f"Proceso completado: {inserted_count} aseguradoras insertadas, {skipped_count} omitidas (duplicadas o vacías)"
        
    except Exception as e:
        return f"Error al procesar el archivo JSON: {str(e)}"

def crud_aseguradoras():
    st.subheader("Gestión de Aseguradoras")
    action = st.selectbox("Seleccione una acción", ["Crear", "Leer", "Actualizar", "Eliminar", "Sucursales", "Cargar desde JSON"])
    
    if action == "Crear":
        st.write("### Crear Aseguradora")
        # Removed dropdown - all insurance companies are legal entities
        tipo_contribuyente = "Persona Jurídica"
        st.info("💼 Tipo de Contribuyente: Persona Jurídica (todas las aseguradoras son personas jurídicas)")
        
        # Removed dropdown - all insurance companies use RUC
        tipo_identificacion = "RUC"
        st.info("🏢 Tipo de Identificación: RUC (todas las aseguradoras usan RUC de 13 dígitos)")
        
        identificacion = st.text_input(
            "RUC (13 dígitos)", 
            max_chars=13,
            help="Ingrese el RUC de 13 dígitos de la aseguradora"
        )
        razon_social = st.text_input("Razón Social")
        nombre_comercial = st.text_input("Nombre Comercial")
        pais = st.text_input("País")
        representante_legal = st.text_input("Representante Legal")
        aniversario = st.date_input("Aniversario")
        web = st.text_input("Sitio Web")
        correo_electronico = st.text_input("Correo Electrónico")
        
        # Replace the 1-5 dropdown with actual ramos from database
        ramos_options = get_ramos_options()
        if ramos_options:
            selected_ramos = st.multiselect(
                "Seleccione los Ramos de Seguros",
                options=[r[0] for r in ramos_options],
                format_func=lambda x: next((r[1] for r in ramos_options if r[0] == x), ""),
                help="Seleccione uno o más ramos de seguros que maneja esta aseguradora"
            )
        else:
            st.warning("No hay ramos de seguros registrados. Por favor, registre ramos antes de crear aseguradoras.")
            selected_ramos = []
        
        if st.button("Crear Aseguradora"):
            if not razon_social:
                st.error("La razón social es obligatoria")
            elif not identificacion or len(identificacion) != 13:
                st.error("El RUC debe tener exactamente 13 dígitos")
            elif not identificacion.isdigit():
                st.error("El RUC debe contener solo números")
            elif not selected_ramos:
                st.error("Debe seleccionar al menos un ramo de seguros")
            else:
                data = (tipo_contribuyente, tipo_identificacion, identificacion, razon_social,
                        nombre_comercial, pais, representante_legal, aniversario, web, correo_electronico)
                message = create_aseguradora(data, selected_ramos)
                st.success(message)
    
    elif action == "Leer":
        st.write("### Listado de Aseguradoras")
        aseguradoras, sucursales_dict = read_aseguradoras_with_sucursales()
        columns = [
            "id", "tipo_contribuyente", "tipo_identificacion", "identificacion", "razon_social",
            "nombre_comercial", "pais", "representante_legal", "aniversario", "web",
            "correo_electronico", "sucursal"
        ]
        for aseguradora in aseguradoras:
            info = dict(zip(columns, aseguradora[:len(columns)]))
            # Mostrar sucursales como lista separada por coma en el campo 'sucursal'
            sucursales_nombres = sucursales_dict.get(aseguradora[0], [])
            info["sucursal"] = ", ".join(sucursales_nombres) if sucursales_nombres else ""
            st.markdown(f"**Aseguradora:** {info.get('razon_social','')}")
            st.write({k: v for k, v in info.items() if k != "razon_social"})
            if sucursales_nombres:
                st.markdown("**Sucursales:**")
                st.write(info["sucursal"])
            else:
                st.info("Sin sucursales registradas.")
    
    elif action == "Actualizar":
        st.write("### Actualizar Aseguradora")
        aseguradoras = read_aseguradoras()
        aseguradora_ids = [aseguradora[0] for aseguradora in aseguradoras]
        seleccion = st.selectbox("Seleccione la Aseguradora a Actualizar", aseguradora_ids)
        if seleccion:
            aseguradora = next((a for a in aseguradoras if a[0] == seleccion), None)
            if aseguradora:
                # Removed dropdown - all insurance companies are legal entities
                tipo_contribuyente = "Persona Jurídica"
                st.info("💼 Tipo de Contribuyente: Persona Jurídica (todas las aseguradoras son personas jurídicas)")
                
                # Removed dropdown - all insurance companies use RUC
                tipo_identificacion = "RUC"
                st.info("🏢 Tipo de Identificación: RUC (todas las aseguradoras usan RUC de 13 dígitos)")
                
                identificacion = st.text_input(
                    "RUC (13 dígitos)", 
                    value=aseguradora[3],
                    max_chars=13,
                    help="Ingrese el RUC de 13 dígitos de la aseguradora"
                )
                razon_social = st.text_input("Razón Social", aseguradora[4])
                nombre_comercial = st.text_input("Nombre Comercial", aseguradora[5])
                pais = st.text_input("País", aseguradora[6])
                representante_legal = st.text_input("Representante Legal", aseguradora[7])
                aniversario = st.date_input("Aniversario", aseguradora[8])
                web = st.text_input("Sitio Web", aseguradora[9])
                correo_electronico = st.text_input("Correo Electrónico", aseguradora[10])
                
                # Get current ramos for this aseguradora
                current_ramos = get_aseguradora_ramos(aseguradora[0])
                current_ramos_ids = [r[0] for r in current_ramos]
                
                # Ramos selection for editing
                ramos_options = get_ramos_options()
                if ramos_options:
                    selected_ramos = st.multiselect(
                        "Seleccione los Ramos de Seguros",
                        options=[r[0] for r in ramos_options],
                        default=current_ramos_ids,
                        format_func=lambda x: next((r[1] for r in ramos_options if r[0] == x), ""),
                        help="Seleccione uno o más ramos de seguros que maneja esta aseguradora"
                    )
                else:
                    st.warning("No hay ramos de seguros registrados.")
                    selected_ramos = []
                
                if st.button("Actualizar Aseguradora"):
                    if not razon_social.strip():
                        st.error("La razón social es obligatoria")
                    elif not identificacion or len(identificacion) != 13:
                        st.error("El RUC debe tener exactamente 13 dígitos")
                    elif not identificacion.isdigit():
                        st.error("El RUC debe contener solo números")
                    elif not selected_ramos:
                        st.error("Debe seleccionar al menos un ramo de seguros")
                    else:
                        data = (tipo_contribuyente, tipo_identificacion, identificacion, razon_social,
                                nombre_comercial, pais, representante_legal, aniversario, web, correo_electronico)
                        message = update_aseguradora(seleccion, data, selected_ramos)
                        st.success(message)
    
    elif action == "Eliminar":
        st.write("### Eliminar Aseguradora")
        aseguradoras = read_aseguradoras()
        aseguradora_ids = [aseguradora[0] for aseguradora in aseguradoras]
        seleccion = st.selectbox("Seleccione la Aseguradora a Eliminar", aseguradora_ids)
        if st.button("Eliminar Aseguradora"):
            message = delete_aseguradora(seleccion)
            st.success(message)
    
    elif action == "Sucursales":
        st.write("### Gestión de Sucursales de Aseguradora")
        aseguradoras = read_aseguradoras()
        aseguradora_ids = [(a[0], a[4]) for a in aseguradoras]  # (id, razon_social)
        if not aseguradora_ids:
            st.info("No hay aseguradoras registradas.")
            return
        aseguradora_sel = st.selectbox("Seleccione la Aseguradora", aseguradora_ids, format_func=lambda x: x[1])
        if aseguradora_sel:
            aseguradora_id = aseguradora_sel[0]
            st.write("#### Sucursales existentes:")
            sucursales = get_sucursales_by_aseguradora(aseguradora_id)
            for s in sucursales:
                st.write(f"ID: {s[0]}, Nombre: {s[1]}, Ciudad: {s[2]}, Dirección: {s[3]}, Teléfono: {s[4]}, Email: {s[5]}")
            st.write("#### Crear nueva sucursal")
            with st.form("form_crear_sucursal"):
                nombre = st.text_input("Nombre de la sucursal")
                ciudad = st.text_input("Ciudad")
                direccion = st.text_input("Dirección")
                telefono = st.text_input("Teléfono")
                email = st.text_input("Email")
                submitted = st.form_submit_button("Crear Sucursal")
                if submitted and nombre:
                    create_sucursal(aseguradora_id, nombre, ciudad, direccion, telefono, email)
                    st.success("Sucursal creada exitosamente.")
                    st.rerun()
    
    elif action == "Cargar desde JSON":
        st.write("### Cargar Aseguradoras desde JSON")
        st.info("Esta opción cargará las aseguradoras desde el archivo assets/aseguradoras.json")
        
        if st.button("Cargar Aseguradoras"):
            with st.spinner("Cargando aseguradoras..."):
                message = populate_aseguradoras_from_json()
                if "Error" in message:
                    st.error(message)
                else:
                    st.success(message)
                    st.info("💡 Nota: Las aseguradoras se han cargado sin ramos asignados. Puede editarlas posteriormente para asignar ramos de seguros.")