import sqlite3
from dbconfig import DB_FILE

def create_client(name, email, phone):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM clients WHERE email=?", (email,))
        if cursor.fetchone():
            return f"El cliente con correo '{email}' ya existe."
        cursor.execute("INSERT INTO clients (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
        conn.commit()
        return f"Cliente '{name}' creado exitosamente."
    except Exception as e:
        return f"Error al crear el cliente: {e}"
    finally:
        conn.close()

def read_clients():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name, email, phone FROM clients")
        return cursor.fetchall()
    finally:
        conn.close()

def update_client(email, new_name=None, new_phone=None):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        if new_name:
            cursor.execute("UPDATE clients SET name=? WHERE email=?", (new_name, email))
        if new_phone:
            cursor.execute("UPDATE clients SET phone=? WHERE email=?", (new_phone, email))
        conn.commit()
        return f"Cliente '{email}' modificado exitosamente."
    except Exception as e:
        return f"Error al modificar el cliente: {e}"
    finally:
        conn.close()

def delete_client(email):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM clients WHERE email=?", (email,))
        conn.commit()
        return f"Cliente '{email}' borrado exitosamente."
    except Exception as e:
        return f"Error al borrar el cliente: {e}"
    finally:
        conn.close()
