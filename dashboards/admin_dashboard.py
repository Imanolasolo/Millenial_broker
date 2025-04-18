import streamlit as st
import sqlite3
import bcrypt
from dbconfig import DB_FILE
from user_crud import create_user, read_users, update_user, delete_user
from client_crud import create_client, read_clients, update_client, delete_client
from create_dashboard import create_dashboard  # Importar la función para crear dashboards

# Inicializar la base de datos y crear tablas si no existen
def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # Crear tabla de clientes si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT NOT NULL
            )
        """)
        # Crear tabla de roles si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        conn.commit()
    except Exception as e:
        st.error(f"Error al inicializar la base de datos: {e}")
    finally:
        conn.close()

# Llamar a la función de inicialización al inicio
initialize_database()

def admin_dashboard():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo.png", width=100)
    with col2:
        st.title("Dashboard de Administrador")
    st.write("Bienvenido, administrador")
    
    # Mensaje de bienvenida enriquecido
    st.markdown("""
        Este es el centro de control para gestionar usuarios, clientes, reportes y configuraciones del sistema.
        Utiliza la barra lateral para navegar entre los diferentes módulos.
    """)

    # Instrucciones básicas en un expander
    with st.expander("Instrucciones Básicas"):
        st.markdown("""
        ### Cómo usar el Dashboard:        
        1. **Usuarios**: Gestiona los usuarios del sistema (crear, leer, modificar, borrar).
        2. **Clientes**: Administra la información de los clientes (crear, leer, modificar, borrar).
        3. **Reportes**: Genera y visualiza reportes relevantes.
        4. **Configuración**: Ajusta las configuraciones del sistema según sea necesario.
        5. **Roles**: Gestiona los roles disponibles en el sistema.
        6. **Logout**: Cierra la sesión de administrador de forma segura.
        
        ### Notas:
        - Asegúrate de completar todos los campos requeridos al realizar operaciones.
        - Los cambios realizados se guardarán automáticamente en la base de datos.
        - Si tienes dudas, contacta al equipo de soporte técnico.
        """)

    # Add custom CSS for sidebar buttons
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {  /* Sidebar background */
            background-color: #3A92AB !important;  /* Blue color */
        }
        [data-testid="stSidebar"] button {  /* Sidebar buttons */
            background-color: white !important;
            color: black !important;
            border: 1px solid #007BFF !important;
        }
        [data-testid="stSidebar"] button:hover {  /* Hover effect for buttons */
            background-color: #e6e6e6 !important;  /* Light gray */
        }
        </style>
    """, unsafe_allow_html=True)

    # Inicializar el estado de la sesión para el módulo y operación seleccionada
    if "module" not in st.session_state:
        st.session_state["module"] = None
    if "client_operation" not in st.session_state:
        st.session_state["client_operation"] = None

    # Sidebar para navegación entre módulos
    st.sidebar.title("Navegación")
    st.sidebar.image("logo.png", width=80)
    if st.sidebar.button("Usuarios"):
        st.session_state["module"] = "Usuarios"
    if st.sidebar.button("Reportes"):
        st.session_state["module"] = "Reportes"
    if st.sidebar.button("Configuración"):
        st.session_state["module"] = "Configuración"
    if st.sidebar.button("Clientes"):
        st.session_state["module"] = "Clientes"
    if st.sidebar.button("Roles"):
        st.session_state["module"] = "Roles"

    module = st.session_state["module"]

    # Nuevo módulo CRUD para roles
    if module == "Roles":
        st.subheader("Gestión de Roles")
        operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"], key="role_operation")

        if operation == "Crear":
            st.subheader("Crear Nuevo Rol")
            new_role_name = st.text_input("Nombre del Rol", key="new_role_name")

            if st.button("Crear Rol", key="create_role_button"):
                if new_role_name:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO roles (name) VALUES (?)", (new_role_name,))
                        conn.commit()
                        st.success("Rol creado exitosamente")
                        
                        # Crear automáticamente el dashboard para el nuevo rol
                        create_dashboard(new_role_name)
                    except sqlite3.IntegrityError:
                        st.error("El rol ya existe")
                    finally:
                        conn.close()
                else:
                    st.error("Por favor, ingresa un nombre para el rol.")

        elif operation == "Leer":
            st.subheader("Lista de Roles")
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM roles")
            roles = cursor.fetchall()
            conn.close()
            if roles:
                for role in roles:
                    st.write(f"ID: {role[0]}, Nombre: {role[1]}")
            else:
                st.info("No hay roles registrados.")

        elif operation == "Modificar":
            st.subheader("Modificar Rol")
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM roles")
            roles = cursor.fetchall()
            conn.close()

            if roles:
                selected_role = st.selectbox("Selecciona un rol para modificar", roles, format_func=lambda x: x[1])
                new_role_name = st.text_input("Nuevo Nombre del Rol", key="new_role_name_modify")

                if st.button("Modificar Rol"):
                    if new_role_name:
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        try:
                            cursor.execute("UPDATE roles SET name = ? WHERE id = ?", (new_role_name, selected_role[0]))
                            conn.commit()
                            st.success("Rol modificado exitosamente")
                        except sqlite3.IntegrityError:
                            st.error("El nuevo nombre del rol ya existe")
                        finally:
                            conn.close()
                    else:
                        st.error("Por favor, ingresa un nuevo nombre para el rol.")

        elif operation == "Borrar":
            st.subheader("Borrar Rol")
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM roles")
            roles = cursor.fetchall()
            conn.close()

            if roles:
                selected_role = st.selectbox("Selecciona un rol para borrar", roles, format_func=lambda x: x[1])

                if st.button("Borrar Rol"):
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("DELETE FROM roles WHERE id = ?", (selected_role[0],))
                        conn.commit()
                        st.success("Rol borrado exitosamente")
                    except sqlite3.IntegrityError:
                        st.error("No se puede borrar el rol porque está asignado a usuarios.")
                    finally:
                        conn.close()
            else:
                st.info("No hay roles disponibles para borrar.")

    elif module == "Usuarios":
        st.subheader("Gestión de Usuarios")
        operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

        if operation == "Crear":
            st.subheader("Crear Nuevo Usuario")
            new_username = st.text_input("Nombre de Usuario")
            new_password = st.text_input("Contraseña", type="password")

            # Obtener roles dinámicamente
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM roles")
            roles = [role[0] for role in cursor.fetchall()]
            conn.close()

            new_role = st.selectbox("Rol", roles)  # Opciones de roles dinámicas

            if st.button("Crear Usuario"):
                if new_username and new_password:
                    result = create_user(new_username, new_password, new_role)
                    st.success(result) if "exitosamente" in result else st.error(result)
                else:
                    st.error("Por favor, completa todos los campos.")

        elif operation == "Leer":
            st.subheader("Lista de Usuarios")
            users = read_users()
            if users:
                for user in users:
                    st.write(f"Usuario: {user[0]}, Rol: {user[1]}")
            else:
                st.info("No hay usuarios registrados.")

        elif operation == "Modificar":
            st.subheader("Modificar Usuario")
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users")
            users = [user[0] for user in cursor.fetchall()]
            conn.close()

            if users:
                selected_user = st.selectbox("Selecciona un usuario para modificar", users)

                # Obtener roles dinámicamente
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM roles")
                roles = [role[0] for role in cursor.fetchall()]
                conn.close()

                new_role = st.selectbox("Nuevo Rol", roles)
                new_password = st.text_input("Nueva Contraseña (opcional)", type="password")

                if st.button("Modificar Usuario"):
                    result = update_user(selected_user, new_role, new_password)
                    st.success(result) if "exitosamente" in result else st.error(result)
            else:
                st.info("No hay usuarios disponibles para modificar.")

        elif operation == "Borrar":
            st.subheader("Borrar Usuario")
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users")
            users = [user[0] for user in cursor.fetchall()]
            conn.close()

            if users:
                selected_user = st.selectbox("Selecciona un usuario para borrar", users)

                if st.button("Borrar Usuario"):
                    result = delete_user(selected_user)
                    st.success(result) if "exitosamente" in result else st.error(result)
            else:
                st.info("No hay usuarios disponibles para borrar.")

    elif module == "Reportes":
        st.subheader("Módulo de Reportes")
        st.write("Aquí puedes ver y generar reportes.")

    elif module == "Configuración":
        st.subheader("Módulo de Configuración")
        st.write("Aquí puedes configurar las opciones del sistema.")

    elif module == "Clientes":
        st.subheader("Gestión de Clientes")
        operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"], 
                                 key="client_operation")

        if operation == "Crear":
            st.subheader("Crear Nuevo Cliente")
            new_client_name = st.text_input("Nombre del Cliente", key="new_client_name")
            new_client_email = st.text_input("Correo Electrónico", key="new_client_email")
            new_client_phone = st.text_input("Teléfono", key="new_client_phone")

            if st.button("Crear Cliente", key="create_client_button"):
                if new_client_name and new_client_email and new_client_phone:
                    result = create_client(new_client_name, new_client_email, new_client_phone)
                    st.success(result) if "exitosamente" in result else st.error(result)
                else:
                    st.error("Por favor, completa todos los campos.")

        elif operation == "Leer":
            st.subheader("Lista de Clientes")
            clients = read_clients()
            if clients:
                for client in clients:
                    st.write(f"Nombre: {client[0]}, Correo: {client[1]}, Teléfono: {client[2]}")
            else:
                st.info("No hay clientes registrados.")

        elif operation == "Modificar":
            st.subheader("Modificar Cliente")
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM clients")
            clients = [client[0] for client in cursor.fetchall()]
            conn.close()

            if clients:
                selected_client = st.selectbox("Selecciona un cliente para modificar", clients)
                new_name = st.text_input("Nuevo Nombre (opcional)")
                new_phone = st.text_input("Nuevo Teléfono (opcional)")

                if st.button("Modificar Cliente"):
                    result = update_client(selected_client, new_name, new_phone)
                    st.success(result) if "exitosamente" in result else st.error(result)
            else:
                st.info("No hay clientes disponibles para modificar.")

        elif operation == "Borrar":
            st.subheader("Borrar Cliente")
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM clients")
            clients = [client[0] for client in cursor.fetchall()]
            conn.close()

            if clients:
                selected_client = st.selectbox("Selecciona un cliente para borrar", clients)

                if st.button("Borrar Cliente"):
                    result = delete_client(selected_client)
                    st.success(result) if "exitosamente" in result else st.error(result)
            else:
                st.info("No hay clientes disponibles para borrar.")

    # Botón de Logout
    if st.sidebar.button("Logout"):
        del st.session_state["token"]  # Eliminar el token de la sesión
        st.success("Sesión cerrada exitosamente")
        st.rerun()  # Recargar la página para volver al login