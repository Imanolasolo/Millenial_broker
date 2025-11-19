# ============================================================================
# CRUD DE RAMOS DE SEGUROS - ramos_crud.py
# ============================================================================
# Operaciones CRUD para gestionar los ramos (tipos) de seguros
# Los ramos son categorías de seguros como Vida, Auto, Hogar, etc.
# ============================================================================

# Importaciones necesarias
import streamlit as st  # Framework de interfaz de usuario
import sqlite3  # Manejo de base de datos SQLite
import pandas as pd  # Manejo de DataFrames para visualización
from dbconfig import DB_FILE  # Ruta del archivo de base de datos
import datetime as dt  # Manejo de fechas

# ============================================================================
# FUNCIÓN: get_all_ramos
# Obtiene todos los ramos de seguros de la base de datos
# ============================================================================
def get_all_ramos():
    """
    Consulta todos los ramos de seguros y los retorna como DataFrame
    
    Retorna:
        pandas.DataFrame: DataFrame con todos los ramos ordenados por nombre
    """
    conn = sqlite3.connect(DB_FILE)
    try:
        query = "SELECT * FROM ramos_seguros ORDER BY nombre"
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        st.error(f"Error al obtener ramos: {str(e)}")
        return pd.DataFrame()
    finally:
        conn.close()

# ============================================================================
# FUNCIÓN: create_ramo
# Crea un nuevo ramo de seguros en la base de datos
# ============================================================================
def create_ramo(nombre, descripcion):
    """
    Inserta un nuevo ramo de seguros
    
    Parámetros:
        nombre (str): Nombre del ramo (único)
        descripcion (str): Descripción del ramo
    
    Retorna:
        tuple: (bool éxito, str mensaje)
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Insertar nuevo ramo
        cursor.execute('''
            INSERT INTO ramos_seguros (nombre, descripcion)
            VALUES (?, ?)
        ''', (nombre, descripcion))
        conn.commit()
        return True, "Ramo creado exitosamente"
    
    except sqlite3.IntegrityError:
        # El nombre ya existe (es UNIQUE)
        return False, "Ya existe un ramo con ese nombre"
    
    except Exception as e:
        # Otro error
        return False, f"Error al crear ramo: {str(e)}"
    
    finally:
        conn.close()

# ============================================================================
# FUNCIÓN: update_ramo
# Actualiza un ramo de seguros existente
# ============================================================================
def update_ramo(ramo_id, nombre, descripcion):
    """
    Modifica los datos de un ramo existente
    
    Parámetros:
        ramo_id (int): ID del ramo a actualizar
        nombre (str): Nuevo nombre
        descripcion (str): Nueva descripción
    
    Retorna:
        tuple: (bool éxito, str mensaje)
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Actualizar ramo
        cursor.execute('''
            UPDATE ramos_seguros 
            SET nombre = ?, descripcion = ?
            WHERE id = ?
        ''', (nombre, descripcion, ramo_id))
        conn.commit()
        
        # Verificar si se actualizó algún registro
        if cursor.rowcount > 0:
            return True, "Ramo actualizado exitosamente"
        else:
            return False, "No se encontró el ramo especificado"
    
    except sqlite3.IntegrityError:
        # El nombre ya existe
        return False, "Ya existe un ramo con ese nombre"
    
    except Exception as e:
        return False, f"Error al actualizar ramo: {str(e)}"
    
    finally:
        conn.close()

# ============================================================================
# FUNCIÓN: delete_ramo
# Elimina un ramo de seguros (con validación de uso)
# ============================================================================
def delete_ramo(ramo_id):
    """
    Elimina un ramo de seguros si no está siendo usado
    
    Parámetros:
        ramo_id (int): ID del ramo a eliminar
    
    Retorna:
        tuple: (bool éxito, str mensaje)
    """
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # ============================================================================
        # VALIDACIÓN: Verificar si el ramo está siendo usado en pólizas
        # ============================================================================
        cursor.execute("SELECT COUNT(*) FROM polizas WHERE ramo_id = ?", (ramo_id,))
        count = cursor.fetchone()[0]
        
        # Si está en uso, no permitir la eliminación (integridad referencial)
        if count > 0:
            return False, f"No se puede eliminar el ramo porque está siendo usado en {count} póliza(s)"
        
        # Si no está en uso, proceder con la eliminación
        cursor.execute("DELETE FROM ramos_seguros WHERE id = ?", (ramo_id,))
        conn.commit()
        
        # Verificar si se eliminó algún registro
        if cursor.rowcount > 0:
            return True, "Ramo eliminado exitosamente"
        else:
            return False, "No se encontró el ramo especificado"
    
    except Exception as e:
        return False, f"Error al eliminar ramo: {str(e)}"
    
    finally:
        conn.close()

