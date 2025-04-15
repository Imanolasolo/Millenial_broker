import sqlite3
import bcrypt
from dbconfig import DB_FILE

def create_user(username, password, role):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            return f"El nombre de usuario '{username}' ya existe."
        hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_pw, role))
        conn.commit()
        return f"Usuario '{username}' creado exitosamente con rol '{role}'."
    except Exception as e:
        return f"Error al crear el usuario: {e}"
    finally:
        conn.close()

def read_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username, role FROM users")
        return cursor.fetchall()
    finally:
        conn.close()

def update_user(username, new_role=None, new_password=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        if new_role:
            cursor.execute("UPDATE users SET role=? WHERE username=?", (new_role, username))
        if new_password:
            hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
            cursor.execute("UPDATE users SET password=? WHERE username=?", (hashed_pw, username))
        conn.commit()
        return f"Usuario '{username}' modificado exitosamente."
    except Exception as e:
        return f"Error al modificar el usuario: {e}"
    finally:
        conn.close()

def delete_user(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        return f"Usuario '{username}' borrado exitosamente."
    except Exception as e:
        return f"Error al borrar el usuario: {e}"
    finally:
        conn.close()
