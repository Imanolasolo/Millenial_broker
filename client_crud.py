import sqlite3
import os
from dbconfig import DB_FILE

# Update the database schema to include the new fields
def initialize_clients_table():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_cliente TEXT,
            nombres TEXT,
            apellidos TEXT,
            razon_social TEXT,
            tipo_documento TEXT,
            numero_documento TEXT,
            fecha_nacimiento TEXT,
            nacionalidad TEXT,
            sexo TEXT,
            estado_civil TEXT,
            correo_electronico TEXT,
            telefono_movil TEXT,
            telefono_fijo TEXT,
            direccion_domicilio TEXT,
            provincia TEXT,
            ciudad TEXT,
            codigo_postal TEXT,
            ocupacion_profesion TEXT,
            empresa_trabajo TEXT,
            tipo_empresa TEXT,
            ingresos_mensuales TEXT,
            nivel_educacion TEXT,
            fumador TEXT,
            actividades_riesgo TEXT,
            historial_medico TEXT,
            historial_siniestros TEXT,
            vehiculos_registrados TEXT,
            propiedades TEXT,
            tipo_contribuyente TEXT,
            numero_ruc TEXT,
            representante_legal_id INTEGER,
            observaciones_legales TEXT,
            canal_preferido_contacto TEXT,
            notas_adicionales TEXT,
            fecha_registro TEXT,
            ultima_actualizacion TEXT
        )
    ''')
    conn.commit()
    conn.close()

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
    # Eliminar el archivo de la base de datos si existe
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    # Crear las tablas nuevamente
    initialize_clients_table()
    # Puedes llamar aquí otras funciones de inicialización si es necesario
