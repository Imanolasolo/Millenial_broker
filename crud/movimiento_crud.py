import streamlit as st
import sqlite3
from dbconfig import DB_FILE, initialize_database

def tipos_movimiento_permitidos():
    return [
        "Endoso de Beneficiario",
        "Anexo de Aumento de Suma Asegurada",
        "Anexo de Disminución de Suma Asegurada",
        "Inclusión de Direcciones",
        "Exclusión de Direcciones",
        "Anexo Aclaratorio",
        "Anexo de Aumento de Prima",
        "Anexo de Disminución de Prima",
        "Cancelación",
        "Anulación",
        "Rehabilitación",
        "Renovación"
    ]

def get_poliza_options():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, numero_poliza FROM polizas")
    polizas = cursor.fetchall()
    conn.close()
    return [(p[0], p[1]) for p in polizas]

def get_client_options():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombres, apellidos, razon_social, tipo_cliente FROM clients")
    clients = cursor.fetchall()
    conn.close()
    options = []
    for c in clients:
        if c[4] == "Persona Jurídica":
            label = f"{c[3]} (PJ) [ID: {c[0]}]"
        else:
            label = f"{c[1]} {c[2]} (PN) [ID: {c[0]}]"
        options.append((c[0], label))
    return options

def crud_movimientos():
    st.subheader("Gestión de Movimientos de Pólizas")
    col1, col2, col3 = st.columns(3)
    with col1:
        operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

    # Reiniciar el proceso y los datos cada vez que se cambia de operación
    if "last_movimiento_operation" not in st.session_state or st.session_state["last_movimiento_operation"] != operation:
        st.session_state["movimiento_form_data"] = {}
        st.session_state["last_movimiento_operation"] = operation

    # Obtener columnas de la tabla movimientos_poliza
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(movimientos_poliza)")
    columns_info = cursor.fetchall()
    movimiento_fields = [col[1] for col in columns_info if col[1] != "id"]
    conn.close()

    if operation == "Crear":
        with st.form("crear_movimiento_form"):
            codigo_movimiento = st.text_input("Código único de movimiento")
            fecha_movimiento = st.date_input("Fecha de movimiento")
            tipo_movimiento = st.selectbox("Tipo de movimiento", tipos_movimiento_permitidos())
            poliza_options = get_poliza_options()
            poliza_id = st.selectbox("Póliza asociada", poliza_options, format_func=lambda x: x[1] if x else "", key="poliza_movimiento") if poliza_options else None
            client_options = get_client_options()
            cliente_id = st.selectbox("Cliente asociado", client_options, format_func=lambda x: x[1] if x else "", key="cliente_movimiento") if client_options else None
            pdf_path = st.text_input("Ruta/archivo PDF adjunto")
            observaciones = st.text_area("Observaciones del ejecutivo")
            estado = st.selectbox("Estado", ["Proceso", "Aprobado", "Aplicado"])
            submitted = st.form_submit_button("Crear movimiento")
            if submitted:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO movimientos_poliza 
                    (codigo_movimiento, fecha_movimiento, tipo_movimiento, poliza_id, cliente_id, pdf_documento, observaciones, estado)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    codigo_movimiento,
                    fecha_movimiento.strftime("%Y-%m-%d"),
                    tipo_movimiento,
                    poliza_id[0] if poliza_id else None,
                    cliente_id[0] if cliente_id else None,
                    pdf_path,
                    observaciones,
                    estado
                ))
                conn.commit()
                conn.close()
                st.success("Movimiento creado exitosamente.")
                st.rerun()

    elif operation == "Leer":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movimientos_poliza")
        movimientos = cursor.fetchall()
        conn.close()
        if movimientos:
            st.markdown("### Movimientos registrados")
            import pandas as pd
            df = pd.DataFrame(movimientos, columns=[col[1] for col in columns_info])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No hay movimientos registrados.")

    elif operation == "Modificar":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo_movimiento FROM movimientos_poliza")
        movimientos = cursor.fetchall()
        if not movimientos:
            st.info("No hay movimientos registrados.")
            conn.close()
            return
        selected_movimiento = st.selectbox("Selecciona un movimiento", movimientos, format_func=lambda x: f"{x[1]} (ID: {x[0]})")
        if selected_movimiento:
            cursor.execute("SELECT * FROM movimientos_poliza WHERE id=?", (selected_movimiento[0],))
            movimiento_actual = cursor.fetchone()
            conn.close()
            if not movimiento_actual:
                st.error("No se encontró el movimiento seleccionado.")
                return
            movimiento_dict = dict(zip([col[1] for col in columns_info], movimiento_actual))
            with st.form("modificar_movimiento_form"):
                codigo_movimiento = st.text_input("Código único de movimiento", value=movimiento_dict.get("codigo_movimiento", ""))
                import datetime
                fecha_val = movimiento_dict.get("fecha_movimiento")
                try:
                    fecha_val = datetime.datetime.strptime(fecha_val, "%Y-%m-%d").date() if fecha_val else None
                except Exception:
                    fecha_val = None
                fecha_movimiento = st.date_input("Fecha de movimiento", value=fecha_val)
                tipo_movimiento = st.selectbox("Tipo de movimiento", tipos_movimiento_permitidos(), index=tipos_movimiento_permitidos().index(movimiento_dict.get("tipo_movimiento", tipos_movimiento_permitidos()[0])))
                poliza_options = get_poliza_options()
                poliza_id = st.selectbox("Póliza asociada", poliza_options, index=[p[0] for p in poliza_options].index(movimiento_dict.get("poliza_id")) if movimiento_dict.get("poliza_id") in [p[0] for p in poliza_options] else 0, format_func=lambda x: x[1] if x else "")
                client_options = get_client_options()
                cliente_id = st.selectbox("Cliente asociado", client_options, index=[c[0] for c in client_options].index(movimiento_dict.get("cliente_id")) if movimiento_dict.get("cliente_id") in [c[0] for c in client_options] else 0, format_func=lambda x: x[1] if x else "")
                pdf_path = st.text_input("Ruta/archivo PDF adjunto", value=movimiento_dict.get("pdf_documento", ""))
                observaciones = st.text_area("Observaciones del ejecutivo", value=movimiento_dict.get("observaciones", ""))
                estado = st.selectbox("Estado", ["Proceso", "Aprobado", "Aplicado"], index=["Proceso", "Aprobado", "Aplicado"].index(movimiento_dict.get("estado", "Proceso")) if movimiento_dict.get("estado") in ["Proceso", "Aprobado", "Aplicado"] else 0)
                submitted = st.form_submit_button("Actualizar movimiento")
                if submitted:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE movimientos_poliza SET
                            codigo_movimiento = ?,
                            fecha_movimiento = ?,
                            tipo_movimiento = ?,
                            poliza_id = ?,
                            cliente_id = ?,
                            pdf_documento = ?,
                            observaciones = ?,
                            estado = ?
                        WHERE id = ?
                    """, (
                        codigo_movimiento,
                        fecha_movimiento.strftime("%Y-%m-%d"),
                        tipo_movimiento,
                        poliza_id[0] if poliza_id else None,
                        cliente_id[0] if cliente_id else None,
                        pdf_path,
                        observaciones,
                        estado,
                        selected_movimiento[0]
                    ))
                    conn.commit()
                    conn.close()
                    st.success("Movimiento actualizado exitosamente.")
                    st.experimental_rerun()

    elif operation == "Borrar":
        st.warning("⚠️ Esta acción eliminará permanentemente el movimiento seleccionado.")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo_movimiento FROM movimientos_poliza")
        movimientos = cursor.fetchall()
        if not movimientos:
            st.info("No hay movimientos registrados para eliminar.")
            conn.close()
            return
        selected_movimiento = st.selectbox("Selecciona el movimiento a eliminar", movimientos, format_func=lambda x: f"{x[1]} (ID: {x[0]})")
        if selected_movimiento:
            confirmar = st.checkbox("Confirmo que deseo eliminar este movimiento permanentemente")
            if st.button("🗑️ ELIMINAR MOVIMIENTO", disabled=not confirmar):
                try:
                    cursor.execute("DELETE FROM movimientos_poliza WHERE id = ?", (selected_movimiento[0],))
                    conn.commit()
                    st.success("Movimiento eliminado exitosamente.")
                    st.rerun()
                except sqlite3.Error as e:
                    st.error(f"Error al eliminar el movimiento: {str(e)}")
        conn.close()

