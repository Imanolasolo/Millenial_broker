import sqlite3
import streamlit as st
from dbconfig import DB_FILE

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

def crud_aseguradoras():
    st.subheader("Gestión de Aseguradoras")
    action = st.selectbox("Seleccione una acción", ["Crear", "Leer", "Actualizar", "Eliminar"])
    
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
        ramo_ids = st.multiselect("Seleccione los Ramos", [1, 2, 3, 4, 5])  # Ejemplo de IDs de ramos
        if st.button("Crear Aseguradora"):
            data = (tipo_contribuyente, tipo_identificacion, identificacion, razon_social,
                    nombre_comercial, pais, representante_legal, aniversario, web, correo_electronico)
            message = create_aseguradora(data, ramo_ids)
            st.success(message)
    
    elif action == "Leer":
        st.write("### Listado de Aseguradoras")
        aseguradoras = read_aseguradoras()
        for aseguradora in aseguradoras:
            st.write(aseguradora)
    
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
                ramo_ids = st.multiselect("Seleccione los Ramos", [1, 2, 3, 4, 5], default=aseguradora[11:])
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