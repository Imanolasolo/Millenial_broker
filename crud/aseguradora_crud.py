import sqlite3
from dbconfig import DB_FILE

def create_aseguradora(data, ramo_ids):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO aseguradoras (
                tipo_contribuyente, tipo_identificacion, identificacion, razon_social,
                nombre_comercial, pais, representante_legal, aniversario, web, correo_electronico
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', data)
        aseguradora_id = cursor.lastrowid
        for ramo_id in ramo_ids:
            cursor.execute('INSERT INTO aseguradora_ramos (aseguradora_id, ramo_id) VALUES (?, ?)', (aseguradora_id, ramo_id))
        conn.commit()
        return "Aseguradora creada exitosamente."
    except sqlite3.IntegrityError:
        return "Error: La aseguradora ya existe o los datos son inválidos."
    finally:
        conn.close()

def read_aseguradoras():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM aseguradoras")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_aseguradora(id, data, ramo_ids):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE aseguradoras
            SET tipo_contribuyente=?, tipo_identificacion=?, identificacion=?, razon_social=?,
                nombre_comercial=?, pais=?, representante_legal=?, aniversario=?, web=?, correo_electronico=?
            WHERE id=?
        ''', (*data, id))
        cursor.execute('DELETE FROM aseguradora_ramos WHERE aseguradora_id=?', (id,))
        for ramo_id in ramo_ids:
            cursor.execute('INSERT INTO aseguradora_ramos (aseguradora_id, ramo_id) VALUES (?, ?)', (id, ramo_id))
        conn.commit()
        return "Aseguradora actualizada exitosamente."
    except sqlite3.IntegrityError:
        return "Error: No se pudo actualizar la aseguradora."
    finally:
        conn.close()

def delete_aseguradora(id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM aseguradoras WHERE id=?", (id,))
        conn.commit()
        return "Aseguradora eliminada exitosamente."
    except sqlite3.IntegrityError:
        return "Error: No se pudo eliminar la aseguradora."
    finally:
        conn.close()