import streamlit as st
import sqlite3
from dbconfig import DB_FILE

def crud_roles():
    st.subheader("Gestión de Roles")
    operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

    if operation == "Crear":
        role_name = st.text_input("Nombre del Rol")
        if st.button("Crear Rol"):
            if role_name:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO roles (name) VALUES (?)", (role_name,))
                    conn.commit()
                    st.success("Rol creado exitosamente")
                except sqlite3.IntegrityError:
                    st.error("El rol ya existe.")
                finally:
                    conn.close()
            else:
                st.error("Ingresa un nombre para el rol.")

    elif operation == "Leer":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM roles")
        roles = cursor.fetchall()
        conn.close()
        if roles:
            import pandas as pd
            df = pd.DataFrame(roles, columns=["ID", "Nombre"])
            st.dataframe(df)
        else:
            st.info("No hay roles registrados.")

    elif operation == "Modificar":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM roles")
        roles = cursor.fetchall()
        conn.close()
        if not roles:
            st.info("No hay roles registrados.")
            return
        selected_role = st.selectbox("Selecciona un rol", roles, format_func=lambda x: x[1])
        new_name = st.text_input("Nuevo nombre del rol")
        if st.button("Modificar Rol"):
            if new_name:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                try:
                    cursor.execute("UPDATE roles SET name = ? WHERE id = ?", (new_name, selected_role[0]))
                    conn.commit()
                    st.success("Rol actualizado exitosamente")
                except sqlite3.IntegrityError:
                    st.error("El nuevo nombre ya existe.")
                finally:
                    conn.close()
            else:
                st.error("Ingresa un nuevo nombre.")

    elif operation == "Borrar":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM roles")
        roles = cursor.fetchall()
        conn.close()
        if not roles:
            st.info("No hay roles registrados.")
            return
        selected_role = st.selectbox("Selecciona un rol para eliminar", roles, format_func=lambda x: x[1])
        if st.button("Eliminar Rol"):
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM roles WHERE id = ?", (selected_role[0],))
                conn.commit()
                st.success("Rol eliminado exitosamente")
            except sqlite3.IntegrityError:
                st.error("No se puede eliminar el rol asignado a usuarios.")
            finally:
                conn.close()
