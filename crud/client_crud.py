import sqlite3
import os
from dbconfig import DB_FILE
from database_config import initialize_database, reset_database

# Update the create_client function to handle all fields
def create_client(**data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # Validar longitud del número de documento
        if data['tipo_documento'].lower() == 'cedula' and len(data['numero_documento']) != 10:
            return "El número de cédula debe tener exactamente 10 dígitos."
        if data['tipo_documento'].lower() == 'ruc' and len(data['numero_documento']) != 13:
            return "El número de RUC debe tener exactamente 13 dígitos."

        # Verificar duplicados en nombres, apellidos, número de documento y correo electrónico
        cursor.execute(
            "SELECT * FROM clients WHERE nombres=? AND apellidos=? AND numero_documento=? AND correo_electronico=?",
            (data['nombres'], data['apellidos'], data['numero_documento'], data['correo_electronico'])
        )
        if cursor.fetchone():
            return f"El cliente con nombre '{data['nombres']} {data['apellidos']}', número de documento '{data['numero_documento']}' y correo '{data['correo_electronico']}' ya existe."

        # Insertar cliente si no hay duplicados
        fields = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        cursor.execute(f'''
            INSERT INTO clients ({fields})
            VALUES ({placeholders})
        ''', tuple(data.values()))
        conn.commit()
        return f"Cliente '{data.get('nombres', 'N/A')} {data.get('apellidos', 'N/A')}' creado exitosamente."
    except Exception as e:
        return f"Error al crear el cliente: {e}"
    finally:
        conn.close()

# Update the read_clients function to fetch all fields
def read_clients():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM clients")
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        conn.close()

# Update the update_client function to handle all fields
def update_client(email, **updates):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        fields = ', '.join([f"{field}=?" for field in updates.keys()])
        values = list(updates.values()) + [email]
        cursor.execute(f"UPDATE clients SET {fields} WHERE correo_electronico=?", values)
        conn.commit()
        return f"Cliente con correo '{email}' modificado exitosamente."
    except Exception as e:
        return f"Error al modificar el cliente: {e}"
    finally:
        conn.close()

# Update the delete_client function to delete by client ID
def delete_client(client_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
        if cursor.rowcount == 0:
            return f"No se encontró un cliente con ID '{client_id}'."
        conn.commit()
        return f"Cliente con ID '{client_id}' borrado exitosamente."
    except Exception as e:
        return f"Error al borrar el cliente: {e}"
    finally:
        conn.close()

# Add a function to reset the database
def reset_database():
    # Eliminar el archivo de la base de datos si existe y crear las tablas nuevamente
    reset_database()