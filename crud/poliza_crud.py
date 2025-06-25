import streamlit as st
import sqlite3
from dbconfig import DB_FILE, initialize_database

initialize_database()

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

def get_aseguradora_options():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, razon_social FROM aseguradoras")
    aseguradoras = cursor.fetchall()
    conn.close()
    return [(a[0], a[1]) for a in aseguradoras]

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

def get_client_details(client_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tipo_cliente, nombres, apellidos, razon_social, tipo_documento, numero_documento, 
               correo_electronico, telefono_movil, telefono_fijo, direccion_domicilio
        FROM clients WHERE id=?
    """, (client_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "tipo_cliente": row[0],
        "nombres": row[1],
        "apellidos": row[2],
        "razon_social": row[3],
        "tipo_documento": row[4],
        "numero_documento": row[5],
        "correo_electronico": row[6],
        "telefono_movil": row[7],
        "telefono_fijo": row[8],
        "direccion_domicilio": row[9]
    }

def get_ramos_options():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM ramos_seguros")
    ramos = cursor.fetchall()
    conn.close()
    return [(r[0], r[1]) for r in ramos]

def crud_polizas():
    st.subheader("Gestión de Pólizas")
    operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

    # Reiniciar el proceso y los datos de la póliza cada vez que se cambia de operación
    if "last_poliza_operation" not in st.session_state or st.session_state["last_poliza_operation"] != operation:
        st.session_state["poliza_form_step"] = 1
        st.session_state["poliza_form_data"] = {}
        st.session_state["ramos_list"] = []
        st.session_state["last_poliza_operation"] = operation

    # Obtener columnas de la tabla polizas para usarlas en el formulario de creación
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(polizas)")
    columns_info = cursor.fetchall()
    conn.close()
    poliza_fields = [col[1] for col in columns_info if col[1] != "id"]

    if operation == "Crear":
        if "poliza_form_step" not in st.session_state:
            st.session_state["poliza_form_step"] = 1
            st.session_state["poliza_form_data"] = {}

        if st.session_state["poliza_form_step"] == 1:
            with st.form("form_poliza_crear"):
                # Nº Póliza
                numero_poliza = st.text_input("Número de Póliza (mínimo 10 caracteres)")
                col1, col2, col3 = st.columns(3)
                with col1:
                # Cliente
                    client_options = get_client_options()
                    selected_client = st.selectbox("Cliente", client_options, format_func=lambda x: x[1] if x else "") if client_options else None
                # Aseguradora
                with col2:
                    aseguradora_options = get_aseguradora_options()
                    selected_aseguradora = st.selectbox("Aseguradora", aseguradora_options, format_func=lambda x: x[1] if x else "") if aseguradora_options else None
                # Usuario (nuevo campo obligatorio)
                with col3:
                    user_options = get_user_options()
                    selected_user = st.selectbox("Usuario responsable", user_options, format_func=lambda x: x[1] if x else "") if user_options else None
                col1, col2, col3 = st.columns(3)
                with col1:
                    # Fecha de Emisión
                    fecha_emision = st.date_input("Fecha de Emisión")
                with col2:
                    # Fecha de Inicio Vigencia
                    fecha_inicio = st.date_input("Fecha de Inicio Vigencia")
                with col3:
                    # Fecha de Fin de Vigencia
                    fecha_fin = st.date_input("Fecha de Fin de Vigencia")
                col1,col2 = st.columns(2)
                # Estado póliza
                with col1:
                    estado_choices = ["Borrador", "Emitida", "Anulada", "Activa", "Pagada", "Pendiente de Pago"]
                    estado = st.selectbox("Estado póliza", estado_choices)
                with col2:
                # Tipo de póliza (nuevo campo obligatorio)
                    tipo_poliza = st.selectbox("Tipo de Póliza", ["Nueva", "Renovación"])
                col1,col2 = st.columns(2)
                # Cobertura
                with col1:
                    cobertura = st.text_input("Cobertura de la póliza")  # Nuevo campo obligatorio
                # Prima (nuevo campo obligatorio)
                with col2:
                    prima = st.text_input("Prima total de la póliza")  # Nuevo campo obligatorio
                # Observaciones
                observaciones = st.text_area("Observaciones")
                seguir = st.form_submit_button("Seguir")

                if seguir:
                    if not numero_poliza or len(numero_poliza) < 10:
                        st.error("El número de póliza debe tener al menos 10 caracteres.")
                    elif not selected_client:
                        st.error("Debe seleccionar un cliente.")
                    elif not selected_aseguradora:
                        st.error("Debe seleccionar una aseguradora.")
                    elif not selected_user:
                        st.error("Debe seleccionar un usuario responsable.")
                    elif not tipo_poliza:
                        st.error("Debe seleccionar un tipo de póliza.")
                    elif not cobertura:
                        st.error("Debe ingresar la cobertura de la póliza.")
                    elif not prima:
                        st.error("Debe ingresar la prima total de la póliza.")
                    else:
                        st.session_state["poliza_form_data"] = {
                            "numero_poliza": numero_poliza,
                            "cliente_id": selected_client[0],
                            "aseguradora_id": selected_aseguradora[0],
                            "usuario_id": selected_user[0],
                            "tipo_poliza": tipo_poliza,
                            "cobertura": cobertura,
                            "prima": prima,
                            "fecha_emision": fecha_emision.strftime("%Y-%m-%d"),
                            "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
                            "fecha_fin": fecha_fin.strftime("%Y-%m-%d"),
                            "estado": estado,
                            "observaciones": observaciones
                        }
                        st.session_state["poliza_form_step"] = 2

        if st.session_state["poliza_form_step"] == 2:
            data = st.session_state.get("poliza_form_data", {})
            client_id = data.get("cliente_id")
            client = get_client_details(client_id) if client_id else None
            continuar = False
            with st.expander("Datos del Cliente Seleccionado", expanded=True):
                if client:
                    if client["tipo_cliente"] == "Empresa":
                        nombre = client["razon_social"]
                    else:
                        nombre = f"{client['nombres']} {client['apellidos']}"
                    st.markdown(f"**Identificación cliente:** {client['numero_documento']}")
                    st.markdown(f"**Nombre/Razón Social:** {nombre}")
                    st.markdown(f"**Tipo de cliente:** {client['tipo_cliente']}")
                    st.markdown(f"**Correo electrónico:** {client['correo_electronico']}")
                    st.markdown(f"**Teléfono 1:** {client['telefono_movil']}")
                    st.markdown(f"**Teléfono 2:** {client['telefono_fijo']}")
                    st.markdown(f"**Dirección:** {client['direccion_domicilio']}")
                else:
                    st.warning("No se pudo obtener los datos del cliente seleccionado.")
                if st.button("Continuar proceso"):
                    st.session_state["poliza_form_step"] = 3

        if st.session_state["poliza_form_step"] == 3:
            st.markdown("### Relación Asegurado/Contratante")
            asegurado_opcion = st.radio(
                "¿Quién es el asegurado?",
                ("El asegurado es el cliente", "El asegurado es otra persona o empresa")
            )
            if asegurado_opcion == "El asegurado es el cliente":
                st.success("El asegurado será el propio cliente seleccionado.")
                st.session_state["poliza_form_data"]["asegurado_id"] = st.session_state["poliza_form_data"]["cliente_id"]
                if st.button("Continuar proceso", key="continuar_ramos_cliente"):
                    st.session_state["poliza_form_step"] = 4
            else:
                with st.form("form_asegurado_otro"):
                    nombre_asegurado = st.text_input("Nombre del Asegurado")
                    id_asegurado = st.text_input("Identificación del Asegurado")
                    crear_asegurado = st.form_submit_button("Crear Asegurado y Continuar")
                    if crear_asegurado:
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO clients (nombres, numero_documento, tipo_cliente) VALUES (?, ?, ?)",
                            (nombre_asegurado, id_asegurado, "Individual")
                        )
                        asegurado_id = cursor.lastrowid
                        conn.commit()
                        conn.close()
                        st.session_state["poliza_form_data"]["asegurado_id"] = asegurado_id
                        st.success("Asegurado creado y seleccionado para la póliza.")
                        st.session_state["poliza_form_step"] = 4

        if st.session_state["poliza_form_step"] == 4:
            st.markdown("### Ramos Asegurados")
            data = st.session_state.get("poliza_form_data", {})
            numero_poliza = data.get("numero_poliza", "")
            if "ramos_list" not in st.session_state:
                st.session_state["ramos_list"] = []
            ramos_list = st.session_state["ramos_list"]

            st.info(f"Número de Póliza: {numero_poliza}")

            nro_ramo = len(ramos_list) + 1

            with st.form("form_ramo_asegurado"):
                st.text_input("Número de Póliza", value=numero_poliza, disabled=True)
                st.text_input("Nº de Ramo", value=str(nro_ramo), disabled=True)
                ramos_options = get_ramos_options()
                ramo_selected = st.selectbox("Tipo de Ramo", ramos_options, format_func=lambda x: x[1] if x else "")
                suma_asegurada = st.text_input("Suma Asegurada")
                prima = st.text_input("Prima")
                observaciones_ramo = st.text_area("Observaciones")
                agregar_ramo = st.form_submit_button("Agregar Ramo a la Póliza")

                if agregar_ramo:
                    ramo_data = {
                        "nro_ramo": nro_ramo,
                        "ramo_id": ramo_selected[0],
                        "ramo_nombre": ramo_selected[1],
                        "suma_asegurada": suma_asegurada,
                        "prima": prima,
                        "observaciones": observaciones_ramo
                    }
                    st.session_state["ramos_list"].append(ramo_data)
                    st.success(f"Ramo {ramo_selected[1]} agregado a la póliza.")

            # Mostrar lista de ramos agregados
            if st.session_state["ramos_list"]:
                st.markdown("#### Ramos agregados a la póliza:")
                for ramo in st.session_state["ramos_list"]:
                    st.markdown(
                        f"- **Nº Ramo:** {ramo['nro_ramo']} | **Tipo:** {ramo['ramo_nombre']} | "
                        f"**Suma Asegurada:** {ramo['suma_asegurada']} | **Prima:** {ramo['prima']} | "
                        f"**Obs.:** {ramo['observaciones']}"
                    )

            # Botón para crear la póliza borrador
            if st.button("Crear póliza borrador"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                try:
                    poliza_data = st.session_state["poliza_form_data"]
                    cobertura = poliza_data.get("cobertura", "")
                    prima = poliza_data.get("prima", "")
                    cursor.execute("""
                        INSERT INTO polizas (
                            numero_poliza, cliente_id, aseguradora_id, usuario_id, tipo_poliza, cobertura, prima, fecha_emision,
                            fecha_inicio, fecha_fin, estado
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        poliza_data["numero_poliza"],
                        poliza_data["cliente_id"],
                        poliza_data["aseguradora_id"],
                        poliza_data["usuario_id"],
                        poliza_data["tipo_poliza"],
                        cobertura,
                        prima,
                        poliza_data["fecha_emision"],
                        poliza_data["fecha_inicio"],
                        poliza_data["fecha_fin"],
                        "Borrador"
                    ))
                    poliza_id = cursor.lastrowid

                    # Insertar los ramos asociados (si tienes tabla poliza_ramos, ajusta aquí)
                    for ramo in st.session_state["ramos_list"]:
                        cursor.execute("""
                            INSERT INTO poliza_ramos (poliza_id, nro_ramo, ramo_id, suma_asegurada, prima, observaciones)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (
                            poliza_id,
                            ramo["nro_ramo"],
                            ramo["ramo_id"],
                            ramo["suma_asegurada"],
                            ramo["prima"],
                            ramo["observaciones"]
                        ))
                    conn.commit()
                    st.success(f"Póliza borrador creada exitosamente con número {poliza_data['numero_poliza']}")
                    st.session_state["poliza_form_step"] = 1
                    st.session_state["poliza_form_data"] = {}
                    st.session_state["ramos_list"] = []
                except Exception as e:
                    st.error(f"Error al crear la póliza: {e}")
                finally:
                    conn.close()

    elif operation == "Leer":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        campos = [
            "id", "numero_poliza", "cliente_id", "aseguradora_id", "usuario_id", "tipo_poliza",
            "cobertura", "prima", "fecha_emision", "fecha_inicio", "fecha_fin", "estado", "observaciones"
        ]
        cursor.execute(f"SELECT {', '.join(campos)} FROM polizas")
        polizas = cursor.fetchall()
        conn.close()
        if polizas:
            import pandas as pd
            # Cargar datos de referencia para clientes, aseguradoras y usuarios
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            # Clientes
            cursor.execute("SELECT id, tipo_cliente, nombres, apellidos, razon_social FROM clients")
            clientes_dict = {row[0]: (row[4] if row[1] == "Empresa" else f"{row[2]} {row[3]}") for row in cursor.fetchall()}
            # Aseguradoras
            cursor.execute("SELECT id, razon_social FROM aseguradoras")
            aseguradoras_dict = {row[0]: row[1] for row in cursor.fetchall()}
            # Usuarios
            cursor.execute("SELECT id, username FROM users")
            usuarios_dict = {row[0]: row[1] for row in cursor.fetchall()}
            # Beneficiarios (asegurado_id)
            cursor.execute("PRAGMA table_info(polizas)")
            polizas_columns = [row[1] for row in cursor.fetchall()]
            tiene_asegurado = "asegurado_id" in polizas_columns
            asegurados_dict = {}
            if tiene_asegurado:
                cursor.execute("SELECT id, tipo_cliente, nombres, apellidos, razon_social FROM clients")
                asegurados_dict = {row[0]: (row[4] if row[1] == "Empresa" else f"{row[2]} {row[3]}") for row in cursor.fetchall()}
            conn.close()

            # Preparar los datos para mostrar
            data = []
            for row in polizas:
                poliza = dict(zip(campos, row))
                cliente = clientes_dict.get(poliza["cliente_id"], "")
                aseguradora = aseguradoras_dict.get(poliza.get("aseguradora_id"), "")
                usuario = usuarios_dict.get(poliza["usuario_id"], "")
                beneficiario = ""
                if tiene_asegurado:
                    asegurado_id = poliza.get("asegurado_id")
                    if asegurado_id and asegurado_id != poliza["cliente_id"]:
                        beneficiario = asegurados_dict.get(asegurado_id, "")
                data.append({
                    "Número de Póliza": poliza["numero_poliza"],
                    "Cliente": cliente,
                    "Aseguradora": aseguradora,
                    "Usuario": usuario,
                    "Tipo de Póliza": poliza["tipo_poliza"],
                    "Cobertura": poliza["cobertura"],
                    "Prima": poliza["prima"],
                    "Fecha Emisión": poliza.get("fecha_emision", ""),
                    "Fecha Inicio": poliza["fecha_inicio"],
                    "Fecha Fin": poliza["fecha_fin"],
                    "Estado": poliza["estado"],
                    "Observaciones": poliza.get("observaciones", ""),
                    "Beneficiario": beneficiario
                })
            df = pd.DataFrame(data)
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