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
    cursor.execute("SELECT id, nombre, direccion, telefono, email FROM aseguradoras")
    aseguradoras = cursor.fetchall()
    conn.close()
    return [
        {
            'id': row[0],
            'nombre': row[1],
            'direccion': row[2],
            'telefono': row[3],
            'email': row[4]
        }
        for row in aseguradoras
    ]

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

def get_aseguradora_by_id(aseguradora_id):
    """Obtiene los detalles de una aseguradora específica"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, direccion, telefono, email FROM aseguradoras WHERE id=?", (aseguradora_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'nombre': row[1],
            'direccion': row[2],
            'telefono': row[3],
            'email': row[4]
        }
    return None

def update_aseguradora(aseguradora_id, nombre, direccion, telefono, email):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE aseguradoras SET nombre=?, direccion=?, telefono=?, email=? WHERE id=?",
                   (nombre, direccion, telefono, email, aseguradora_id))
    conn.commit()
    conn.close()

def delete_aseguradora(aseguradora_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM aseguradoras WHERE id=?", (aseguradora_id,))
    conn.commit()
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

def display_aseguradoras_cards():
    """Muestra las aseguradoras en formato de tarjetas estilo Trello"""
    
    # CSS para las tarjetas estilo Trello
    st.markdown("""
        <style>
        .card-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px 0;
        }
        .aseguradora-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            border-left: 4px solid #0079BF;
        }
        .aseguradora-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .card-header {
            font-size: 1.3em;
            font-weight: bold;
            color: #172B4D;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid #DFE1E6;
        }
        .card-field {
            margin: 8px 0;
            font-size: 0.95em;
        }
        .card-label {
            font-weight: 600;
            color: #5E6C84;
            display: inline-block;
            width: 80px;
        }
        .card-value {
            color: #172B4D;
        }
        .card-id {
            background: #0079BF;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)
    
    aseguradoras = read_aseguradoras()
    
    if not aseguradoras:
        st.info("No hay aseguradoras registradas.")
        return
    
    st.markdown(f"### 📋 Total de Aseguradoras: {len(aseguradoras)}")
    
    # Crear tarjetas en formato HTML
    cards_html = '<div class="card-container">'
    
    for aseg in aseguradoras:
        cards_html += f"""
        <div class="aseguradora-card">
            <div class="card-header">
                <span class="card-id">ID: {aseg['id']}</span>
                <div style="margin-top: 8px;">{aseg['nombre']}</div>
            </div>
            <div class="card-field">
                <span class="card-label">📍 Dirección:</span>
                <span class="card-value">{aseg['direccion']}</span>
            </div>
            <div class="card-field">
                <span class="card-label">📞 Teléfono:</span>
                <span class="card-value">{aseg['telefono']}</span>
            </div>
            <div class="card-field">
                <span class="card-label">📧 Email:</span>
                <span class="card-value">{aseg['email']}</span>
            </div>
        </div>
        """
    
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

def crud_aseguradoras():
    """Interfaz CRUD para gestionar aseguradoras con visualización de tarjetas"""
    st.header("Gestión de Aseguradoras")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Ver Aseguradoras", "➕ Crear", "✏️ Modificar", "🗑️ Eliminar"])
    
    with tab1:
        st.subheader("Lista de Aseguradoras")
        display_aseguradoras_cards()
    
    with tab2:
        st.subheader("Crear Nueva Aseguradora")
        with st.form("form_crear_aseguradora"):
            nombre = st.text_input("Nombre de la Aseguradora")
            direccion = st.text_input("Dirección")
            telefono = st.text_input("Teléfono")
            email = st.text_input("Email")
            submitted = st.form_submit_button("Crear Aseguradora")
            
            if submitted:
                if nombre and direccion and telefono and email:
                    create_aseguradora(nombre, direccion, telefono, email)
                    st.success("Aseguradora creada exitosamente!")
                    st.rerun()
                else:
                    st.error("Todos los campos son obligatorios.")
    
    with tab3:
        st.subheader("Modificar Aseguradora")
        aseguradoras = read_aseguradoras()
        
        if aseguradoras:
            aseg_options = {f"{a['id']} - {a['nombre']}": a['id'] for a in aseguradoras}
            selected = st.selectbox("Seleccionar Aseguradora", list(aseg_options.keys()))
            
            if selected:
                aseg_id = aseg_options[selected]
                aseg = get_aseguradora_by_id(aseg_id)
                
                if aseg:
                    with st.form("form_modificar_aseguradora"):
                        nombre = st.text_input("Nombre", value=aseg['nombre'])
                        direccion = st.text_input("Dirección", value=aseg['direccion'])
                        telefono = st.text_input("Teléfono", value=aseg['telefono'])
                        email = st.text_input("Email", value=aseg['email'])
                        submitted = st.form_submit_button("Guardar Cambios")
                        
                        if submitted:
                            update_aseguradora(aseg_id, nombre, direccion, telefono, email)
                            st.success("Aseguradora actualizada exitosamente!")
                            st.rerun()
        else:
            st.info("No hay aseguradoras para modificar.")
    
    with tab4:
        st.subheader("Eliminar Aseguradora")
        aseguradoras = read_aseguradoras()
        
        if aseguradoras:
            aseg_options = {f"{a['id']} - {a['nombre']}": a['id'] for a in aseguradoras}
            selected = st.selectbox("Seleccionar Aseguradora a Eliminar", list(aseg_options.keys()))
            
            if selected:
                aseg_id = aseg_options[selected]
                st.warning(f"¿Estás seguro de eliminar la aseguradora: {selected}?")
                
                if st.button("Confirmar Eliminación", type="primary"):
                    delete_aseguradora(aseg_id)
                    st.success("Aseguradora eliminada exitosamente!")
                    st.rerun()
        else:
            st.info("No hay aseguradoras para eliminar.")
    
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