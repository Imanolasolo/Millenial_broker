import os
import sqlite3
from dbconfig import DB_FILE

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

def welcome_message():
    print("Bienvenido al dashboard del rol: {role_name}")

def manage_modules():
    # Aquí se gestionarán los módulos necesarios para este rol
    print("Gestionando módulos para el rol: {role_name}")
    """
    # Crear el archivo
    with open(file_path, "w") as file:
        file.write(content.strip())
    print(f"Dashboard creado: {file_path}")

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
