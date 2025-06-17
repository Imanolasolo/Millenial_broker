import streamlit as st
import sqlite3
from dbconfig import DB_FILE

def get_next_numero_poliza():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT numero_poliza FROM polizas ORDER BY id DESC LIMIT 1")
    last = cursor.fetchone()
    conn.close()
    if last and last[0] and last[0].startswith("PRG-"):
        try:
            num = int(last[0].replace("PRG-", ""))
            return f"PRG-{num + 1}"
        except Exception:
            pass
    return "PRG-1"

def get_client_options():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, tipo_cliente, nombres, apellidos, razon_social FROM clients")
    clients = cursor.fetchall()
    conn.close()
    options = []
    for c in clients:
        if c[1] == "Empresa":
            label = f"{c[4]} (Empresa) [ID: {c[0]}]"
        else:
            label = f"{c[2]} {c[3]} (Individual) [ID: {c[0]}]"
        options.append((c[0], label))
    return options

def get_user_options():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    conn.close()
    options = []
    for u in users:
        label = f"{u[1]} ({u[2]}) [ID: {u[0]}]"
        options.append((u[0], label))
    return options

def crud_polizas():
    st.subheader("Gestión de Pólizas")
    operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

    # Obtener columnas de la tabla polizas para usarlas en el formulario de creación
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(polizas)")
    columns_info = cursor.fetchall()
    conn.close()
    poliza_fields = [col[1] for col in columns_info if col[1] != "id"]

    if operation == "Crear":
        with st.form("crear_poliza"):
            field_values = {}
            for field in poliza_fields:
                if field == "numero_poliza":
                    next_numero = get_next_numero_poliza()
                    field_values[field] = st.text_input("Número de Póliza", value=next_numero, disabled=True)
                elif field == "cliente_id":
                    client_options = get_client_options()
                    if client_options:
                        selected_client = st.selectbox("Cliente", client_options, format_func=lambda x: x[1])
                        field_values[field] = selected_client[0]
                    else:
                        st.warning("No hay clientes registrados.")
                        field_values[field] = ""
                elif field == "usuario_id":
                    user_options = get_user_options()
                    if user_options:
                        selected_user = st.selectbox("Usuario", user_options, format_func=lambda x: x[1])
                        field_values[field] = selected_user[0]
                    else:
                        st.warning("No hay usuarios registrados.")
                        field_values[field] = ""
                elif field == "tipo_poliza":
                    field_values[field] = st.selectbox("Tipo de Póliza", ["Nueva", "Renovación"])
                elif field in ["fecha_inicio", "fecha_fin"]:
                    field_values[field] = st.date_input(field.replace("_", " ").capitalize())
                elif field == "estado":
                    field_values[field] = st.selectbox("Estado", ["Activa", "Vencida", "Cancelada"])
                else:
                    field_values[field] = st.text_input(field.replace("_", " ").capitalize())
            submit = st.form_submit_button("Crear Póliza")
            if submit:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                try:
                    for f in ["fecha_inicio", "fecha_fin"]:
                        if f in field_values and hasattr(field_values[f], "strftime"):
                            field_values[f] = field_values[f].strftime("%Y-%m-%d")
                    field_values["numero_poliza"] = get_next_numero_poliza()
                    values = [field_values[f] for f in poliza_fields]
                    placeholders = ', '.join(['?'] * len(poliza_fields))
                    cursor.execute(
                        f"INSERT INTO polizas ({', '.join(poliza_fields)}) VALUES ({placeholders})",
                        values
                    )
                    conn.commit()
                    st.success(f"Póliza creada exitosamente con número {field_values['numero_poliza']}")
                except sqlite3.IntegrityError:
                    st.error("El número de póliza ya existe o los datos son inválidos.")
                finally:
                    conn.close()

    elif operation == "Leer":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM polizas")
        columns = [col[0] for col in cursor.description]
        polizas = [dict(zip(columns, row)) for row in cursor.fetchall()]
        conn.close()
        if polizas:
            import pandas as pd
            df = pd.DataFrame(polizas)
            st.dataframe(df)
        else:
            st.info("No hay pólizas registradas.")

    elif operation == "Modificar":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, numero_poliza FROM polizas")
        polizas = cursor.fetchall()
        conn.close()
        if not polizas:
            st.info("No hay pólizas registradas.")
            return
        selected_poliza = st.selectbox("Selecciona una póliza", polizas, format_func=lambda x: x[1])
        if selected_poliza:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM polizas WHERE id=?", (selected_poliza[0],))
            poliza_actual = cursor.fetchone()
            columns = [col[0] for col in cursor.description]
            conn.close()
            poliza_dict = dict(zip(columns, poliza_actual))
            with st.form("modificar_poliza"):
                updated_values = {}
                for field in poliza_fields:
                    if field == "numero_poliza":
                        updated_values[field] = st.text_input("Número de Póliza", value=poliza_dict.get(field, ""), disabled=True)
                    elif field == "cliente_id":
                        client_options = get_client_options()
                        current_client = next((c for c in client_options if c[0] == poliza_dict.get(field)), None)
                        updated = st.selectbox("Cliente", client_options, index=client_options.index(current_client) if current_client else 0, format_func=lambda x: x[1])
                        updated_values[field] = updated[0]
                    elif field == "usuario_id":
                        user_options = get_user_options()
                        current_user = next((u for u in user_options if u[0] == poliza_dict.get(field)), None)
                        updated = st.selectbox("Usuario", user_options, index=user_options.index(current_user) if current_user else 0, format_func=lambda x: x[1])
                        updated_values[field] = updated[0]
                    elif field == "tipo_poliza":
                        updated_values[field] = st.selectbox("Tipo de Póliza", ["Nueva", "Renovación"], index=["Nueva", "Renovación"].index(poliza_dict.get(field, "Nueva")) if poliza_dict.get(field) in ["Nueva", "Renovación"] else 0)
                    elif field in ["fecha_inicio", "fecha_fin"]:
                        import datetime
                        val = poliza_dict.get(field)
                        try:
                            val = datetime.datetime.strptime(val, "%Y-%m-%d").date() if val else None
                        except Exception:
                            val = None
                        updated_values[field] = st.date_input(field.replace("_", " ").capitalize(), value=val)
                    elif field == "estado":
                        updated_values[field] = st.selectbox("Estado", ["Activa", "Vencida", "Cancelada"], index=["Activa", "Vencida", "Cancelada"].index(poliza_dict.get(field, "Activa")) if poliza_dict.get(field) in ["Activa", "Vencida", "Cancelada"] else 0)
                    else:
                        updated_values[field] = st.text_input(field.replace("_", " ").capitalize(), value=str(poliza_dict.get(field, "")))
                submit = st.form_submit_button("Actualizar Póliza")
                if submit:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        for f in ["fecha_inicio", "fecha_fin"]:
                            if f in updated_values and hasattr(updated_values[f], "strftime"):
                                updated_values[f] = updated_values[f].strftime("%Y-%m-%d")
                        set_clause = ', '.join([f"{f}=?" for f in poliza_fields])
                        values = [updated_values[f] for f in poliza_fields] + [selected_poliza[0]]
                        cursor.execute(
                            f"UPDATE polizas SET {set_clause} WHERE id=?",
                            values
                        )
                        conn.commit()
                        st.success("Póliza actualizada exitosamente")
                    except sqlite3.IntegrityError:
                        st.error("No se pudo actualizar la póliza.")
                    finally:
                        conn.close()

    elif operation == "Borrar":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, numero_poliza FROM polizas")
        polizas = cursor.fetchall()
        conn.close()
        if not polizas:
            st.info("No hay pólizas registradas.")
            return
        selected_poliza = st.selectbox("Selecciona una póliza para eliminar", polizas, format_func=lambda x: x[1])
        if st.button("Eliminar Póliza"):
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM polizas WHERE id = ?", (selected_poliza[0],))
                conn.commit()
                st.success("Póliza eliminada exitosamente")
            except sqlite3.IntegrityError:
                st.error("No se puede eliminar la póliza.")
            finally:
                conn.close()
