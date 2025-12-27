import streamlit as st
import sqlite3
import datetime
from dbconfig import DB_FILE, initialize_database

initialize_database()

# Lista canonica de estados de póliza usada en crear y modificar
ESTADOS_POLIZA = [
    "Borrador",
    "Emitida",
    "Anulada",
    "Activa",
    "Pagada",
    "Pendiente de Pago",
]

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
        # Mostrar Razón Social si es Persona Jurídica, nombre y apellido si es Persona Natural
        if c[1] == "Persona Jurídica":
            label = f"{c[4]} (Persona Jurídica) [ID: {c[0]}]"
        else:
            label = f"{c[2]} {c[3]} (Persona Natural) [ID: {c[0]}]"
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
    cursor.execute("SELECT id, nombre FROM ramos_seguros ORDER BY nombre")
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
    # --- Campo eliminado: tipo_movimiento ---
    # if "tipo_movimiento" not in poliza_columns:
    #     cursor.execute("ALTER TABLE polizas ADD COLUMN tipo_movimiento TEXT")
    # --- Añadir columna sucursal_id si no existe ---
    if "sucursal_id" not in poliza_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN sucursal_id INTEGER")
    # --- Añadir columna asegurado_contratante si no existe ---
    if "asegurado_contratante" not in poliza_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN asegurado_contratante TEXT")
    # --- Añadir columna id_beneficiario si no existe ---
    if "id_beneficiario" not in poliza_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN id_beneficiario TEXT")
    # --- Añadir columna prima_neta si no existe ---
    if "prima_neta" not in poliza_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN prima_neta TEXT")
    # --- Añadir columna fecha_factura si no existe ---
    if "fecha_factura" not in poliza_columns:
        cursor.execute("ALTER TABLE polizas ADD COLUMN fecha_factura TEXT")
    # --- Campo eliminado: anexos ---
    # if "anexos" not in poliza_columns:
    #     cursor.execute("ALTER TABLE polizas ADD COLUMN anexos TEXT")
    conn.commit()
    conn.close()
    poliza_fields = [col[1] for col in columns_info if col[1] != "id"]

    # --- NUEVO: Añadir campos de facturación si no existen ---
    fact_fields = [
        ("numero_factura", "TEXT"),
        ("moneda", "TEXT"),
        # ("clausulas_particulares", "TEXT"),  # Campo eliminado
        ("contrib_scvs", "TEXT"),
        ("derechos_emision", "TEXT"),
        ("ssoc_camp", "TEXT"),
        ("subtotal", "TEXT"),
        ("iva_15", "TEXT"),
        # ("csolidaria_2", "TEXT"),  # Campo eliminado
        # ("financiacion", "TEXT"),  # Campo eliminado
        # ("otros_iva", "TEXT"),  # Campo eliminado - ya no es necesario
        ("total", "TEXT"),
        ("formas_de_pago", "TEXT"),  # <-- Nuevo campo
        ("cuotas", "TEXT"),
        ("valor_cuota_inicial", "TEXT"),
        ("valor_cuotas_financiadas", "TEXT"),
        ("fecha_factura", "TEXT"),
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
            col1, col2 = st.columns(2)
            with col1:
                # PRIMER CAMPO: Número de Póliza
                numero_poliza = st.text_input("Número de Póliza")

            with col2:
                # SEGUNDO CAMPO: Solicitante
                client_options = get_client_options()
                selected_tomador = st.selectbox(
                "Solicitante",
                client_options,
                format_func=lambda x: x[1] if x else "",
                key="tomador_poliza_selector"
            ) if client_options else None
            
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

            fecha_emision = st.date_input("Fecha de Emisión")

            col1, col2, col3 = st.columns(3)
            with col1:
                fecha_inicio = st.date_input("Inicio de vigencia")
            with col2:
                # Calcular automáticamente la fecha fin como un año después del inicio
                fecha_fin_default = None
                if fecha_inicio:
                    try:
                        from datetime import datetime, timedelta
                        # Agregar un año a la fecha de inicio
                        if fecha_inicio.month == 2 and fecha_inicio.day == 29:
                            # Manejar años bisiestos - si es 29 de febrero, usar 28 de febrero del año siguiente
                            fecha_fin_default = fecha_inicio.replace(year=fecha_inicio.year + 1, day=28)
                        else:
                            try:
                                fecha_fin_default = fecha_inicio.replace(year=fecha_inicio.year + 1)
                            except ValueError:
                                # Fallback para casos edge
                                fecha_fin_default = fecha_inicio + timedelta(days=365)
                    except Exception:
                        fecha_fin_default = None
                
                fecha_fin = st.date_input(
                    "Fin de vigencia", 
                    value=fecha_fin_default,
                    help="Se establece automáticamente un año después del inicio de vigencia. Puede modificarse si es necesario."
                )
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
                estado_poliza = st.selectbox("Estado póliza", ESTADOS_POLIZA)
            with col2:
                agrupadora_options = get_agrupadora_options()
                selected_agrupadora = st.selectbox(
                    "Agrupadora",
                    agrupadora_options,
                    format_func=lambda x: x[1] if x else "",
                    key="agrupadora"
                ) if agrupadora_options else None

            # Campos adicionales: Dirección y Contenido asegurado (usar keys para persistencia)
            col3, col4 = st.columns(2)
            with col3:
                st.text_input(
                    "Dirección",
                    help="Localización donde se maneja la póliza (se almacenará en la columna 'direccion')",
                    key="poliza_direccion"
                )
            with col4:
                st.text_area(
                    "Contenido asegurado",
                    help="Descripción del contenido que se asegurará (se almacenará en la columna 'contenido')",
                    height=80,
                    key="poliza_contenido"
                )

            siguiente = st.button("Siguiente")

            if siguiente:
                if not selected_aseguradora:
                    st.error("Debe seleccionar una aseguradora.")
                elif not numero_poliza or not numero_poliza.strip():
                    st.error("El número de póliza es obligatorio.")
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
                        "tomador_id": tomador_id,
                        "tomador_nombre": tomador_nombre,
                        "estado_poliza": estado_poliza,
                        # Guardar los campos nuevos (leer desde session_state para persistencia)
                        "direccion": st.session_state.get("poliza_direccion", ""),
                        "contenido": st.session_state.get("poliza_contenido", ""),
                    }
                    st.session_state["poliza_form_step"] = 2

        # MOSTRAR INFORMACIÓN DEL CLIENTE (solo si se ha pulsado "Siguiente" y paso 2)
        if st.session_state.get("poliza_form_step") == 2:
            poliza_data = st.session_state.get("poliza_form_data", {})
            tomador_id = poliza_data.get("tomador_id")
            
            if tomador_id:
                client_details = get_client_details(tomador_id)
                if client_details:
                    with st.expander("II. Datos del Cliente (autocompletados, solo lectura)", expanded=True):
                        import pandas as pd
                        
                        # Preparar los datos para el DataFrame
                        if client_details.get("tipo_cliente") == "Individual":
                            nombre_display = f"{client_details.get('nombres', '')} {client_details.get('apellidos', '')}".strip()
                        else:
                            nombre_display = client_details.get("razon_social", "")
                        
                        telefono_display = client_details.get("telefono_movil", "") or client_details.get("telefono_fijo", "")
                        
                        # Crear DataFrame con los datos del cliente
                        client_data = {
                            "Campo": [
                                "Identificación cliente",
                                "Nombre / Razón social", 
                                "Tipo de cliente",
                                "Correo electrónico",
                                "Teléfono",
                                "Dirección"
                            ],
                            "Valor": [
                                client_details.get("numero_documento", ""),
                                nombre_display,
                                client_details.get("tipo_cliente", ""),
                                client_details.get("correo_electronico", ""),
                                telefono_display,
                                client_details.get("direccion_domicilio", "")
                            ],
                            "Observaciones": [
                                "Cédula o RUC",
                                "Natural o Jurídico",
                                "Solo lectura",
                                "Solo lectura",
                                "Solo lectura", 
                                "Solo lectura"
                            ]
                        }
                        
                        df_client = pd.DataFrame(client_data)
                        
                        # Mostrar el DataFrame con formato mejorado
                        st.dataframe(
                            df_client,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Campo": st.column_config.TextColumn("Campo", width="medium"),
                                "Valor": st.column_config.TextColumn("Valor", width="large"),
                                "Observaciones": st.column_config.TextColumn("Observaciones", width="medium")
                            }
                        )

            # NUEVO EXPANDER: Relación Asegurado-Contratante
            with st.expander("III. Relación Asegurado-Contratante", expanded=True):
                asegurado_contratante = st.selectbox(
                    "¿El asegurado es el mismo que el contratante?",
                    ["Sí", "No"],
                    help="Seleccione si el asegurado y el contratante son la misma persona/entidad"
                )
                
                # Campos adicionales cuando el asegurado NO es el mismo que el contratante
                beneficiario_nombre = ""
                id_beneficiario = ""
                
                if asegurado_contratante == "No":
                    st.info("💡 Complete los datos del beneficiario/asegurado por separado:")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        beneficiario_nombre = st.text_input(
                            "Beneficiario",
                            help="Nombre completo del beneficiario/asegurado"
                        )
                    with col2:
                        id_beneficiario = st.text_input(
                            "ID de Beneficiario",
                            help="Cédula, RUC o identificación del beneficiario"
                        )
                else:
                    st.success("✅ El asegurado es el mismo que el contratante (solicitante de la póliza).")

            # NUEVO EXPANDER: Ramos asegurados
            with st.expander("IV. Ramos asegurados", expanded=True):
                # Campo de Número de Póliza
                st.markdown("**📄 Número de Póliza para los Ramos**")
                
                # Obtener el número de póliza actual
                poliza_data = st.session_state.get("poliza_form_data", {})
                numero_poliza_actual = poliza_data.get("numero_poliza", "")
                
                # Obtener pólizas existentes
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT numero_poliza FROM polizas ORDER BY id DESC")
                polizas_existentes = cursor.fetchall()
                conn.close()
                
                # Opciones de selección de póliza
                col1, col2 = st.columns(2)
                with col1:
                    opcion_poliza = st.radio(
                        "Seleccione una opción:",
                        ["Usar póliza actual", "Usar póliza existente"],
                        key="opcion_numero_poliza"
                    )
                
                with col2:
                    if opcion_poliza == "Usar póliza actual":
                        numero_poliza_seleccionado = st.text_input(
                            "Número de Póliza (actual)",
                            value=numero_poliza_actual,
                            disabled=True,
                            help="Este es el número de la póliza que se está creando actualmente"
                        )
                    else:
                        if polizas_existentes:
                            polizas_opciones = [p[0] for p in polizas_existentes if p[0]]
                            numero_poliza_seleccionado = st.selectbox(
                                "Seleccionar póliza existente",
                                polizas_opciones,
                                help="Seleccione una póliza previamente creada"
                            )
                        else:
                            st.warning("No hay pólizas existentes en el sistema")
                            numero_poliza_seleccionado = numero_poliza_actual
                
                # Mostrar póliza seleccionada
                if numero_poliza_seleccionado:
                    st.success(f"✅ Póliza seleccionada: **{numero_poliza_seleccionado}**")
                else:
                    st.error("⚠️ Debe seleccionar un número de póliza")
                
                st.divider()
                
                st.info("📋 Seleccione los ramos de seguros que cubrirá esta póliza")
                
                # Obtener opciones de ramos disponibles
                ramos_disponibles = get_ramos_options()
                
                if ramos_disponibles:
                    # Inicializar la lista de ramos seleccionados en session_state si no existe
                    if "ramos_seleccionados" not in st.session_state:
                        st.session_state["ramos_seleccionados"] = []
                    
                    # Selector de ramo
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        ramo_a_agregar = st.selectbox(
                            "Seleccionar ramo de seguro",
                            ramos_disponibles,
                            format_func=lambda x: x[1] if x else "",
                            key="selector_ramo"
                        )
                    with col2:
                        if st.button("➕ Agregar Ramo", key="btn_agregar_ramo"):
                            if ramo_a_agregar and ramo_a_agregar not in st.session_state["ramos_seleccionados"]:
                                st.session_state["ramos_seleccionados"].append(ramo_a_agregar)
                                st.success(f"Ramo '{ramo_a_agregar[1]}' agregado exitosamente")
                            elif ramo_a_agregar in st.session_state["ramos_seleccionados"]:
                                st.warning("Este ramo ya está seleccionado")
                    
                    # Mostrar ramos seleccionados
                    if st.session_state["ramos_seleccionados"]:
                        st.markdown("**Ramos seleccionados:**")
                        
                        # Crear DataFrame con los ramos seleccionados
                        import pandas as pd
                        ramos_data = []
                        for idx, ramo in enumerate(st.session_state["ramos_seleccionados"]):
                            ramos_data.append({
                                "N°": idx + 1,
                                "ID": ramo[0],
                                "Nombre del Ramo": ramo[1],
                                "Acción": f"Eliminar_{idx}"
                            })
                        
                        df_ramos = pd.DataFrame(ramos_data)
                        
                        # Mostrar la tabla
                        st.dataframe(
                            df_ramos[["N°", "ID", "Nombre del Ramo"]],
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Botones para eliminar ramos individuales
                        st.markdown("**Eliminar ramos:**")
                        cols = st.columns(min(len(st.session_state["ramos_seleccionados"]), 4))
                        for idx, ramo in enumerate(st.session_state["ramos_seleccionados"]):
                            with cols[idx % 4]:
                                if st.button(f"🗑️ {ramo[1][:15]}...", key=f"eliminar_ramo_{idx}"):
                                    st.session_state["ramos_seleccionados"].remove(ramo)
                                    st.rerun()
                        
                        # Botón para limpiar todos los ramos
                        if st.button("🗑️ Limpiar todos los ramos", key="limpiar_ramos"):
                            st.session_state["ramos_seleccionados"] = []
                    st.warning("⚠️ No hay ramos de seguros registrados en el sistema. Por favor, registre ramos antes de crear pólizas.")

                st.divider()
                
                # Campo de Suma Asegurada
                st.markdown("**💰 Suma Asegurada**")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    suma_asegurada_input = st.text_input(
                        "Suma Asegurada",
                        help="Ingrese el monto máximo que cubrirá la póliza (solo números)",
                        placeholder="Ej: 100000.00"
                    )
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)  # Espacio para alinear
                    st.markdown("**USD $**")
                
                # Validar y formatear la suma asegurada
                suma_asegurada = ""
                if suma_asegurada_input:
                    try:
                        # Remover caracteres no numéricos excepto punto decimal
                        cleaned_amount = ''.join(c for c in suma_asegurada_input if c.isdigit() or c == '.')
                        if cleaned_amount:
                            amount = float(cleaned_amount)
                            suma_asegurada = f"${amount:,.2f} USD"
                            st.success(f"✅ Suma Asegurada formateada: **{suma_asegurada}**")
                        else:
                            st.error("⚠️ Ingrese un monto válido")
                    except ValueError:
                        st.error("⚠️ Formato de monto inválido. Use solo números y punto decimal.")
                
                # Guardar el valor limpio para la base de datos
                suma_asegurada_db = suma_asegurada_input if suma_asegurada_input else ""

                st.divider()
                
                # Campo de Prima Neta
                st.markdown("**💵 Prima Neta**")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    prima_neta_input = st.text_input(
                        "Prima Neta",
                        help="Ingrese el monto de la prima neta (solo números)",
                        placeholder="Ej: 5000.00"
                    )
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)  # Espacio para alinear
                    st.markdown("**USD $**")
                
                # Validar y formatear la prima neta
                prima_neta = ""
                if prima_neta_input:
                    try:
                        # Remover caracteres no numéricos excepto punto decimal
                        cleaned_amount = ''.join(c for c in prima_neta_input if c.isdigit() or c == '.')
                        if cleaned_amount:
                            amount = float(cleaned_amount)
                            prima_neta = f"${amount:,.2f} USD"
                            st.success(f"✅ Prima Neta formateada: **{prima_neta}**")
                        else:
                            st.error("⚠️ Ingrese un monto válido")
                    except ValueError:
                        st.error("⚠️ Formato de monto inválido. Use solo números y punto decimal.")
                
                # Guardar el valor limpio para la base de datos
                prima_neta_db = prima_neta_input if prima_neta_input else ""

                st.divider()
                
                # Campo de Observaciones
                st.markdown("**📝 Observaciones**")
                observaciones_ramos = st.text_area(
                    "Observaciones",
                    help="Ingrese observaciones adicionales sobre los ramos asegurados",
                    placeholder="Ej: Cobertura especial para equipos electrónicos...",
                    height=100
                )

        # FORMULARIO 2: Datos para facturación (solo si se ha pulsado "Siguiente" y paso 2)
        if st.session_state.get("poliza_form_step") == 2:
            with st.expander("Información Adicional y de facturacion"):
                
                
                col1, col2 = st.columns(2)
                with col1:
                    tipo_renovacion = st.selectbox("Tipo Renovación", ["MANUAL", "AUTOMATICO"])
                with col2:
                    # Campo eliminado: Tipo de Movimiento
                    pass
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
                    # ...existing code...
                    pass
                # Campo Valor de Cuota inicial (USD)
                col1, col2 = st.columns([3, 1])
                with col1:
                    valor_cuota_inicial = st.text_input(
                        "Valor de Cuota inicial",
                        help="Ingrese el valor de la cuota inicial (USD)",
                        placeholder="Ej: 100.00"
                    )
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("**USD $**")
                # Campo Valor de cuotas financiadas (USD)
                col1, col2 = st.columns([3, 1])
                with col1:
                    valor_cuotas_financiadas = st.text_input(
                        "Valor de cuotas financiadas",
                        help="Ingrese el valor de las cuotas financiadas (USD)",
                        placeholder="Ej: 200.00"
                    )
                with col2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("**USD $**")
                # Añadir campo formas_de_pago como selectbox
                formas_de_pago = st.selectbox(
                    "Forma de Pago",
                    ["Tarjeta de crédito", "Transferencia", "Débito", "Refinanciamiento"]
                )
                # Tipo de Factura después de anexos
                tipo_factura = st.selectbox("Tipo de Factura", ["Física", "Electrónica", "Otro"])
                
                st.markdown("### Información Factura")
                col1, col2 = st.columns(2)
                with col1:
                    numero_factura = st.text_input("Nº Factura")
                # Eliminar el campo de moneda
                # with col2:
                #     moneda = st.selectbox("Moneda", ["USD", "EUR", "Otra"])
                # Campo eliminado: Cláusulas particulares
                col1, col2 ,col3 = st.columns(3)
                with col1:
                    # Calcular Contrib. S.C.V.S. como 0.5% de la prima neta
                    contrib_scvs_calculado = ""
                    if prima_neta_db:
                        try:
                            prima_neta_valor = float(prima_neta_db)
                            contrib_scvs_valor = prima_neta_valor * 0.005  # 0.5%
                            contrib_scvs_calculado = f"{contrib_scvs_valor:.2f}"
                        except ValueError:
                            contrib_scvs_calculado = "0.00"
                    else:
                        contrib_scvs_calculado = "0.00"
                    
                    contrib_scvs = st.text_input(
                        "Contrib. S.C.V.S. (0.5% Prima Neta)", 
                        value=contrib_scvs_calculado,
                        disabled=True,
                        help="Calculado automáticamente como 0.5% de la Prima Neta"
                    )
                with col2:
                    # Calcular Seguro Social Campesino como 0.5% de la prima neta
                    ssoc_camp_calculado = ""
                    if prima_neta_db:
                        try:
                            prima_neta_valor = float(prima_neta_db)
                            ssoc_camp_valor = prima_neta_valor * 0.005  # 0.5%
                            ssoc_camp_calculado = f"{ssoc_camp_valor:.2f}"
                        except ValueError:
                            ssoc_camp_calculado = "0.00"
                    else:
                        ssoc_camp_calculado = "0.00"
                    
                    ssoc_camp = st.text_input(
                        "Seguro Campesino (0.5% Prima Neta)", 
                        value=ssoc_camp_calculado,
                        disabled=True,
                        help="Calculado automáticamente como 0.5% de la Prima Neta"
                    )
                with col3:
                    derechos_emision = st.text_input("Derechos Emisión")
                
                # Calcular Subtotal como suma de Prima Neta + Contrib. S.C.V.S. + Seguro Campesino + Derechos Emisión
                subtotal_calculado = ""
                try:
                    prima_neta_valor = float(prima_neta_db) if prima_neta_db else 0.0
                    contrib_valor = float(contrib_scvs_calculado) if contrib_scvs_calculado else 0.0
                    ssoc_valor = float(ssoc_camp_calculado) if ssoc_camp_calculado else 0.0
                    derechos_valor = float(derechos_emision) if derechos_emision else 0.0
                    subtotal_valor = prima_neta_valor + contrib_valor + ssoc_valor + derechos_valor
                    subtotal_calculado = f"{subtotal_valor:.2f}"
                except ValueError:
                    subtotal_calculado = "0.00"
                
                subtotal = st.text_input(
                    "Subtotal (Prima Neta + Contrib S.C.V.S. + Seguro Campesino + Derechos)",
                    value=subtotal_calculado,
                    disabled=True,
                    help="Calculado automáticamente como la suma de Prima Neta + Contribuciones + Derechos"
                )
                col1,col2,col3,col4 = st.columns(4)
                with col1:
                    # Calcular IVA como 15% del subtotal
                    iva_15_calculado = ""
                    if subtotal_calculado:
                        try:
                            subtotal_valor = float(subtotal_calculado)
                            iva_15_valor = subtotal_valor * 0.15  # 15%
                            iva_15_calculado = f"{iva_15_valor:.2f}"
                        except ValueError:
                            iva_15_calculado = "0.00"
                    else:
                        iva_15_calculado = "0.00"
                    
                    iva_15 = st.text_input(
                        "IVA (15% del Subtotal)", 
                        value=iva_15_calculado,
                        disabled=True,
                        help="Calculado automáticamente como 15% del Subtotal"
                    )
                with col2:
                    # Campo eliminado: C.Solidaria(2%)
                    # Campo eliminado: Financiación
                    pass
                # Campo eliminado: Otros IVA - ya no es necesario
                
                # Calcular Prima Total como suma de Subtotal + IVA
                total_calculado = ""
                try:
                    subtotal_valor = float(subtotal_calculado) if subtotal_calculado else 0.0
                    iva_valor = float(iva_15_calculado) if iva_15_calculado else 0.0
                    total_valor = subtotal_valor + iva_valor
                    total_calculado = f"{total_valor:.2f}"
                except ValueError:
                    total_calculado = "0.00"
                
                total = st.text_input(
                    "Prima Total (Subtotal + IVA)",
                    value=total_calculado,
                    disabled=True,
                    help="Prima Total calculada automáticamente como Subtotal + IVA (15%)"
                )
                       
                # Campo eliminado: Anexos (separados por coma)
                # anexos = st.text_area(
                #     "Anexos (separados por coma)",
                #     help="Ingrese los nombres de los anexos o archivos relacionados, separados por coma",
                #     placeholder="Ej: anexo1.pdf, anexo2.jpg"
                # )
                # anexos_list = [a.strip() for a in anexos.split(",")] if anexos else []

                guardar_fact = st.button("Guardar datos de facturación")

                if guardar_fact:
                    # Validar que se hayan seleccionado ramos
                    if not st.session_state.get("ramos_seleccionados"):
                        st.error("⚠️ Debe seleccionar al menos un ramo de seguro antes de guardar.")
                        return
                    
                    # Obtener datos de la relación asegurado-contratante
                    poliza_data = st.session_state.get("poliza_form_data", {})
                    
                    # Convertir la lista de ramos seleccionados a string separado por comas (nombres en lugar de IDs)
                    ramos_nombres = ", ".join([str(ramo[1]) for ramo in st.session_state.get("ramos_seleccionados", [])])
                    
                    st.session_state["facturacion_data"] = {
                        "tipo_renovacion": tipo_renovacion,
                        "gestion_cobro": selected_ejecutivo[0] if selected_ejecutivo else None,
                        "liberacion_comision": liberacion_comision,
                        "ramo_id": ramos_nombres,  # Guardar como string con nombres separados por comas
                        "suma_asegurada": suma_asegurada_db,
                        "prima_neta": prima_neta_db,
                        "observaciones_poliza": observaciones_ramos,
                        "numero_factura": numero_factura,
                        "contrib_scvs": contrib_scvs,
                        "derechos_emision": derechos_emision,
                        "ssoc_camp": ssoc_camp,
                        "subtotal": subtotal,
                        "iva_15": iva_15,
                        "total": total,
                        "cuotas": cuotas,
                        "valor_cuota_inicial": valor_cuota_inicial,
                        "valor_cuotas_financiadas": valor_cuotas_financiadas,
                        "tipo_factura": tipo_factura,
                        "agrupadora": selected_agrupadora[0] if selected_agrupadora else None,
                        # Nuevos campos de beneficiario
                        "asegurado_contratante": asegurado_contratante,
                        "beneficiario": beneficiario_nombre if asegurado_contratante == "No" else "",
                        "id_beneficiario": id_beneficiario if asegurado_contratante == "No" else "",
                        "formas_de_pago": formas_de_pago,
                    }
                    # Persistir la factura provisionalmente en la tabla `facturas` para que quede registrada
                    try:
                        connf = sqlite3.connect(DB_FILE)
                        curf = connf.cursor()
                        # Preparar montos numéricos seguros
                        try:
                            monto_neto_f = float(st.session_state["facturacion_data"].get("prima_neta", 0) or 0)
                        except Exception:
                            monto_neto_f = 0.0
                        try:
                            impuestos_f = float(st.session_state["facturacion_data"].get("contrib_scvs", 0) or 0) + float(st.session_state["facturacion_data"].get("ssoc_camp", 0) or 0) + float(st.session_state["facturacion_data"].get("derechos_emision", 0) or 0)
                        except Exception:
                            impuestos_f = 0.0
                        try:
                            iva_f = float(st.session_state["facturacion_data"].get("iva_15", 0) or 0)
                        except Exception:
                            iva_f = 0.0
                        try:
                            total_f = float(st.session_state["facturacion_data"].get("total", 0) or 0)
                        except Exception:
                            total_f = monto_neto_f + impuestos_f + iva_f

                        # Use None for empty invoice number so SQLite stores NULL (UNIQUE allows multiple NULLs)
                        numero_fact_raw = st.session_state["facturacion_data"].get("numero_factura", "")
                        numero_fact = numero_fact_raw.strip() if numero_fact_raw and str(numero_fact_raw).strip() else None
                        fecha_fact = st.session_state["facturacion_data"].get("fecha_factura", None)
                        # intentar derivar cliente_id del formulario de póliza si está disponible
                        cliente_id_for_fact = None
                        try:
                            cliente_id_for_fact = st.session_state.get("poliza_form_data", {}).get("tomador_id")
                        except Exception:
                            cliente_id_for_fact = None

                        # Use a local import of date to avoid accidental shadowing of the `datetime` name
                        from datetime import date
                        fecha_reg = date.today().strftime('%Y-%m-%d')

                        curf.execute(
                            '''
                            INSERT INTO facturas (numero_factura, poliza_id, movimiento_id, cliente_id, fecha_emision, monto_neto, impuestos, iva, total, estado, fecha_registro)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''',
                            (
                                numero_fact,
                                None,
                                None,
                                cliente_id_for_fact,
                                fecha_fact,
                                monto_neto_f,
                                impuestos_f,
                                iva_f,
                                total_f,
                                'Emitida',
                                fecha_reg
                            )
                        )
                        connf.commit()
                        factura_id_created = curf.lastrowid
                        st.session_state["factura_id"] = factura_id_created
                        st.success(f"Datos de facturación guardados y factura provisional registrada (id={factura_id_created}).")
                    except Exception as e:
                        st.warning(f"No se pudo crear factura provisional automáticamente: {e}")
                    finally:
                        try:
                            connf.close()
                        except Exception:
                            pass
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
                            # Asegurar que exista la columna canonical 'estado' y mapear valores desde el formulario
                            if "estado" not in poliza_cols:
                                try:
                                    cursor.execute("ALTER TABLE polizas ADD COLUMN estado TEXT")
                                    poliza_cols.append("estado")
                                except Exception:
                                    # Si falla, continuar sin detener la inserción
                                    pass
                            # El formulario guarda el estado en la clave 'estado_poliza'
                            if "estado_poliza" in insert_data and "estado" in poliza_cols:
                                insert_data["estado"] = insert_data.get("estado_poliza", "")
                                # conservar la clave original si la tabla también la tiene; evitar duplicados al mapear
                                insert_data.pop("estado_poliza", None)
                            # Si por alguna razón la tabla tiene 'estado_poliza' (vieja convención), también mantenerla
                            elif "estado_poliza" in poliza_cols and "estado" in insert_data:
                                insert_data["estado_poliza"] = insert_data.get("estado", "")
                                insert_data.pop("estado", None)
                            # --- Asegura que formas_de_pago esté en poliza_cols ---
                            if "formas_de_pago" not in poliza_cols:
                                cursor.execute("ALTER TABLE polizas ADD COLUMN formas_de_pago TEXT")
                                poliza_cols.append("formas_de_pago")
                            # --- FIN FIX ---
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
                                new_poliza_id = cursor.lastrowid
                                conn.commit()
                                st.success("Póliza creada exitosamente.")
                                st.session_state["poliza_form_step"] = 1
                                st.session_state["poliza_form_data"] = {}
                                st.session_state["facturacion_data"] = {}
                                # Si previamente se creó una factura provisional, ligarla a la póliza creada
                                try:
                                    factura_pending = st.session_state.get("factura_id")
                                    if factura_pending:
                                        cur_up = conn.cursor()
                                        cur_up.execute("UPDATE facturas SET poliza_id = ? WHERE id = ?", (new_poliza_id, factura_pending))
                                        conn.commit()
                                        # limpiar estado de factura provisional
                                        st.session_state.pop("factura_id", None)
                                except Exception:
                                    # No bloquear la creación si no se puede ligar la factura
                                    pass
                            except Exception as e:
                                st.error(f"Error al crear la póliza: {e}")
                            finally:
                                conn.close()
                            # Debug: ensure direccion/contenido were saved (logs for local debugging)
                            try:
                                conn2 = sqlite3.connect(DB_FILE)
                                cur2 = conn2.cursor()
                                cur2.execute("SELECT id, numero_poliza, direccion, contenido FROM polizas WHERE numero_poliza = ? ORDER BY id DESC LIMIT 1", (insert_data.get('numero_poliza', ''),))
                                saved = cur2.fetchone()
                                if saved:
                                    st.write('Guardado en DB:', saved)
                                conn2.close()
                            except Exception:
                                pass
    elif operation == "Leer":
        # Agregar estilos CSS para las tarjetas
        st.markdown("""
        <style>
        .poliza-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s, box-shadow 0.2s;
            color: white;
        }
        .poliza-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
        }
        .poliza-numero {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .poliza-info {
            font-size: 14px;
            margin: 5px 0;
            opacity: 0.9;
        }
        .poliza-estado {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            background-color: rgba(255, 255, 255, 0.2);
            font-size: 12px;
            margin-top: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Asegurar que exista la columna canonical 'estado'
        cursor.execute("PRAGMA table_info(polizas)")
        all_fields = [row[1] for row in cursor.fetchall()]
        if "estado" not in all_fields:
            try:
                cursor.execute("ALTER TABLE polizas ADD COLUMN estado TEXT")
                conn.commit()
                all_fields.append("estado")
            except Exception:
                pass

        # Construir diccionario de clientes
        cursor.execute("SELECT id, tipo_cliente, nombres, apellidos, razon_social FROM clients")
        clients_rows = cursor.fetchall()
        clientes_dict = {}
        for row in clients_rows:
            tipo = (row[1] or "").lower()
            if tipo in ("persona jurídica", "persona juridica", "empresa"):
                clientes_dict[row[0]] = row[4] or ""
            else:
                clientes_dict[row[0]] = f"{(row[2] or '').strip()} {(row[3] or '').strip()}".strip()

        # Obtener todas las pólizas con información adicional
        cursor.execute("PRAGMA table_info(polizas)")
        pol_cols = [r[1] for r in cursor.fetchall()]
        
        select_fields = ["id", "numero_poliza", "cliente_id", "aseguradora_id", "fecha_inicio", "fecha_fin"]
        if "tomador_nombre" in pol_cols:
            select_fields.append("tomador_nombre")
        if "estado" in pol_cols:
            select_fields.append("estado")
        elif "estado_poliza" in pol_cols:
            select_fields.append("estado_poliza")
        if "suma_asegurada" in pol_cols:
            select_fields.append("suma_asegurada")
        if "prima_neta" in pol_cols:
            select_fields.append("prima_neta")
            
        cursor.execute(f"SELECT {', '.join(select_fields)} FROM polizas ORDER BY fecha_inicio DESC")
        pol_rows = cursor.fetchall()
        
        # Obtener nombres de aseguradoras
        cursor.execute("SELECT id, razon_social FROM aseguradoras")
        aseguradoras_dict = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Obtener nombres de sucursales
        cursor.execute("SELECT id, nombre FROM sucursales")
        sucursales_dict = {row[0]: row[1] for row in cursor.fetchall()}
        
        # Obtener nombres de agrupadoras
        cursor.execute("SELECT id, name FROM companies")
        agrupadoras_dict = {row[0]: row[1] for row in cursor.fetchall()}

        if not pol_rows:
            st.info("📋 No hay pólizas registradas.")
            conn.close()
            return

        st.markdown(f"### 📊 Total de Pólizas: {len(pol_rows)}")
        st.divider()
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            estados_disponibles = list(set([row[7] if len(row) > 7 and row[7] else "Sin estado" for row in pol_rows]))
            filtro_estado = st.multiselect("Filtrar por estado", ["Todos"] + estados_disponibles, default=["Todos"])
        
        with col2:
            aseguradoras_disponibles = list(set([aseguradoras_dict.get(row[3], "Sin aseguradora") for row in pol_rows if len(row) > 3]))
            filtro_aseguradora = st.multiselect("Filtrar por aseguradora", ["Todas"] + aseguradoras_disponibles, default=["Todas"])
        
        with col3:
            buscar = st.text_input("🔍 Buscar por número de póliza", placeholder="Ej: PRG-1")

        # Aplicar filtros
        pol_rows_filtradas = pol_rows
        if "Todos" not in filtro_estado:
            pol_rows_filtradas = [r for r in pol_rows_filtradas if (len(r) > 7 and r[7] in filtro_estado) or (len(r) <= 7 and "Sin estado" in filtro_estado)]
        
        if "Todas" not in filtro_aseguradora:
            pol_rows_filtradas = [r for r in pol_rows_filtradas if aseguradoras_dict.get(r[3], "Sin aseguradora") in filtro_aseguradora]
        
        if buscar:
            pol_rows_filtradas = [r for r in pol_rows_filtradas if buscar.upper() in str(r[1]).upper()]

        if not pol_rows_filtradas:
            st.warning("⚠️ No se encontraron pólizas con los filtros aplicados.")
            conn.close()
            return

        st.markdown(f"**Mostrando {len(pol_rows_filtradas)} pólida(s)**")
        
        # Mostrar pólizas en tarjetas (2 columnas)
        for idx in range(0, len(pol_rows_filtradas), 2):
            cols = st.columns(2)
            
            for col_idx, col in enumerate(cols):
                if idx + col_idx < len(pol_rows_filtradas):
                    row = pol_rows_filtradas[idx + col_idx]
                    
                    with col:
                        # Extraer información de la fila
                        poliza_id = row[0]
                        numero_poliza = row[1] or "(Sin número)"
                        cliente_id = row[2]
                        aseguradora_id = row[3]
                        fecha_inicio = row[4] if len(row) > 4 else ""
                        fecha_fin = row[5] if len(row) > 5 else ""
                        tomador_nombre = row[6] if len(row) > 6 and "tomador_nombre" in select_fields else None
                        estado = row[7] if len(row) > 7 else "Sin estado"
                        suma_asegurada = row[8] if len(row) > 8 else ""
                        prima_neta = row[9] if len(row) > 9 else ""
                        
                        # Obtener nombre del cliente
                        client_name = "(Sin solicitante)"
                        if tomador_nombre and str(tomador_nombre).strip().lower() not in ("none", ""):
                            client_name = tomador_nombre
                        elif cliente_id and cliente_id in clientes_dict:
                            client_name = clientes_dict[cliente_id] or client_name
                        
                        # Obtener nombre de aseguradora
                        aseguradora_nombre = aseguradoras_dict.get(aseguradora_id, "(Sin aseguradora)")
                        
                        # Color de estado
                        estado_colors = {
                            "Borrador": "🟡",
                            "Emitida": "🟢",
                            "Anulada": "🔴",
                            "Activa": "🟢",
                            "Pagada": "🟢",
                            "Pendiente de Pago": "🟠"
                        }
                        estado_icon = estado_colors.get(estado, "⚪")
                        
                        # Crear tarjeta con expander
                        with st.expander(f"📄 {numero_poliza}", expanded=False):
                            st.markdown(f"""
                            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                        border-radius: 10px; padding: 15px; color: white; margin-bottom: 10px;'>
                                <div style='font-size: 20px; font-weight: bold; margin-bottom: 10px;'>
                                    {numero_poliza}
                                </div>
                                <div style='font-size: 14px; opacity: 0.9;'>
                                    👤 <strong>Cliente:</strong> {client_name}<br>
                                    🏢 <strong>Aseguradora:</strong> {aseguradora_nombre}<br>
                                    📅 <strong>Vigencia:</strong> {fecha_inicio} → {fecha_fin}<br>
                                    {estado_icon} <strong>Estado:</strong> {estado}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Obtener detalles completos de la póliza
                            cursor.execute("PRAGMA table_info(polizas)")
                            all_fields = [row[1] for row in cursor.fetchall()]
                            cursor.execute(f"SELECT {', '.join(all_fields)} FROM polizas WHERE id=?", (poliza_id,))
                            poliza_row = cursor.fetchone()
                            
                            if poliza_row:
                                poliza_dict = dict(zip(all_fields, poliza_row))
                                
                                # Información adicional en tabs
                                tab1, tab2, tab3 = st.tabs(["📋 Detalles", "💰 Facturación", "📊 Documentos"])
                                
                                with tab1:
                                    st.markdown("**Información General**")
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.text_input("Suma Asegurada", value=poliza_dict.get("suma_asegurada", ""), disabled=True, key=f"suma_{poliza_id}")
                                        st.text_input("Prima Neta", value=poliza_dict.get("prima_neta", ""), disabled=True, key=f"prima_{poliza_id}")
                                        
                                        # Mostrar ramos asociados (ya están como nombres)
                                        ramos_nombres = poliza_dict.get("ramo_id", "")
                                        if ramos_nombres and str(ramos_nombres).strip():
                                            st.text_area("Ramos de Seguro", value=ramos_nombres, disabled=True, key=f"ramos_{poliza_id}", height=80)
                                        else:
                                            st.text_input("Ramos de Seguro", value="Sin ramos asignados", disabled=True, key=f"ramos_{poliza_id}")
                                    with col_b:
                                        st.text_input("Beneficiario", value=poliza_dict.get("beneficiario", ""), disabled=True, key=f"benef_{poliza_id}")
                                        st.text_input("ID Beneficiario", value=poliza_dict.get("id_beneficiario", ""), disabled=True, key=f"id_benef_{poliza_id}")
                                    
                                    st.text_area("Dirección", value=poliza_dict.get("direccion", ""), disabled=True, height=80, key=f"dir_{poliza_id}")
                                    st.text_area("Contenido", value=poliza_dict.get("contenido", ""), disabled=True, height=80, key=f"cont_{poliza_id}")
                                
                                with tab2:
                                    st.markdown("**Información de Facturación**")
                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        st.text_input("Número Factura", value=poliza_dict.get("numero_factura", ""), disabled=True, key=f"nfact_{poliza_id}")
                                        st.text_input("Subtotal", value=poliza_dict.get("subtotal", ""), disabled=True, key=f"sub_{poliza_id}")
                                        st.text_input("IVA", value=poliza_dict.get("iva_15", ""), disabled=True, key=f"iva_{poliza_id}")
                                    with col_b:
                                        st.text_input("Total", value=poliza_dict.get("total", ""), disabled=True, key=f"tot_{poliza_id}")
                                        st.text_input("Cuotas", value=poliza_dict.get("cuotas", ""), disabled=True, key=f"cuot_{poliza_id}")
                                        st.text_input("Forma de Pago", value=poliza_dict.get("formas_de_pago", ""), disabled=True, key=f"fpago_{poliza_id}")
                                
                                with tab3:
                                    # Movimientos asociados
                                    try:
                                        cursor.execute("""
                                            SELECT m.id, m.codigo_movimiento, m.tipo_movimiento, m.estado, m.fecha_movimiento
                                            FROM movimientos_poliza m
                                            WHERE m.poliza_id = ?
                                            ORDER BY m.fecha_movimiento DESC
                                        """, (poliza_id,))
                                        movimientos = cursor.fetchall()
                                        
                                        if movimientos:
                                            st.markdown("**📝 Movimientos**")
                                            import pandas as pd
                                            df_mov = pd.DataFrame(movimientos, columns=['ID', 'Código', 'Tipo', 'Estado', 'Fecha'])
                                            st.dataframe(df_mov, use_container_width=True, hide_index=True)
                                        else:
                                            st.info("Sin movimientos registrados")
                                    except Exception:
                                        pass
                                    
                                    # Facturas
                                    try:
                                        cursor.execute("""
                                            SELECT numero_factura, fecha_emision, total, estado
                                            FROM facturas WHERE poliza_id = ?
                                        """, (poliza_id,))
                                        facturas = cursor.fetchall()
                                        
                                        if facturas:
                                            st.markdown("**💵 Facturas**")
                                            import pandas as pd
                                            df_fact = pd.DataFrame(facturas, columns=['Número', 'Fecha', 'Total', 'Estado'])
                                            st.dataframe(df_fact, use_container_width=True, hide_index=True)
                                        else:
                                            st.info("Sin facturas registradas")
                                    except Exception:
                                        pass

        conn.close()
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
                    elif field == "ramo_id":
                        ramos_options = get_ramos_options()
                        current_ramo = next((r for r in ramos_options if r[0] == poliza_dict.get(field)), None)
                        if ramos_options:
                            updated = st.selectbox("Ramos de Seguro", ramos_options, index=ramos_options.index(current_ramo) if current_ramo else 0, format_func=lambda x: x[1])
                            updated_values[field] = updated[0]
                        else:
                            st.warning("No hay ramos de seguros registrados.")
                            updated_values[field] = None
                    elif field in ["fecha_inicio", "fecha_fin", "fecha_emision"]:
                        import datetime
                        val = poliza_dict.get(field)
                        try:
                            val = datetime.datetime.strptime(val, "%Y-%m-%d").date() if val else None
                        except Exception:
                            val = None
                        updated_values[field] = st.date_input(field.replace("_", " ").capitalize(), value=val)
                    elif field == "estado":
                        # Usar la lista canonica ESTADOS_POLIZA. Si el valor actual viene en 'estado' o 'estado_poliza', usarlo como valor por defecto.
                        current_estado = poliza_dict.get(field) or poliza_dict.get("estado_poliza") or ""
                        try:
                            default_idx = ESTADOS_POLIZA.index(current_estado) if current_estado in ESTADOS_POLIZA else 0
                        except Exception:
                            default_idx = 0
                        updated_values[field] = st.selectbox("Estado", ESTADOS_POLIZA, index=default_idx)
                    elif field == "direccion":
                        updated_values[field] = st.text_input("Dirección", value=str(poliza_dict.get(field, "")))
                    elif field == "contenido":
                        updated_values[field] = st.text_area("Contenido asegurado", value=str(poliza_dict.get(field, "")), height=120)
                    else:
                        updated_values[field] = st.text_input(field.replace("_", " ").capitalize(), value=str(poliza_dict.get(field, "")))
                submit = st.form_submit_button("Actualizar Póliza")
                if submit:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        # Mantener consistencia entre columnas 'estado' y 'estado_poliza' si existen ambas
                        if "estado" in all_fields and "estado_poliza" in all_fields:
                            # si se seleccionó 'estado' (selectbox), propagar a 'estado_poliza'
                            if "estado" in updated_values:
                                updated_values["estado_poliza"] = updated_values.get("estado", "")
                            elif "estado_poliza" in updated_values:
                                updated_values["estado"] = updated_values.get("estado_poliza", "")
                        # Si la tabla tiene solo 'estado_poliza' pero no 'estado', crear 'estado' para normalizar
                        if "estado_poliza" in all_fields and "estado" not in all_fields:
                            try:
                                cursor.execute("ALTER TABLE polizas ADD COLUMN estado TEXT")
                                conn.commit()
                                all_fields.append("estado")
                                updated_values["estado"] = updated_values.get("estado_poliza", "")
                            except Exception:
                                pass
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
        st.warning("⚠️ **Atención**: Esta acción eliminará permanentemente la póliza seleccionada.")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, numero_poliza FROM polizas ORDER BY numero_poliza")
        polizas = cursor.fetchall()
        
        if not polizas:
            st.info("No hay pólizas registradas para eliminar.")
            conn.close()
            return
        
        # Mostrar información de la póliza antes de eliminar
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_poliza = st.selectbox(
                "Selecciona la póliza a eliminar", 
                polizas, 
                format_func=lambda x: f"Póliza: {x[1]} (ID: {x[0]})",
                help="Seleccione la póliza que desea eliminar del sistema"
            )
        
        if selected_poliza:
            # Verificar qué columnas existen en la tabla
            cursor.execute("PRAGMA table_info(polizas)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            # Construir la consulta solo con columnas que existan
            select_fields = ["numero_poliza"]
            if "tomador_id" in existing_columns:
                select_fields.append("tomador_id")
            elif "cliente_id" in existing_columns:
                select_fields.append("cliente_id")
            else:
                select_fields.append("NULL as tomador_id")
                
            if "aseguradora_id" in existing_columns:
                select_fields.append("aseguradora_id")
            else:
                select_fields.append("NULL as aseguradora_id")
                
            if "fecha_inicio" in existing_columns:
                select_fields.append("fecha_inicio")
            else:
                select_fields.append("NULL as fecha_inicio")
                
            if "fecha_fin" in existing_columns:
                select_fields.append("fecha_fin")
            else:
                select_fields.append("NULL as fecha_fin")
                
            if "estado_poliza" in existing_columns:
                select_fields.append("estado_poliza")
            elif "estado" in existing_columns:
                select_fields.append("estado")
            else:
                select_fields.append("NULL as estado_poliza")
            
            # Obtener detalles de la póliza seleccionada
            query = f"SELECT {', '.join(select_fields)} FROM polizas WHERE id=?"
            cursor.execute(query, (selected_poliza[0],))
            poliza_details = cursor.fetchone()
            
            if poliza_details:
                numero_poliza = poliza_details[0]
                tomador_id = poliza_details[1] if len(poliza_details) > 1 else None
                aseguradora_id = poliza_details[2] if len(poliza_details) > 2 else None
                fecha_inicio = poliza_details[3] if len(poliza_details) > 3 else None
                fecha_fin = poliza_details[4] if len(poliza_details) > 4 else None
                estado_poliza = poliza_details[5] if len(poliza_details) > 5 else None
                
                # Obtener nombre del tomador
                tomador_name = "Sin tomador"
                if tomador_id:
                    try:
                        cursor.execute("SELECT tipo_cliente, nombres, apellidos, razon_social FROM clients WHERE id=?", (tomador_id,))
                        client_info = cursor.fetchone()
                        if client_info:
                            tomador_name = client_info[3] if client_info[0] == "Empresa" else f"{client_info[1]} {client_info[2]}"
                        else:
                            tomador_name = "Cliente no encontrado"
                    except Exception:
                        tomador_name = "Error al obtener cliente"
                
                # Obtener nombre de aseguradora
                aseguradora_name = "Sin aseguradora"
                if aseguradora_id:
                    try:
                        cursor.execute("SELECT razon_social FROM aseguradoras WHERE id=?", (aseguradora_id,))
                        aseg_info = cursor.fetchone()
                        aseguradora_name = aseg_info[0] if aseg_info else "Aseguradora no encontrada"
                    except Exception:
                        aseguradora_name = "Error al obtener aseguradora"
                
                # Mostrar información de la póliza
                st.markdown("### 📄 Información de la Póliza a Eliminar")
                
                info_data = {
                    "Campo": ["Número de Póliza", "Solicitante", "Aseguradora", "Vigencia", "Estado"],
                    "Valor": [
                        numero_poliza or "Sin número",
                        tomador_name,
                        aseguradora_name,
                        f"{fecha_inicio} a {fecha_fin}" if fecha_inicio and fecha_fin else "Sin vigencia",
                        estado_poliza if estado_poliza else "Sin estado"
                    ]
                }
                
                import pandas as pd
                df_info = pd.DataFrame(info_data)
                st.dataframe(df_info, use_container_width=True, hide_index=True)
                
                st.divider()
                
                # Confirmación de eliminación
                st.markdown("### 🗑️ Confirmación de Eliminación")
                
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col2:
                    confirmar = st.checkbox(
                        "Confirmo que deseo eliminar esta póliza permanentemente",
                        help="Marque esta casilla para habilitar el botón de eliminación"
                    )
                
                st.markdown("")  # Espacio
                
                # Botón de eliminación
                col1, col2, col3 = st.columns([1, 1, 1])
                
                with col2:
                    if st.button(
                        "🗑️ ELIMINAR PÓLIZA", 
                        disabled=not confirmar,
                        type="primary" if confirmar else "secondary",
                        use_container_width=True
                    ):
                        try:
                            cursor.execute("DELETE FROM polizas WHERE id = ?", (selected_poliza[0],))
                            conn.commit()
                            st.success(f"✅ Póliza '{numero_poliza}' eliminada exitosamente.")
                            st.balloons()
                            
                            # Limpiar session state para refrescar la lista
                            if "poliza_form_data" in st.session_state:
                                del st.session_state["poliza_form_data"]
                            
                            # Rerun para actualizar la interfaz
                            st.rerun()
                            
                        except sqlite3.Error as e:
                            st.error(f"❌ Error al eliminar la póliza: {str(e)}")
                        except Exception as e:
                            st.error(f"❌ Error inesperado: {str(e)}")
            else:
                st.error("No se pudieron obtener los detalles de la póliza seleccionada.")
        
        conn.close()