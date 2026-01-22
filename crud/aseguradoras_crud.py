import sqlite3
import streamlit as st
from dbconfig import DB_FILE

def create_aseguradora(nombre, direccion, telefono, email):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO aseguradoras (razon_social, nombre_comercial, correo_electronico) 
        VALUES (?, ?, ?)
    """, (nombre, nombre, email))
    conn.commit()
    conn.close()

def read_aseguradoras():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, 
               COALESCE(razon_social, nombre_comercial) as nombre,
               COALESCE(web, '') as direccion,
               COALESCE(representante_legal, '') as telefono,
               COALESCE(correo_electronico, '') as email 
        FROM aseguradoras
    """)
    aseguradoras = cursor.fetchall()
    conn.close()
    return [
        {
            'id': row[0],
            'nombre': row[1] or 'Sin nombre',
            'direccion': row[2] or 'Sin dirección',
            'telefono': row[3] or 'Sin teléfono',
            'email': row[4] or 'Sin email'
        }
        for row in aseguradoras
    ]

def get_aseguradora_by_id(aseguradora_id):
    """Obtiene los detalles de una aseguradora específica"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, 
               COALESCE(razon_social, nombre_comercial) as nombre,
               COALESCE(web, '') as direccion,
               COALESCE(representante_legal, '') as telefono,
               COALESCE(correo_electronico, '') as email 
        FROM aseguradoras 
        WHERE id=?
    """, (aseguradora_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            'id': row[0],
            'nombre': row[1] or 'Sin nombre',
            'direccion': row[2] or 'Sin dirección',
            'telefono': row[3] or 'Sin teléfono',
            'email': row[4] or 'Sin email'
        }
    return None

def update_aseguradora(aseguradora_id, nombre, direccion, telefono, email):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE aseguradoras 
        SET razon_social=?, 
            nombre_comercial=?, 
            correo_electronico=? 
        WHERE id=?
    """, (nombre, nombre, email, aseguradora_id))
    conn.commit()
    conn.close()

def delete_aseguradora(aseguradora_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM aseguradoras WHERE id=?", (aseguradora_id,))
    conn.commit()
    conn.close()

def display_aseguradoras_cards():
    """Muestra las aseguradoras en formato de tarjetas estilo Trello usando componentes de Streamlit"""
    
    aseguradoras = read_aseguradoras()
    
    if not aseguradoras:
        st.info("No hay aseguradoras registradas.")
        return
    
    st.markdown(f"### 📋 Total de Aseguradoras: {len(aseguradoras)}")
    
    # Crear grid de 3 columnas
    cols_per_row = 3
    for i in range(0, len(aseguradoras), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(aseguradoras):
                aseg = aseguradoras[idx]
                
                with cols[j]:
                    # Usar container para cada tarjeta
                    with st.container():
                        st.markdown(f"""
                            <div style="
                                background: white;
                                border-radius: 8px;
                                padding: 20px;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                                border-left: 4px solid #0079BF;
                                margin-bottom: 20px;
                            ">
                                <div style="
                                    font-size: 1.1em;
                                    font-weight: bold;
                                    color: #172B4D;
                                    margin-bottom: 12px;
                                    padding-bottom: 8px;
                                    border-bottom: 2px solid #DFE1E6;
                                ">
                                    <span style="
                                        background: #0079BF;
                                        color: white;
                                        padding: 2px 8px;
                                        border-radius: 4px;
                                        font-size: 0.85em;
                                    ">ID: {aseg['id']}</span>
                                    <div style="margin-top: 8px;">{aseg['nombre']}</div>
                                </div>
                                <div style="margin: 8px 0; font-size: 0.9em;">
                                    <strong style="color: #5E6C84;">📍 Web:</strong>
                                    <span style="color: #172B4D;">{aseg['direccion']}</span>
                                </div>
                                <div style="margin: 8px 0; font-size: 0.9em;">
                                    <strong style="color: #5E6C84;">📞 Representante:</strong>
                                    <span style="color: #172B4D;">{aseg['telefono']}</span>
                                </div>
                                <div style="margin: 8px 0; font-size: 0.9em;">
                                    <strong style="color: #5E6C84;">📧 Email:</strong>
                                    <span style="color: #172B4D;">{aseg['email']}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

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
