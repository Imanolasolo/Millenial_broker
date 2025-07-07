import sqlite3
import streamlit as st
from dbconfig import DB_FILE

# --- NUEVO: Tabla sucursales ---
def ensure_sucursales_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sucursales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aseguradora_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            ciudad TEXT,
            direccion TEXT,
            telefono TEXT,
            email TEXT,
            FOREIGN KEY (aseguradora_id) REFERENCES aseguradoras(id)
        )
    ''')
    conn.commit()
    conn.close()

def create_sucursal(aseguradora_id, nombre, ciudad, direccion, telefono, email):
    ensure_sucursales_table()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sucursales (aseguradora_id, nombre, ciudad, direccion, telefono, email)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (aseguradora_id, nombre, ciudad, direccion, telefono, email))
    conn.commit()
    conn.close()

def get_sucursales_by_aseguradora(aseguradora_id):
    ensure_sucursales_table()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, ciudad, direccion, telefono, email FROM sucursales WHERE aseguradora_id=?', (aseguradora_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def create_aseguradora(data, ramo_ids):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # Eliminar columna sucursal si existe (no usar más en aseguradoras)
        cursor.execute("PRAGMA table_info(aseguradoras)")
        cols = [row[1] for row in cursor.fetchall()]
        # No agregar ni usar columna sucursal aquí
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
        # No usar columna sucursal aquí
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

def crud_aseguradoras():
    st.subheader("Gestión de Aseguradoras")
    action = st.selectbox("Seleccione una acción", ["Crear", "Leer", "Actualizar", "Eliminar", "Sucursales"])
    
    if action == "Crear":
        st.write("### Crear Aseguradora")
        tipo_contribuyente = st.selectbox("Tipo de Contribuyente", ["Persona Natural", "Persona Jurídica"])
        tipo_identificacion = st.selectbox("Tipo de Identificación", ["Cédula", "RUC", "Pasaporte"])
        identificacion = st.text_input("Identificación")
        razon_social = st.text_input("Razón Social")
        nombre_comercial = st.text_input("Nombre Comercial")
        pais = st.text_input("País")
        representante_legal = st.text_input("Representante Legal")
        aniversario = st.date_input("Aniversario")
        web = st.text_input("Sitio Web")
        correo_electronico = st.text_input("Correo Electrónico")
        # Eliminar campo sucursal aquí
        ramo_ids = st.multiselect("Seleccione los Ramos", [1, 2, 3, 4, 5])  # Ejemplo de IDs de ramos
        if st.button("Crear Aseguradora"):
            data = (tipo_contribuyente, tipo_identificacion, identificacion, razon_social,
                    nombre_comercial, pais, representante_legal, aniversario, web, correo_electronico)
            message = create_aseguradora(data, ramo_ids)
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
                tipo_contribuyente = st.selectbox("Tipo de Contribuyente", ["Persona Natural", "Persona Jurídica"], index=["Persona Natural", "Persona Jurídica"].index(aseguradora[1]))
                tipo_identificacion = st.selectbox("Tipo de Identificación", ["Cédula", "RUC", "Pasaporte"], index=["Cédula", "RUC", "Pasaporte"].index(aseguradora[2]))
                identificacion = st.text_input("Identificación", aseguradora[3])
                razon_social = st.text_input("Razón Social", aseguradora[4])
                nombre_comercial = st.text_input("Nombre Comercial", aseguradora[5])
                pais = st.text_input("País", aseguradora[6])
                representante_legal = st.text_input("Representante Legal", aseguradora[7])
                aniversario = st.date_input("Aniversario", aseguradora[8])
                web = st.text_input("Sitio Web", aseguradora[9])
                correo_electronico = st.text_input("Correo Electrónico", aseguradora[10])
                # Eliminar campo sucursal aquí
                ramo_ids = st.multiselect("Seleccione los Ramos", [1, 2, 3, 4, 5], default=aseguradora[11:] if len(aseguradora) > 11 else [])
                if st.button("Actualizar Aseguradora"):
                    data = (tipo_contribuyente, tipo_identificacion, identificacion, razon_social,
                            nombre_comercial, pais, representante_legal, aniversario, web, correo_electronico)
                    message = update_aseguradora(seleccion, data, ramo_ids)
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
                    # Refrescar la página para mostrar la nueva sucursal
                    st.experimental_rerun()