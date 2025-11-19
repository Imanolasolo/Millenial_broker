# ============================================================================
# CRUD DE USUARIOS - user_crud.py
# ============================================================================
# Contiene todas las operaciones CRUD (Create, Read, Update, Delete) para usuarios
# Incluye encriptación de contraseñas con bcrypt y validaciones
# ============================================================================

# Importaciones necesarias
import sqlite3  # Manejo de base de datos SQLite
import os  # Operaciones del sistema operativo
import bcrypt  # Encriptación de contraseñas con hash seguro
import streamlit as st  # Framework de interfaz de usuario
from dbconfig import DB_FILE  # Ruta del archivo de base de datos
from database_config import initialize_database, reset_database  # Funciones de inicialización

# ============================================================================
# FUNCIÓN: create_user
# Crea un nuevo usuario en la base de datos con contraseña encriptada
# ============================================================================
def create_user(**data):
    """
    Crea un nuevo usuario en la base de datos
    
    Parámetros:
        **data: Diccionario con los datos del usuario (username, password, nombres, etc.)
    
    Retorna:
        str: Mensaje indicando éxito o error en la creación
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # ============================================================================
        # VALIDACIÓN: Verificar si el usuario ya existe
        # ============================================================================
        cursor.execute("SELECT * FROM users WHERE username = ?", (data['username'],))
        if cursor.fetchone():
            return f"El usuario '{data['username']}' ya existe."

        # ============================================================================
        # SEGURIDAD: Cifrar la contraseña con bcrypt
        # ============================================================================
        # bcrypt.hashpw genera un hash seguro de la contraseña
        # bcrypt.gensalt() genera un "salt" aleatorio para mayor seguridad
        data['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

        # ============================================================================
        # INSERCIÓN: Construir y ejecutar query SQL dinámicamente
        # ============================================================================
        # Construir la lista de campos y placeholders desde el diccionario data
        fields = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        
        # Insertar usuario en la base de datos
        cursor.execute(f'''
            INSERT INTO users ({fields}, company_id)
            VALUES ({placeholders}, ?)
        ''', tuple(data.values()) + (data.get("company_id"),))
        
        conn.commit()  # Confirmar cambios
        return f"Usuario '{data['username']}' creado exitosamente."
    
    except Exception as e:
        # Capturar y retornar cualquier error
        return f"Error al crear el usuario: {e}"
    
    finally:
        # Siempre cerrar la conexión a la base de datos
        conn.close()

# ============================================================================
# FUNCIÓN: read_users
# Lee todos los usuarios de la base de datos con información de su empresa
# ============================================================================
def read_users():
    """
    Obtiene todos los usuarios de la base de datos con sus datos completos
    Incluye nombre de la empresa asociada mediante LEFT JOIN
    
    Retorna:
        list: Lista de diccionarios con los datos de cada usuario
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # ============================================================================
        # CONSULTA: JOIN para obtener usuarios con nombre de empresa
        # ============================================================================
        # LEFT JOIN permite traer usuarios sin empresa asignada (company_id NULL)
        cursor.execute("""
            SELECT u.*, c.name AS company_name
            FROM users u
            LEFT JOIN companies c ON u.company_id = c.id
        """)
        
        # Obtener nombres de columnas de la consulta
        columns = [col[0] for col in cursor.description]
        
        # Convertir cada fila a diccionario con nombres de columnas como keys
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    finally:
        # Cerrar conexión
        conn.close()

# ============================================================================
# FUNCIÓN: update_user
# Actualiza los datos de un usuario existente identificado por username
# ============================================================================
def update_user(username, **updates):
    """
    Modifica los datos de un usuario en la base de datos
    
    Parámetros:
        username (str): Nombre de usuario a actualizar
        **updates: Diccionario con los campos a actualizar y sus nuevos valores
    
    Retorna:
        str: Mensaje indicando éxito o error en la actualización
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # ============================================================================
        # SEGURIDAD: Si se actualiza la contraseña, encriptarla
        # ============================================================================
        if "password" in updates:
            # Solo encriptar si es una contraseña nueva (no ya encriptada)
            # Las contraseñas bcrypt empiezan con "$2b$"
            updates["password"] = (
                bcrypt.hashpw(updates["password"].encode('utf-8'), bcrypt.gensalt())
                if isinstance(updates["password"], str) and not updates["password"].startswith("$2b$")
                else updates["password"]
            )

        # ============================================================================
        # CONSTRUCCIÓN: Construir query SQL dinámicamente
        # ============================================================================
        # Crear la parte SET de la query (campo1=?, campo2=?, ...)
        fields = ', '.join([f"{field}=?" for field in updates.keys()])
        # Valores a insertar: primero los valores de updates, luego el username
        values = list(updates.values()) + [username]

        # Ejecutar actualización
        cursor.execute(f'''
            UPDATE users SET {fields} WHERE username=?
        ''', values)
        conn.commit()

        # ============================================================================
        # VALIDACIÓN: Verificar si se actualizó algún registro
        # ============================================================================
        if cursor.rowcount == 0:
            return f"No se encontró el usuario '{username}' para actualizar."
        
        return f"Usuario '{username}' actualizado exitosamente."
    
    except Exception as e:
        return f"Error al actualizar el usuario: {e}"
    
    finally:
        conn.close()

# ============================================================================
# FUNCIÓN: delete_user
# Elimina un usuario de la base de datos por su username
# ============================================================================
def delete_user(username):
    """
    Elimina permanentemente un usuario de la base de datos
    
    Parámetros:
        username (str): Nombre de usuario a eliminar
    
    Retorna:
        str: Mensaje indicando éxito o error en la eliminación
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Ejecutar eliminación
        cursor.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        return f"Usuario '{username}' eliminado exitosamente."
    
    except Exception as e:
        return f"Error al eliminar el usuario: {e}"
    
    finally:
        conn.close()

