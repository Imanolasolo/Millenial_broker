import streamlit as st
import sqlite3
from dbconfig import DB_FILE

def crud_agencias():
    st.subheader("Gestión de Agencias")
    operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

    if operation == "Crear":
        with st.form("crear_agencia"):
            name = st.text_input("Nombre de la Agencia")
            address = st.text_area("Dirección")
            phone = st.text_input("Teléfono")
            email = st.text_input("Correo Electrónico")
            submit_button = st.form_submit_button("Crear Agencia")
            if submit_button:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO companies (name, address, phone, email)
                        VALUES (?, ?, ?, ?)
                    """, (name, address, phone, email))
                    conn.commit()
                    st.success("Agencia creada exitosamente")
                except sqlite3.IntegrityError:
                    st.error("El nombre de la agencia ya existe.")
                finally:
                    conn.close()

    elif operation == "Leer":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, address, phone, email FROM companies")
        columns = [col[0] for col in cursor.description]
        agencias = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        if agencias:
            import pandas as pd
            df = pd.DataFrame(agencias)
            st.dataframe(df)
        else:
            st.info("No hay agencias registradas.")

    elif operation == "Modificar":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM companies")
        agencias = cursor.fetchall()
        conn.close()
        selected_agencia = st.selectbox("Selecciona una agencia", agencias, format_func=lambda x: x[1])
        if selected_agencia:
            name = st.text_input("Nombre de la Agencia", value=selected_agencia[1])
            address = st.text_area("Dirección")
            phone = st.text_input("Teléfono")
            email = st.text_input("Correo Electrónico")
            if st.button("Actualizar Agencia"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        UPDATE companies
                        SET name = ?, address = ?, phone = ?, email = ?
                        WHERE id = ?
                    """, (name, address, phone, email, selected_agencia[0]))
                    conn.commit()
                    st.success("Agencia actualizada exitosamente")
                except sqlite3.IntegrityError:
                    st.error("Error al actualizar la agencia.")
                finally:
                    conn.close()

    elif operation == "Borrar":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM companies")
        agencias = cursor.fetchall()
        conn.close()
        selected_agencia = st.selectbox("Selecciona una agencia para eliminar", agencias, format_func=lambda x: x[1])
        if st.button("Eliminar Agencia"):
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM companies WHERE id = ?", (selected_agencia[0],))
                conn.commit()
                st.success("Agencia eliminada exitosamente")
            except sqlite3.IntegrityError:
                st.error("No se puede eliminar la agencia asignada a usuarios.")
            finally:
                conn.close()
