import sqlite3
from dbconfig import DB_FILE

def create_aseguradora(nombre, direccion, telefono, email):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO aseguradoras (nombre, direccion, telefono, email) VALUES (?, ?, ?, ?)",
                   (nombre, direccion, telefono, email))
    conn.commit()
    conn.close()

def read_aseguradoras():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM aseguradoras")
    aseguradoras = cursor.fetchall()
    conn.close()
    return aseguradoras

def update_aseguradora(aseguradora_id, nombre, direccion, telefono, email):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE aseguradoras SET nombre=?, direccion=?, telefono=?, email=? WHERE id=?",
                   (nombre, direccion, telefono, email, aseguradora_id))
    conn.commit()
    conn.close()

def delete_aseguradora(aseguradora_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM aseguradoras WHERE id=?", (aseguradora_id,))
    conn.commit()
    conn.close()