# ============================================================================
# FUNCIÓN: reset_user_table
# Reinicia completamente la base de datos (CUIDADO: elimina todos los datos)
# ============================================================================
def reset_user_table():
    """
    Reinicia la base de datos eliminando y recreando todas las tablas
    ADVERTENCIA: Esta función elimina TODOS los datos
    """
    reset_database()  # Eliminar base de datos actual
    initialize_database()  # Crear estructura nueva

# ============================================================================
# FUNCIÓN: get_user_details
# Obtiene detalles específicos de un usuario por su username
# ============================================================================
def get_user_details(username):
    """
    Obtiene información detallada de un usuario específico
    
    Parámetros:
        username (str): Nombre de usuario a buscar
    
    Retorna:
        dict: Diccionario con username, nombre completo y empresa, o None si no existe
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Consultar usuario con JOIN para obtener nombre de empresa
        cursor.execute("""
            SELECT u.username, u.nombres, u.apellidos, c.name AS company_name
            FROM users u
            LEFT JOIN companies c ON u.company_id = c.id
            WHERE u.username = ?
        """, (username,))
        
        user = cursor.fetchone()
        
        if user:
            # Construir diccionario con los datos del usuario
            return {
                "username": user[0],
                "full_name": f"{user[1]} {user[2]}",
                "company_name": user[3] or "Sin afiliación"
            }
        
        # Si no se encuentra el usuario, retornar None
        return None
    
    finally:
        conn.close()

# ============================================================================
# FUNCIÓN: crud_usuarios
# Interfaz de usuario Streamlit para gestionar usuarios (CRUD completo)
# ============================================================================
def crud_usuarios():
    """
    Renderiza la interfaz completa de gestión de usuarios en Streamlit
    Permite crear, leer, modificar y borrar usuarios de manera interactiva
    """
    # Título de la sección
    st.subheader("Gestión de Usuarios")
    
    # Selector de operación CRUD
    operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

    if operation == "Crear":
        st.header("Crear Usuario")
        username = st.text_input("Nombre de usuario")
        password = st.text_input("Contraseña", type="password")
        nombres = st.text_input("Nombres")
        apellidos = st.text_input("Apellidos")
        company_id = st.text_input("ID de la compañía (opcional)")
        if st.button("Crear Usuario"):
            result = create_user(
                username=username,
                password=password,
                nombres=nombres,
                apellidos=apellidos,
                company_id=company_id if company_id else None
            )
            st.success(result)

    elif operation == "Leer":
        st.header("Usuarios")
        users = read_users()
        for user in users:
            st.write(f"{user['username']} - {user['nombres']} {user['apellidos']} - {user['company_name'] or 'Sin afiliación'}")

    elif operation == "Modificar":
        st.header("Modificar Usuario")
        users = read_users()
        if not users:
            st.info("No hay usuarios registrados.")
            return

        # Construir opciones para el selectbox
        user_options = []
        for user in users:
            label = f"{user.get('username', '')} ({user.get('role', 'Sin rol')})"
            user_options.append((user.get('username', ''), label))

        selected = st.selectbox("Selecciona un usuario para modificar", user_options, format_func=lambda x: x[1] if x else "")
        selected_username = selected[0] if selected else None
        selected_user = next((u for u in users if u.get('username') == selected_username), None)

        if selected_user:
            nuevos_nombres = st.text_input("Nuevos nombres", value=selected_user.get("nombres", ""))
            nuevos_apellidos = st.text_input("Nuevos apellidos", value=selected_user.get("apellidos", ""))
            nueva_contrasena = st.text_input("Nueva contraseña", type="password")
            if st.button("Actualizar Usuario"):
                updates = {
                    "nombres": nuevos_nombres,
                    "apellidos": nuevos_apellidos,
                }
                if nueva_contrasena:
                    updates["password"] = nueva_contrasena
                result = update_user(selected_username, **updates)
                st.success(result)
        else:
            st.warning("Usuario no encontrado.")

    elif operation == "Borrar":
        st.header("Borrar Usuario")
        users = read_users()
        if not users:
            st.info("No hay usuarios registrados.")
            return

        # Construir opciones para el selectbox
        user_options = []
        for user in users:
            label = f"{user.get('username', '')} ({user.get('role', 'Sin rol')})"
            user_options.append((user.get('username', ''), label))

        selected = st.selectbox("Selecciona un usuario para eliminar", user_options, format_func=lambda x: x[1] if x else "")
        selected_username = selected[0] if selected else None

        if st.button("Eliminar Usuario"):
            if selected_username:
                result = delete_user(selected_username)
                st.success(result)
            else:
                st.warning("Debes seleccionar un usuario para eliminar.")