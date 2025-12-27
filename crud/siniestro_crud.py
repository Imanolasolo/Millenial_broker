"""
CRUD de Siniestros
Operaciones para crear, leer, actualizar y eliminar siniestros
"""

import sqlite3
import streamlit as st
from dbconfig import DB_FILE
from datetime import datetime

def generate_codigo_siniestro(tipo_siniestro):
    """
    Genera un código único para el siniestro
    Formato: SIN-VEH-001 o SIN-SAL-001
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    prefix = "SIN-VEH" if tipo_siniestro == "Vehicular" else "SIN-SAL"
    
    cursor.execute(
        "SELECT codigo_siniestro FROM siniestros WHERE codigo_siniestro LIKE ? ORDER BY id DESC LIMIT 1",
        (f"{prefix}-%",)
    )
    last = cursor.fetchone()
    conn.close()
    
    if last and last[0]:
        try:
            num = int(last[0].split('-')[-1])
            return f"{prefix}-{num + 1:03d}"
        except:
            pass
    
    return f"{prefix}-001"

def create_siniestro(**data):
    """
    Crea un nuevo siniestro en la base de datos
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Generar código único
        if 'codigo_siniestro' not in data:
            data['codigo_siniestro'] = generate_codigo_siniestro(data.get('tipo_siniestro', 'Vehicular'))
        
        # Agregar fecha de registro
        data['fecha_registro'] = datetime.now().strftime('%Y-%m-%d')
        
        # Construir query de inserción
        fields = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        
        cursor.execute(
            f"INSERT INTO siniestros ({fields}) VALUES ({placeholders})",
            tuple(data.values())
        )
        
        conn.commit()
        siniestro_id = cursor.lastrowid
        return True, f"Siniestro {data['codigo_siniestro']} creado exitosamente", siniestro_id
    
    except Exception as e:
        return False, f"Error al crear siniestro: {str(e)}", None
    
    finally:
        conn.close()

def read_siniestros(tipo_siniestro=None, estado=None):
    """
    Lee todos los siniestros o filtrados por tipo y estado
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        query = """
            SELECT s.*, p.numero_poliza, c.nombres, c.apellidos
            FROM siniestros s
            LEFT JOIN polizas p ON s.poliza_id = p.id
            LEFT JOIN clients c ON s.cliente_id = c.id
            WHERE 1=1
        """
        params = []
        
        if tipo_siniestro:
            query += " AND s.tipo_siniestro = ?"
            params.append(tipo_siniestro)
        
        if estado:
            query += " AND s.estado = ?"
            params.append(estado)
        
        query += " ORDER BY s.fecha_siniestro DESC"
        
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    finally:
        conn.close()

def update_siniestro(siniestro_id, **updates):
    """
    Actualiza un siniestro existente
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        updates['fecha_actualizacion'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        fields = ', '.join([f"{k}=?" for k in updates.keys()])
        values = list(updates.values()) + [siniestro_id]
        
        cursor.execute(
            f"UPDATE siniestros SET {fields} WHERE id=?",
            values
        )
        
        conn.commit()
        return True, "Siniestro actualizado exitosamente"
    
    except Exception as e:
        return False, f"Error al actualizar siniestro: {str(e)}"
    
    finally:
        conn.close()

def delete_siniestro(siniestro_id):
    """
    Elimina un siniestro
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM siniestros WHERE id=?", (siniestro_id,))
        conn.commit()
        return True, "Siniestro eliminado exitosamente"
    
    except Exception as e:
        return False, f"Error al eliminar siniestro: {str(e)}"
    
    finally:
        conn.close()

def get_siniestro_by_id(siniestro_id):
    """
    Obtiene un siniestro por su ID
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT s.*, p.numero_poliza, c.nombres, c.apellidos
            FROM siniestros s
            LEFT JOIN polizas p ON s.poliza_id = p.id
            LEFT JOIN clients c ON s.cliente_id = c.id
            WHERE s.id = ?
        """, (siniestro_id,))
        
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        
        return dict(zip(columns, row)) if row else None
    
    finally:
        conn.close()
