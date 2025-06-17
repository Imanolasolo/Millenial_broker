import sqlite3
import os
import bcrypt
import streamlit as st
from dbconfig import DB_FILE
from database_config import initialize_database, reset_database

# Crear usuario
def create_user(**data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # Verificar si el usuario ya existe
        cursor.execute("SELECT * FROM users WHERE username = ?", (data['username'],))
        if cursor.fetchone():
            return f"El usuario '{data['username']}' ya existe."

        # Cifrar la contraseña
        data['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

        fields = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        cursor.execute(f'''
            INSERT INTO users ({fields}, company_id)
            VALUES ({placeholders}, ?)
        ''', tuple(data.values()) + (data.get("company_id"),))
        conn.commit()
        return f"Usuario '{data['username']}' creado exitosamente."
    except Exception as e:
        return f"Error al crear el usuario: {e}"
    finally:
        conn.close()

# Leer todos los usuarios
def read_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT u.*, c.name AS company_name
            FROM users u
            LEFT JOIN companies c ON u.company_id = c.id
        """)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        conn.close()

# Actualizar usuario por username
def update_user(username, **updates):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        if "password" in updates:
            updates["password"] = (
                bcrypt.hashpw(updates["password"].encode('utf-8'), bcrypt.gensalt())
                if isinstance(updates["password"], str) and not updates["password"].startswith("$2b$")
                else updates["password"]
            )

        # Construct the fields and values for the SQL query
        fields = ', '.join([f"{field}=?" for field in updates.keys()])
        values = list(updates.values()) + [username]

        cursor.execute(f'''
            UPDATE users SET {fields} WHERE username=?
        ''', values)
        conn.commit()

        # Check if any rows were affected
        if cursor.rowcount == 0:
            return f"No se encontró el usuario '{username}' para actualizar."
        return f"Usuario '{username}' actualizado exitosamente."
    except Exception as e:
        return f"Error al actualizar el usuario: {e}"
    finally:
        conn.close()

# Eliminar usuario por username
def delete_user(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        return f"Usuario '{username}' eliminado exitosamente."
    except Exception as e:
        return f"Error al eliminar el usuario: {e}"
    finally:
        conn.close()

# Reiniciar la base de datos (solo tabla de usuarios)
def reset_user_table():
    reset_database()
    initialize_database()

# Obtener detalles del usuario por username
def get_user_details(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT u.username, u.nombres, u.apellidos, c.name AS company_name
            FROM users u
            LEFT JOIN companies c ON u.company_id = c.id
            WHERE u.username = ?
        """, (username,))
        user = cursor.fetchone()
        if user:
            return {
                "username": user[0],
                "full_name": f"{user[1]} {user[2]}",
                "company_name": user[3] or "Sin afiliación"
            }
        return None
    finally:
        conn.close()

def crud_usuarios():
    st.subheader("Gestión de Usuarios")
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