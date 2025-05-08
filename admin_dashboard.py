import sqlite3
import pandas as pd  # Importar pandas para manejar fechas
from aseguradora_crud import create_aseguradora, update_aseguradora
from dbconfig import DB_FILE
import streamlit as st
import os

def get_ramos_seguros():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM ramos_seguros")
    ramos = cursor.fetchall()
    conn.close()
    return ramos

def add_ramo_seguro(nombre, descripcion):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO ramos_seguros (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))
        conn.commit()
        return "Ramo de seguro creado exitosamente."
    except sqlite3.IntegrityError:
        return "Error: El ramo de seguro ya existe o los datos son inválidos."
    finally:
        conn.close()

# Agregar una función para manejar el estado de la sesión
def set_session_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value
    else:
        st.session_state[key] = value

def get_session_state(key, default=None):
    return st.session_state.get(key, default)

def manage_aseguradoras():
    st.title("Gestión de Aseguradoras")

    # Seleccionar acción
    action = st.radio("Seleccione una acción", ["Crear", "Actualizar"])

    if action == "Crear":
        # Formulario para crear aseguradora
        with st.form("crear_aseguradora_form"):
            tipo_contribuyente = st.text_input("Tipo de Contribuyente")
            tipo_identificacion = st.text_input("Tipo de Identificación")
            identificacion = st.text_input("Identificación")
            razon_social = st.text_input("Razón Social")
            nombre_comercial = st.text_input("Nombre Comercial")
            pais = st.text_input("País")
            representante_legal = st.text_input("Representante Legal")
            aniversario = st.date_input("Aniversario")
            web = st.text_input("Web")
            correo_electronico = st.text_input("Correo Electrónico")

            # Dropdown para seleccionar ramos de seguros
            ramos = get_ramos_seguros()
            ramo_ids = st.multiselect(
                "Ramos de Seguros",
                options=[r[0] for r in ramos],
                format_func=lambda x: dict(ramos)[x]
            )

            # Botón para agregar un nuevo ramo de seguro
            with st.expander("Agregar nuevo ramo de seguro"):
                nuevo_ramo_nombre = st.text_input("Nombre del Ramo")
                nuevo_ramo_descripcion = st.text_area("Descripción del Ramo")
                if st.button("Crear Ramo", key="crear_ramo"):
                    if nuevo_ramo_nombre:
                        result = add_ramo_seguro(nuevo_ramo_nombre, nuevo_ramo_descripcion)
                        st.success(result)
                        set_session_state("reload", True)  # Marcar para recargar
                        st.experimental_rerun()  # Recargar la página

            submit = st.form_submit_button("Guardar")  # Botón de envío

            if submit:
                if not ramo_ids:
                    st.error("Debe seleccionar al menos un ramo de seguro.")
                    return

                data = (
                    tipo_contribuyente, tipo_identificacion, identificacion, razon_social,
                    nombre_comercial, pais, representante_legal, aniversario, web, correo_electronico
                )
                result = create_aseguradora(data, ramo_ids)
                st.success(result)

    elif action == "Actualizar":
        # Formulario para actualizar aseguradora
        with st.form("actualizar_aseguradora_form"):
            aseguradora_id = st.text_input("ID de Aseguradora")
            # Obtener datos de la aseguradora si el ID es válido
            if aseguradora_id:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM aseguradoras WHERE id=?", (aseguradora_id,))
                aseguradora = cursor.fetchone()
                conn.close()

                if aseguradora:
                    tipo_contribuyente = st.text_input("Tipo de Contribuyente", value=aseguradora[1])
                    tipo_identificacion = st.text_input("Tipo de Identificación", value=aseguradora[2])
                    identificacion = st.text_input("Identificación", value=aseguradora[3])
                    razon_social = st.text_input("Razón Social", value=aseguradora[4])
                    nombre_comercial = st.text_input("Nombre Comercial", value=aseguradora[5])
                    pais = st.text_input("País", value=aseguradora[6])
                    representante_legal = st.text_input("Representante Legal", value=aseguradora[7])
                    aniversario = st.date_input("Aniversario", value=pd.to_datetime(aseguradora[8]))
                    web = st.text_input("Sitio Web", value=aseguradora[9])
                    correo_electronico = st.text_input("Correo Electrónico", value=aseguradora[10])

                    # Dropdown para seleccionar ramos de seguros
                    ramos = get_ramos_seguros()
                    cursor.execute("SELECT ramo_id FROM aseguradora_ramos WHERE aseguradora_id=?", (aseguradora_id,))
                    selected_ramos = [row[0] for row in cursor.fetchall()]
                    ramo_ids = st.multiselect(
                        "Ramos de Seguros",
                        options=[r[0] for r in ramos],
                        default=selected_ramos,
                        format_func=lambda x: dict(ramos)[x]
                    )

                    # Botón para agregar un nuevo ramo de seguro
                    with st.expander("Agregar nuevo ramo de seguro"):
                        nuevo_ramo_nombre = st.text_input("Nombre del Ramo", key="update_ramo_nombre")
                        nuevo_ramo_descripcion = st.text_area("Descripción del Ramo", key="update_ramo_descripcion")
                        if st.button("Crear Ramo", key="update_ramo_button"):
                            if nuevo_ramo_nombre:
                                result = add_ramo_seguro(nuevo_ramo_nombre, nuevo_ramo_descripcion)
                                st.success(result)
                                set_session_state("reload", True)  # Marcar para recargar
                                st.experimental_rerun()  # Recargar la página

                    submit = st.form_submit_button("Guardar")  # Botón de envío

                    if submit:
                        data = (
                            tipo_contribuyente, tipo_identificacion, identificacion, razon_social,
                            nombre_comercial, pais, representante_legal, aniversario, web, correo_electronico
                        )
                        result = update_aseguradora(aseguradora_id, data, ramo_ids)
                        st.success(result)
                else:
                    st.error("No se encontró una aseguradora con el ID proporcionado.")

# Verificar si se necesita recargar la página
if get_session_state("reload", False):
    set_session_state("reload", False)  # Restablecer el estado
    st.experimental_rerun()