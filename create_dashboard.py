import os
import sqlite3
from dbconfig import DB_FILE
import streamlit as st

def create_dashboard(role_name):
    """
    Crea un archivo de dashboard para un nuevo rol.
    
    Args:
        role_name (str): Nombre del rol para el cual se creará el dashboard.
    """
    # Definir la ruta del archivo
    dashboard_dir = "f:\\CODECODIX\\MILLENIAL_BROKER_project\\dashboards"
    os.makedirs(dashboard_dir, exist_ok=True)
    file_path = os.path.join(dashboard_dir, f"{role_name}_dashboard.py")
    
    # Contenido del archivo
    content = f"""
# filepath: {file_path}
# Dashboard para el rol: {role_name}
import streamlit as st
def welcome_message():
    st.header("Bienvenido al dashboard del rol: :red[ {role_name} ]")

def manage_modules():
    # Aquí se gestionarán los modulos necesarios para este rol
    st.write("Gestionando modulos para el rol: {role_name}")

    if st.button("Logout"):
        del st.session_state["token"]  # Eliminar el token de la sesión
        st.success("Sesion cerrada exitosamente")
        st.rerun()  # Recargar la página para volver al login
    """
    # Crear el archivo
    with open(file_path, "w") as file:
        file.write(content.strip())
    st.success(f"Dashboard creado: {file_path}")

def create_dashboards_for_existing_roles():
    """
    Crea dashboards para todos los roles existentes en la base de datos.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM roles")
        roles = cursor.fetchall()
        for role in roles:
            role_name = role[0]
            create_dashboard(role_name)
    except Exception as e:
        print(f"Error al crear dashboards para roles existentes: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_dashboards_for_existing_roles()
