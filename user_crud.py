import sqlite3
import os
import bcrypt
from dbconfig import DB_FILE

# Crear tabla de usuarios
def initialize_users_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            correo TEXT,
            nombres TEXT,
            apellidos TEXT,
            telefono TEXT,
            fecha_registro TEXT,
            ultima_actualizacion TEXT
        )
    ''')
    # Check and add missing columns
    existing_columns = [col[1] for col in cursor.execute("PRAGMA table_info(users)").fetchall()]
    if "correo" not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN correo TEXT")
    conn.commit()
    conn.close()

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
            INSERT INTO users ({fields})
            VALUES ({placeholders})
        ''', tuple(data.values()))
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
        cursor.execute("SELECT * FROM users")
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
            updates["password"] = bcrypt.hashpw(updates["password"].encode('utf-8'), bcrypt.gensalt())

        fields = ', '.join([f"{field}=?" for field in updates.keys()])
        values = list(updates.values()) + [username]
        cursor.execute(f'''
            UPDATE users SET {fields} WHERE username=?
        ''', values)
        conn.commit()
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
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    initialize_users_table()