def crud_ramos():
    """Interfaz principal del CRUD de ramos de seguros"""
    st.title("Gestión de Ramos de Seguros")
    
    # Tabs para diferentes operaciones
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Ver Ramos", "➕ Crear Ramo", "✏️ Editar Ramo", "🗑️ Eliminar Ramo"])
    
    with tab1:
        st.subheader("Lista de Ramos de Seguros")
        
        # Botón para refrescar datos
        if st.button("🔄 Refrescar"):
            st.rerun()
        
        # Obtener y mostrar datos
        df = get_all_ramos()
        
        if not df.empty:
            # Mostrar estadísticas
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total de Ramos", len(df))
            
            # Mostrar tabla
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "ID",
                    "nombre": "Nombre del Ramo",
                    "descripcion": "Descripción"
                }
            )
            
            # Opción para descargar como CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv,
                file_name=f"ramos_seguros_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No hay ramos de seguros registrados")
    
    with tab2:
        st.subheader("Crear Nuevo Ramo de Seguros")
        
        with st.form("crear_ramo"):
            nombre = st.text_input("Nombre del Ramo*", placeholder="Ej: Vida, Auto, Hogar")
            descripcion = st.text_area("Descripción", placeholder="Descripción del ramo de seguros")
            
            submitted = st.form_submit_button("Crear Ramo")
            
            if submitted:
                if not nombre.strip():
                    st.error("El nombre del ramo es obligatorio")
                else:
                    success, message = create_ramo(nombre.strip(), descripcion.strip())
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    with tab3:
        st.subheader("Editar Ramo de Seguros")
        
        df = get_all_ramos()
        if not df.empty:
            # Selector de ramo
            ramo_options = {f"{row['nombre']} (ID: {row['id']})": row['id'] for _, row in df.iterrows()}
            selected_ramo = st.selectbox("Seleccionar Ramo a Editar", options=list(ramo_options.keys()))
            
            if selected_ramo:
                ramo_id = ramo_options[selected_ramo]
                ramo_data = df[df['id'] == ramo_id].iloc[0]
                
                with st.form("editar_ramo"):
                    nombre = st.text_input("Nombre del Ramo*", value=ramo_data['nombre'])
                    descripcion = st.text_area("Descripción", value=ramo_data['descripcion'] if pd.notna(ramo_data['descripcion']) else "")
                    
                    submitted = st.form_submit_button("Actualizar Ramo")
                    
                    if submitted:
                        if not nombre.strip():
                            st.error("El nombre del ramo es obligatorio")
                        else:
                            success, message = update_ramo(ramo_id, nombre.strip(), descripcion.strip())
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
        else:
            st.info("No hay ramos de seguros para editar")
    
    with tab4:
        st.subheader("Eliminar Ramo de Seguros")
        
        df = get_all_ramos()
        if not df.empty:
            # Selector de ramo
            ramo_options = {f"{row['nombre']} (ID: {row['id']})": row['id'] for _, row in df.iterrows()}
            selected_ramo = st.selectbox("Seleccionar Ramo a Eliminar", options=list(ramo_options.keys()))
            
            if selected_ramo:
                ramo_id = ramo_options[selected_ramo]
                ramo_data = df[df['id'] == ramo_id].iloc[0]
                
                # Mostrar información del ramo a eliminar
                st.info(f"**Ramo seleccionado:** {ramo_data['nombre']}")
                if pd.notna(ramo_data['descripcion']) and ramo_data['descripcion']:
                    st.info(f"**Descripción:** {ramo_data['descripcion']}")
                
                # Confirmación de eliminación
                st.warning("⚠️ Esta acción no se puede deshacer")
                
                if st.button("🗑️ Confirmar Eliminación", type="secondary"):
                    success, message = delete_ramo(ramo_id)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
        else:
            st.info("No hay ramos de seguros para eliminar")
