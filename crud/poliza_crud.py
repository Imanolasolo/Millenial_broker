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

def get_sucursales_by_aseguradora_id(aseguradora_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Asegurarse de que la tabla sucursales existe antes de consultar
    cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='sucursales'
    """)
    if not cursor.fetchone():
        conn.close()
        return []
    cursor.execute("SELECT id, nombre FROM sucursales WHERE aseguradora_id=?", (aseguradora_id,))
    sucursales = cursor.fetchall()
    conn.close()
    return sucursales

def get_agrupadora_options():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM companies")
    agrupadoras = cursor.fetchall()
    conn.close()
    return [(a[0], a[1]) for a in agrupadoras]

def get_ejecutivo_comercial_options():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombres, apellidos FROM users WHERE role = 'Ejecutivo Comercial'")
    ejecutivos = cursor.fetchall()
    conn.close()
    # Mostrar nombre y apellido juntos
    return [(e[0], f"{e[1]} {e[2]}") for e in ejecutivos]

def crud_polizas():
    st.subheader("Gestión de Pólizas")
    col1, col2, col3 = st.columns(3)
    with col1:
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
    # --- Añadir columna beneficiario si no existe ---
    poliza_columns = [col[1] for col in columns_info]
    if "beneficiario" not in poliza_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN beneficiario TEXT")
    # --- Añadir columna tipo_renovacion si no existe ---
    if "tipo_renovacion" not in poliza_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN tipo_renovacion TEXT")
    # --- Añadir columna tipo_movimiento si no existe ---
    if "tipo_movimiento" not in poliza_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN tipo_movimiento TEXT")
    # --- Añadir columna sucursal_id si no existe ---
    if "sucursal_id" not in poliza_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN sucursal_id INTEGER")
    conn.commit()
    conn.close()
    poliza_fields = [col[1] for col in columns_info if col[1] != "id"]

    # --- NUEVO: Añadir campos de facturación si no existen ---
    fact_fields = [
        ("numero_factura", "TEXT"),
        ("moneda", "TEXT"),
        ("clausulas_particulares", "TEXT"),
        ("contrib_scvs", "TEXT"),
        ("derechos_emision", "TEXT"),
        ("ssoc_camp", "TEXT"),
        ("subtotal", "TEXT"),
        ("iva_15", "TEXT"),
        ("csolidaria_2", "TEXT"),
        ("financiacion", "TEXT"),
        ("otros_iva", "TEXT"),
        ("total", "TEXT"),
        ("cuotas", "TEXT"),
    ]
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(polizas)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    for col, coltype in fact_fields:
        if col not in existing_cols:
            cursor.execute(f"ALTER TABLE polizas ADD COLUMN {col} {coltype}")
    conn.commit()
    conn.close()

    if operation == "Crear":
        # FORMULARIO 1: Datos de información general
        with st.expander("Datos generales de la póliza"):
            aseguradora_options = get_aseguradora_options()
            aseguradora_labels = [a[1] for a in aseguradora_options]
            col1, col2 = st.columns(2)
            with col1:
                selected_aseguradora_label = st.selectbox(
                    "Aseguradora",
                    aseguradora_labels,
                    key="aseguradora_label"
                )
                selected_aseguradora = next((a for a in aseguradora_options if a[1] == selected_aseguradora_label), None)

            # Resetear la sucursal seleccionada si cambia la aseguradora
            if "last_aseguradora_label" not in st.session_state:
                st.session_state["last_aseguradora_label"] = selected_aseguradora_label
            if st.session_state["last_aseguradora_label"] != selected_aseguradora_label:
                if "sucursal_label" in st.session_state:
                    del st.session_state["sucursal_label"]
                st.session_state["last_aseguradora_label"] = selected_aseguradora_label

            selected_sucursal = None
            if selected_aseguradora:
                sucursal_options = get_sucursales_by_aseguradora_id(selected_aseguradora[0])
                if sucursal_options:
                    sucursal_labels = [s[1] for s in sucursal_options]
                    if "sucursal_label" in st.session_state and st.session_state["sucursal_label"] in sucursal_labels:
                        default_idx = sucursal_labels.index(st.session_state["sucursal_label"])
                    else:
                        default_idx = 0
                    with col2:
                        selected_sucursal_label = st.selectbox(
                            "Sucursal",
                            sucursal_labels,
                            index=default_idx,
                            key="sucursal_label"
                        )
                    # selected_sucursal es una tupla (id, nombre)
                    selected_sucursal = next((s for s in sucursal_options if s[1] == selected_sucursal_label), None)
                else:
                    st.info("No hay sucursales registradas para esta aseguradora.")

            col1, col2 = st.columns(2)
            with col1:
                numero_poliza = st.text_input("Número de Póliza (mínimo 10 caracteres)")
            with col2:
                fecha_emision = st.date_input("Fecha de Emisión")

            col1, col2 = st.columns(2)
            # Inicializar client_options antes de usarlo
            client_options = get_client_options()
            with col1:
                selected_tomador = st.selectbox(
                    "Tomador de la póliza",
                    client_options,
                    format_func=lambda x: x[1] if x else ""
                ) if client_options else None
            with col2:
                beneficiario_text = st.text_input("Beneficiario")

            col1, col2, col3 = st.columns(3)
            with col1:
                fecha_inicio = st.date_input("Inicio de vigencia")
            with col2:
                fecha_fin = st.date_input("Fin de vigencia")
            with col3:
                dias_cobertura = ""
                if fecha_inicio and fecha_fin:
                    try:
                        dias_cobertura = (fecha_fin - fecha_inicio).days
                    except Exception:
                        dias_cobertura = ""
                st.text_input("Días de Cobertura", value=str(dias_cobertura) if dias_cobertura != "" else "", disabled=True)
            col1, col2 = st.columns(2)
            with col1:
                tipo_riesgo = st.selectbox("Tipo de Riesgo", ["Nueva", "Renovación"])
            with col2:
                agrupadora_options = get_agrupadora_options()
                selected_agrupadora = st.selectbox(
                    "Agrupadora",
                    agrupadora_options,
                    format_func=lambda x: x[1] if x else "",
                    key="agrupadora"
                ) if agrupadora_options else None
            col1, col2 = st.columns(2)
            with col1:
                formas_de_pago = st.selectbox("Formas de pago", ["Contado", "Cuotas", "Crédito"])
            with col2:
                tipo_de_facturacion = st.selectbox("Tipo de Facturación", ["Anual", "Semestral","Trimestral","Mensual"])
            # Mover el campo cuotas aquí desde el formulario siguiente
            # cuotas = st.text_input("Cuotas")
            siguiente = st.button("Siguiente")

            if siguiente:
                # Ya no es necesario volver a pedir selected_tomador ni validarlo aquí
                if not selected_aseguradora:
                    st.error("Debe seleccionar una aseguradora.")
                elif not selected_sucursal:
                    st.error("Debe seleccionar una sucursal.")
                elif not numero_poliza or len(numero_poliza) < 10:
                    st.error("El número de póliza debe tener al menos 10 caracteres.")
                elif not beneficiario_text:
                    st.error("Debe ingresar el beneficiario.")
                elif not fecha_inicio or not fecha_fin:
                    st.error("Debe ingresar la vigencia de la póliza.")
                else:
                    # Guardar también el nombre del tomador seleccionado para mostrarlo fácilmente al leer
                    tomador_id = selected_tomador[0] if isinstance(selected_tomador, tuple) else selected_tomador
                    tomador_nombre = selected_tomador[1] if isinstance(selected_tomador, tuple) and len(selected_tomador) > 1 else ""
                    st.session_state["poliza_form_data"] = {
                        "aseguradora_id": selected_aseguradora[0],
                        "sucursal_id": selected_sucursal[0] if selected_sucursal else None,
                        "numero_poliza": numero_poliza,
                        "fecha_emision": fecha_emision.strftime("%Y-%m-%d"),
                        "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d"),
                        "fecha_fin": fecha_fin.strftime("%Y-%m-%d"),
                        "beneficiario": beneficiario_text,
                        "tomador_id": tomador_id,
                        "tomador_nombre": tomador_nombre,  # <-- Aquí se guarda el nombre del tomador
                        "tipo_riesgo": tipo_riesgo,
                        "formas_de_pago": formas_de_pago,
                        "tipo_de_facturacion": tipo_de_facturacion,
                        # "cuotas": cuotas,
                        # ...existing code...
                    }
                    st.session_state["poliza_form_step"] = 2

        # FORMULARIO 2: Datos para facturación (solo si se ha pulsado "Siguiente" y paso 2)
        if st.session_state.get("poliza_form_step") == 2:
            with st.container():
                
                st.markdown("### Información Adicional")
                col1, col2 = st.columns(2)
                with col1:
                    tipo_renovacion = st.selectbox("Tipo Renovación", ["MANUAL", "AUTOMATICO"])
                with col2:
                    tipo_movimiento = st.selectbox("Tipo de Movimiento", ["ALTA", "BAJA", "MODIFICACION"])
                col1, col2 = st.columns(2)
                with col1:
                    ejecutivo_options = get_ejecutivo_comercial_options()
                    selected_ejecutivo = st.selectbox(
                        "Gestión de Cobro (Ejecutivo Comercial)",
                        ejecutivo_options,
                        format_func=lambda x: x[1] if x else "",
                        key="ejecutivo_comercial"
                    ) if ejecutivo_options else None
                with col2:
                    liberacion_comision = st.selectbox("Liberación Comisión", ["NO", "SI"])
                client_options = get_client_options()
                col1, col2 = st.columns(2)
                with col1:
                    cuotas = st.text_input("Cuotas", key="cuotas_form2")
                with col2:
                    anexos = []
                    num_anexos = st.number_input("Cantidad de Anexos", min_value=0, max_value=10, value=0, step=1)
                    for i in range(num_anexos):
                        anexo = st.text_input(f"Anexo {i+1}", key=f"anexo_{i+1}")
                        anexos.append(anexo)
                # Tipo de Factura después de anexos
                tipo_factura = st.selectbox("Tipo de Factura", ["Física", "Electrónica", "Otro"])
                
                # --- Inputs para prima, suma asegurada y observaciones ---
                col1, col2 = st.columns(2)
                with col1:
                    prima = st.text_input("Prima del Seguro")
                with col2:
                    suma_asegurada = st.text_input("Suma Asegurada")
                # Eliminar deducible y cobertura
                observaciones_poliza = st.text_area("Observaciones de la póliza")

                st.markdown("### Información Factura")
                col1, col2 = st.columns(2)
                with col1:
                    numero_factura = st.text_input("Nº Factura")
                with col2:
                    moneda = st.selectbox("Moneda", ["USD", "EUR", "Otra"])
                clausulas_particulares = st.text_area("Cláusulas particulares")
                col1, col2 ,col3 = st.columns(3)
                with col1:
                    contrib_scvs = st.text_input("Contrib. S.C.V.S.")
                with col2:
                    derechos_emision = st.text_input("Derechos Emisión")
                with col3:
                    ssoc_camp = st.text_input("S.Soc.Camp.")
                subtotal = st.text_input("Subtotal")
                col1,col2,col3,col4 = st.columns(4)
                with col1:
                    iva_15 = st.text_input("IVA (15%)")
                with col2:
                    csolidaria_2 = st.text_input("C.Solidaria(2%)")
                with col3:
                    financiacion = st.text_input("Financiación")
                with col4:
                    otros_iva = st.text_input("Otros IVA")
                total = st.text_input("Total")
                       
                guardar_fact = st.button("Guardar datos de facturación")

                if guardar_fact:
                    # Guardar los anexos en una variable separada para manipulación antes de guardar en la base de datos
                    anexos_poliza = [a for a in anexos if a and str(a).strip()]
                    st.session_state["facturacion_data"] = {
                        "tipo_renovacion": tipo_renovacion,
                        "tipo_movimiento": tipo_movimiento,
                        "gestion_cobro": selected_ejecutivo[0] if selected_ejecutivo else None,
                        "liberacion_comision": liberacion_comision,
                        "prima": prima,
                        "suma_asegurada": suma_asegurada,
                        # "deducible": deducible,  # Eliminado
                        # "cobertura": cobertura,  # Eliminado
                        "observaciones_poliza": observaciones_poliza,
                        "numero_factura": numero_factura,
                        "moneda": moneda,
                        "clausulas_particulares": clausulas_particulares,
                        "contrib_scvs": contrib_scvs,
                        "derechos_emision": derechos_emision,
                        "ssoc_camp": ssoc_camp,
                        "subtotal": subtotal,
                        "iva_15": iva_15,
                        "csolidaria_2": csolidaria_2,
                        "financiacion": financiacion,
                        "otros_iva": otros_iva,
                        "total": total,
                        "cuotas": cuotas,
                        # Guardar anexos como string serializado para la base de datos
                        "anexos_poliza": str(anexos_poliza),  # Guardar en la columna anexos_poliza
                        "tipo_factura": tipo_factura,
                        "agrupadora": selected_agrupadora[0] if selected_agrupadora else None,
                    }
                    # --- CREAR POLIZA EN LA BASE DE DATOS ---
                    poliza_data = st.session_state.get("poliza_form_data", {})
                    facturacion_data = st.session_state.get("facturacion_data", {})
                    if poliza_data:
                        # Validar que el número de póliza no exista antes de insertar
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute("SELECT COUNT(*) FROM polizas WHERE numero_poliza = ?", (poliza_data.get("numero_poliza", ""),))
                        exists = cursor.fetchone()[0]
                        if exists:
                            st.error("Ya existe una póliza con ese número. Por favor, ingrese un número de póliza único.")
                            conn.close()
                        else:
                            insert_data = {**poliza_data, **facturacion_data}
                            cursor.execute("PRAGMA table_info(polizas)")
                            poliza_cols = [row[1] for row in cursor.fetchall() if row[1] != "id"]
                            insert_fields = []
                            insert_values = []
                            for col in poliza_cols:
                                insert_fields.append(col)
                                insert_values.append(insert_data.get(col, ""))
                            try:
                                cursor.execute(
                                    f"INSERT INTO polizas ({', '.join(insert_fields)}) VALUES ({', '.join(['?']*len(insert_fields))})",
                                    insert_values
                                )
                                conn.commit()
                                st.success("Póliza creada exitosamente.")
                                st.session_state["poliza_form_step"] = 1
                                st.session_state["poliza_form_data"] = {}
                                st.session_state["facturacion_data"] = {}
                            except Exception as e:
                                st.error(f"Error al crear la póliza: {e}")
                            finally:
                                conn.close()
    elif operation == "Leer":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Obtener todos los campos de la tabla polizas
        cursor.execute("PRAGMA table_info(polizas)")
        all_fields = [row[1] for row in cursor.fetchall()]
        cursor.execute(f"SELECT {', '.join(all_fields)} FROM polizas")
        polizas = cursor.fetchall()
        # Obtener nombres legibles para aseguradora, sucursal y agrupadora
        cursor.execute("SELECT id, razon_social FROM aseguradoras")
        aseguradoras_dict = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute("SELECT id, nombre FROM sucursales")
        sucursales_dict = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute("SELECT id, name FROM companies")
        agrupadoras_dict = {row[0]: row[1] for row in cursor.fetchall()}
        # Obtener clientes para mostrar nombre/razón social del tomador
        cursor.execute("SELECT id, tipo_cliente, nombres, apellidos, razon_social FROM clients")
        clientes_dict = {row[0]: (row[4] if row[1] == "Empresa" else f"{row[2]} {row[3]}") for row in cursor.fetchall()}
        conn.close()

        import json

        if polizas:
            st.markdown("### Pólizas (JSON)")
            for idx, row in enumerate(polizas):
                poliza_dict = dict(zip(all_fields, row))
                result = {}
                result["numero_poliza"] = poliza_dict.get("numero_poliza", "")
                # Mostrar SIEMPRE el nombre del tomador: primero intenta campo 'tomador_nombre', si no, busca por id
                tomador_nombre = poliza_dict.get("tomador_nombre")
                if not tomador_nombre or str(tomador_nombre).lower() == "none":
                    tomador_id = poliza_dict.get("tomador_id")
                    try:
                        if tomador_id is not None and not isinstance(tomador_id, int):
                            tomador_id = int(tomador_id)
                    except Exception:
                        tomador_id = None
                    if tomador_id in clientes_dict:
                        tomador_nombre = clientes_dict[tomador_id]
                if (not tomador_nombre or str(tomador_nombre).lower() == "none") and poliza_dict.get("cliente_id") in clientes_dict:
                    tomador_nombre = clientes_dict[poliza_dict["cliente_id"]]
                result["tomador"] = tomador_nombre if tomador_nombre else "(Sin tomador)"
                # Mostrar la aseguradora
                aseguradora_nombre = ""
                aseguradora_id = poliza_dict.get("aseguradora_id")
                if aseguradora_id in aseguradoras_dict:
                    aseguradora_nombre = aseguradoras_dict[aseguradora_id]
                result["aseguradora"] = aseguradora_nombre if aseguradora_nombre else "(Sin aseguradora)"
                # Mostrar la sucursal
                sucursal_nombre = ""
                sucursal_id = poliza_dict.get("sucursal_id")
                # Buscar el nombre de la sucursal en la tabla sucursales
                if sucursal_id:
                    try:
                        # Si el id no es int, convertirlo
                        if not isinstance(sucursal_id, int):
                            sucursal_id = int(sucursal_id)
                    except Exception:
                        sucursal_id = None
                if sucursal_id and sucursal_id in sucursales_dict:
                    sucursal_nombre = sucursales_dict[sucursal_id]
                result["sucursal"] = sucursal_nombre if sucursal_nombre else "(Sin sucursal)"
                # Mostrar suma asegurada
                suma_asegurada = poliza_dict.get("suma_asegurada", "")
                result["suma_asegurada"] = suma_asegurada if suma_asegurada else "(Sin suma asegurada)"
                # Mostrar prima
                prima = poliza_dict.get("prima", "")
                result["prima"] = prima if prima else "(Sin prima)"
                # Mostrar anexos desde la columna anexos_poliza
                anexos_poliza = poliza_dict.get("anexos_poliza", "")
                anexos_list = []
                if anexos_poliza:
                    try:
                        import ast
                        if isinstance(anexos_poliza, str):
                            anexos_list = ast.literal_eval(anexos_poliza)
                            if isinstance(anexos_list, list):
                                anexos_list = [a for a in anexos_list if a and str(a).strip()]
                        elif isinstance(anexos_poliza, list):
                            anexos_list = [a for a in anexos_poliza if a and str(a).strip()]
                    except Exception:
                        anexos_list = []
                if anexos_list:
                    result["anexos"] = anexos_list
                else:
                    result["anexos"] = "(Sin anexos)"
                # Mostrar tipo de renovación
                tipo_renovacion = poliza_dict.get("tipo_renovacion", "")
                result["tipo_renovacion"] = tipo_renovacion if tipo_renovacion else "(Sin tipo de renovación)"
                # Mostrar tipo de movimiento
                tipo_movimiento = poliza_dict.get("tipo_movimiento", "")
                result["tipo_movimiento"] = tipo_movimiento if tipo_movimiento else "(Sin tipo de movimiento)"
                # Mostrar gestión de cobro (ejecutivo comercial)
                gestion_cobro = poliza_dict.get("gestion_cobro", "")
                # Si tienes una tabla de usuarios y quieres mostrar el nombre:
                gestion_cobro_nombre = ""
                if gestion_cobro:
                    try:
                        # Buscar el nombre del ejecutivo comercial si es un id
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute("SELECT nombres, apellidos FROM users WHERE id=?", (gestion_cobro,))
                        row = cursor.fetchone()
                        conn.close()
                        if row:
                            gestion_cobro_nombre = f"{row[0]} {row[1]}"
                    except Exception:
                        gestion_cobro_nombre = str(gestion_cobro)
                result["gestion_cobro"] = gestion_cobro_nombre if gestion_cobro_nombre else "(Sin gestión de cobro)"
                # Mostrar agrupadora
                agrupadora_nombre = ""
                agrupadora_id = poliza_dict.get("agrupadora")
                if agrupadora_id and agrupadora_id in agrupadoras_dict:
                    agrupadora_nombre = agrupadoras_dict[agrupadora_id]
                result["agrupadora"] = agrupadora_nombre if agrupadora_nombre else "(Sin agrupadora)"
                # Mostrar número de factura
                numero_factura = poliza_dict.get("numero_factura", "")
                result["numero_factura"] = numero_factura if numero_factura else "(Sin número de factura)"
                # Mostrar formas de pago
                formas_de_pago = poliza_dict.get("formas_de_pago", "")
                result["formas_de_pago"] = formas_de_pago if formas_de_pago else "(Sin formas de pago)"
                # Mostrar cuotas
                cuotas = poliza_dict.get("cuotas", "")
                result["cuotas"] = cuotas if cuotas else "(Sin cuotas)"
                # Mostrar subtotal
                subtotal = poliza_dict.get("subtotal", "")
                result["subtotal"] = subtotal if subtotal else "(Sin subtotal)"
                # Mostrar total
                total = poliza_dict.get("total", "")
                result["total"] = total if total else "(Sin total)"
                st.markdown(f"#### Póliza #{idx+1}")
                st.code(json.dumps(result, indent=2, ensure_ascii=False), language="json")
                st.markdown("---")
        else:
            st.info("No hay pólizas registradas.")
    elif operation == "Modificar":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Obtener todos los campos de la tabla polizas
        cursor.execute("PRAGMA table_info(polizas)")
        all_fields = [row[1] for row in cursor.fetchall()]
        cursor.execute(f"SELECT id, numero_poliza FROM polizas")
        polizas = cursor.fetchall()
        if not polizas:
            st.info("No hay pólizas registradas.")
            conn.close()
            return
        selected_poliza = st.selectbox("Selecciona una póliza", polizas, format_func=lambda x: x[1])
        if selected_poliza:
            cursor.execute(f"SELECT {', '.join(all_fields)} FROM polizas WHERE id=?", (selected_poliza[0],))
            poliza_actual = cursor.fetchone()
            conn.close()
            if not poliza_actual:
                st.error("No se encontró la póliza seleccionada.")
                return
            poliza_dict = dict(zip(all_fields, poliza_actual))
            with st.form("modificar_poliza"):
                updated_values = {}
                for field in all_fields:
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
                    elif field == "sucursal_id":
                        aseguradora_id = poliza_dict.get("aseguradora_id")
                        sucursal_options = get_sucursales_by_aseguradora_id(aseguradora_id) if aseguradora_id else []
                        current_sucursal = next((s for s in sucursal_options if s[0] == poliza_dict.get(field)), None)
                        updated = st.selectbox("Sucursal", sucursal_options, index=sucursal_options.index(current_sucursal) if current_sucursal else 0, format_func=lambda x: x[1]) if sucursal_options else None
                        updated_values[field] = updated[0] if updated else None
                    elif field == "agrupadora":
                        agrupadora_options = get_agrupadora_options()
                        current_agrupadora = next((a for a in agrupadora_options if a[0] == poliza_dict.get(field)), None)
                        updated = st.selectbox("Agrupadora", agrupadora_options, index=agrupadora_options.index(current_agrupadora) if current_agrupadora else 0, format_func=lambda x: x[1]) if agrupadora_options else None
                        updated_values[field] = updated[0] if updated else None
                    elif field in ["fecha_inicio", "fecha_fin", "fecha_emision"]:
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
                        for f in ["fecha_inicio", "fecha_fin", "fecha_emision"]:
                            if f in updated_values and hasattr(updated_values[f], "strftime"):
                                updated_values[f] = updated_values[f].strftime("%Y-%m-%d")
                        set_clause = ', '.join([f"{f}=?" for f in all_fields])
                        values = [updated_values[f] for f in all_fields] + [selected_poliza[0]]
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
        if not polizas:
            st.info("No hay pólizas registradas.")
            conn.close()
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