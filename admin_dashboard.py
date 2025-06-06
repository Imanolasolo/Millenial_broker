import streamlit as st
import sqlite3
from dbconfig import DB_FILE
from crud.user_crud import create_user, read_users, update_user, delete_user, get_user_details
<<<<<<< HEAD
from crud.client_crud import create_client, read_clients, update_client, delete_client
from crud.aseguradora_crud import create_aseguradora, read_aseguradoras, update_aseguradora, delete_aseguradora
=======
from client_crud import create_client, read_clients, update_client, delete_client
>>>>>>> b0be7c8f67415dcd7d0dfd5253f143d27a0627f1
from create_dashboard import create_dashboard
from database_config import initialize_database

initialize_database()

def admin_dashboard():
    # Retrieve username from session state
    username = st.session_state.get("username")
    user_details = get_user_details(username) if username else None

    # Display header with avatar, name, and group
    st.sidebar.image("assets/avatar.png", width=100)  # Ruta actualizada
    st.sidebar.markdown(f"**Usuario:** {user_details['full_name'] if user_details else 'Desconocido'}")
    st.sidebar.markdown(f"**Afiliación:** {user_details['company_name'] if user_details else 'Sin afiliación'}")

    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("assets/logo.png", width=100)
    with col2:
        st.title("Dashboard de Administrador")
    st.write("Bienvenido, administrador")

    st.markdown("""
        Este es el centro de control para gestionar usuarios, clientes, reportes y configuraciones del sistema.
        Utiliza la barra lateral para navegar entre los diferentes módulos.
    """)

    with st.expander("Instrucciones Básicas"):
        st.markdown("""
        ### Cómo usar el Dashboard:        
        1. **Usuarios**: Gestiona los usuarios del sistema (crear, leer, modificar, borrar).
        2. **Clientes**: Administra la información de los clientes.
        3. **Reportes**: Genera y visualiza reportes.
        4. **Configuración**: Ajusta el sistema.
        5. **Roles**: Gestiona los roles disponibles.
        6. **Pólizas**: Gestiona las pólizas de seguro.
        7. **Agrupadores**: Gestiona los agrupadores.
        8. **Aseguradoras**: Gestiona las aseguradoras.
        9. **Ramos de Seguros**: Gestiona los ramos de seguros.
        10. **Logout**: Cierra sesión.
        """)

    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            background-color: #3A92AB !important;
        }
        [data-testid="stSidebar"] button {
            background-color: white !important;
            color: black !important;
            border: 1px solid #007BFF !important;
        }
        [data-testid="stSidebar"] button:hover {
            background-color: #e6e6e6 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Estilos para reducir el ancho de TODOS los campos de entrada (inputs, selects, multiselects, date, file, number, checkbox, radio, color, slider, etc.)
    st.markdown("""
        <style>
        /* Inputs de texto */
        .stTextInput input {
            max-width: 300px !important;
            min-width: 120px !important;
            width: 50% !important;
        }
        /* Áreas de texto */
        .stTextArea textarea {
            max-width: 300px !important;
            min-width: 120px !important;
            width: 50% !important;
        }
        /* Selectbox y multiselect */
        .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] {
            max-width: 300px !important;
            min-width: 120px !important;
            width: 50% !important;
        }
        /* Date input */
        .stDateInput input {
            max-width: 300px !important;
            min-width: 120px !important;
            width: 50% !important;
        }
        /* File uploader */
        .stFileUploader {
            max-width: 300px !important;
            min-width: 120px !important;
            width: 50% !important;
        }
        /* Number input */
        .stNumberInput input {
            max-width: 300px !important;
            min-width: 120px !important;
            width: 50% !important;
        }
        /* Checkbox y radio */
        .stCheckbox, .stRadio {
            max-width: 300px !important;
            min-width: 120px !important;
            width: 50% !important;
        }
        /* Color picker */
        .stColorPicker {
            max-width: 300px !important;
            min-width: 120px !important;
            width: 50% !important;
        }
        /* Slider */
        .stSlider {
            max-width: 300px !important;
            min-width: 120px !important;
            width: 50% !important;
        }
        /* Botones */
        button[kind="primary"], button[kind="secondary"], .stButton button {
            max-width: 300px !important;
            min-width: 120px !important;
            width: 50% !important;
        }
        /* Centrar los inputs si lo deseas */
        .stTextInput, .stTextArea, .stSelectbox, .stMultiSelect, .stDateInput, .stFileUploader, .stNumberInput, .stCheckbox, .stRadio, .stColorPicker, .stSlider {
            margin-left: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if "module" not in st.session_state:
        st.session_state["module"] = None

    st.sidebar.title("Navegación")
    st.sidebar.image("assets/logo.png", width=80)
    if st.sidebar.button("Usuarios"):
        st.session_state["module"] = "Usuarios"
    if st.sidebar.button("Clientes"):
        st.session_state["module"] = "Clientes"
    if st.sidebar.button("Roles"):
        st.session_state["module"] = "Roles"
    if st.sidebar.button("Pólizas"):
        st.session_state["module"] = "Pólizas"
    if st.sidebar.button("Agrupadores"):  # Replace "Empresas" with "Agrupadores"
        st.session_state["module"] = "Agrupadores"
    if st.sidebar.button("Aseguradoras"):
        st.session_state["module"] = "Aseguradoras"
    if st.sidebar.button("Ramos de Seguros"):
        st.session_state["module"] = "Ramos de Seguros"
    
    module = st.session_state["module"]

    if module == "Usuarios":
        st.subheader("Gestión de Usuarios")
        operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

        if operation == "Crear":
            username = st.text_input("Nombre de Usuario")
            password = st.text_input("Contraseña", type="password")
            correo = st.text_input("Correo Electrónico")
            nombres = st.text_input("Nombres")
            apellidos = st.text_input("Apellidos")
            telefono = st.text_input("Teléfono")
            role = st.selectbox("Rol", [role[0] for role in sqlite3.connect(DB_FILE).cursor().execute("SELECT name FROM roles").fetchall()])
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM companies")
            companies = cursor.fetchall()
            conn.close()
            company_id = st.selectbox("Agrupador", companies, format_func=lambda x: x[1])  # Update label

            if st.button("Crear Usuario"):
                if username and password and correo and nombres and apellidos and telefono and role and company_id:
                    result = create_user(
                        username=username,
                        password=password,
                        role=role,
                        correo=correo,
                        nombres=nombres,
                        apellidos=apellidos,
                        telefono=telefono,
                        company_id=company_id[0],
                        fecha_registro=st.date_input("Fecha de Registro").strftime("%Y-%m-%d"),
                        ultima_actualizacion=st.date_input("Última Actualización").strftime("%Y-%m-%d")
                    )
                    st.success(result) if "exitosamente" in result else st.error(result)
                else:
                    st.error("Completa todos los campos.")

        elif operation == "Leer":
            st.subheader("Lista de Usuarios")
            users = read_users()
            if users:
                # Excluir la columna 'password' de los datos mostrados
                for user in users:
                    user.pop("password", None)
                st.table(users)
            else:
                st.info("No hay usuarios registrados.")

        elif operation == "Modificar":
            st.subheader("Modificar Usuario")
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users")
            users = [user[0] for user in cursor.fetchall()]
            cursor.execute("SELECT name FROM roles")
            roles = [role[0] for role in cursor.fetchall()]
            cursor.execute("SELECT id, name FROM companies")
            companies = cursor.fetchall()
            conn.close()

            selected_user = st.selectbox("Selecciona un usuario", users)

            if selected_user:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE username = ?", (selected_user,))
                user_data = cursor.fetchone()
                conn.close()

                if user_data:
                    # Populate fields with existing user data
                    username = st.text_input("Nombre de Usuario", value=user_data[1])
                    new_password = st.text_input("Nueva Contraseña", type="password")
                    correo = st.text_input("Correo Electrónico", value=user_data[4])
                    nombres = st.text_input("Nombres", value=user_data[5])
                    apellidos = st.text_input("Apellidos", value=user_data[6])
                    telefono = st.text_input("Teléfono", value=user_data[7])
                    role = st.selectbox("Rol", roles, index=roles.index(user_data[3]))
                    company_ids = [company[0] for company in companies]
                    company_index = company_ids.index(user_data[8]) if user_data[8] in company_ids else 0
                    company_id = st.selectbox("Agrupador", companies, format_func=lambda x: x[1], index=company_index)

                    if st.button("Actualizar Usuario"):
                        if username and correo and nombres and apellidos and telefono and role and company_id:
                            password_to_store = new_password if new_password else user_data[2]

                            result = update_user(
                                username=username,
                                password=password_to_store,
                                role=role,
                                correo=correo,
                                nombres=nombres,
                                apellidos=apellidos,
                                telefono=telefono,
                                company_id=company_id[0],
                                fecha_registro=user_data[8],
                                ultima_actualizacion=st.date_input("Última Actualización").strftime("%Y-%m-%d")
                            )
                            st.success(result) if "exitosamente" in result else st.error(result)
                        else:
                            st.error("Completa todos los campos.")

        elif operation == "Borrar":
            st.subheader("Eliminar Usuario")
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users")
            users = [user[0] for user in cursor.fetchall()]
            conn.close()

            selected_user = st.selectbox("Selecciona un usuario para eliminar", users)

            if st.button("Eliminar Usuario"):
                result = delete_user(selected_user)
                st.success(result) if "exitosamente" in result else st.error(result)

    elif module == "Clientes":
        st.subheader("Gestión de Clientes")
        operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

        if operation == "Crear":
            tipo_cliente = st.selectbox("Tipo de Cliente", ["Individual", "Empresa"])
            nombres = st.text_input("Nombres")
            apellidos = st.text_input("Apellidos")
            razon_social = st.text_input("Razón Social") if tipo_cliente == "Empresa" else None
            tipo_documento = st.selectbox("Tipo de Documento", ["Cédula", "Pasaporte", "RUC"])  # Cambiar "DNI" por "Cédula"

            # Mostrar el campo de número de documento según el tipo seleccionado
            if tipo_documento == "Cédula" or tipo_documento == "Pasaporte":
                numero_documento = st.text_input(f"Número de {tipo_documento}")
                if tipo_documento == "Cédula" and len(numero_documento) not in (0, 10):
                    st.warning("El número de Cédula debe tener exactamente 10 dígitos.")
            elif tipo_documento == "RUC":
                numero_documento = st.text_input("Número de RUC")
                if len(numero_documento) not in (0, 13):
                    st.warning("El número de RUC debe tener exactamente 13 dígitos.")

            fecha_nacimiento = st.date_input("Fecha de Nacimiento")
            nacionalidad = st.text_input("Nacionalidad")
            sexo = st.selectbox("Sexo", ["Masculino", "Femenino", "Otro"])
            estado_civil = st.selectbox("Estado Civil", ["Soltero", "Casado", "Divorciado", "Viudo"])
            correo_electronico = st.text_input("Correo Electrónico")
            telefono_movil = st.text_input("Teléfono Móvil")
            telefono_fijo = st.text_input("Teléfono Fijo")
            direccion_domicilio = st.text_area("Dirección Domicilio")
            provincia = st.text_input("Provincia")
            ciudad = st.text_input("Ciudad")
            codigo_postal = st.text_input("Código Postal")
            ocupacion_profesion = st.text_input("Ocupación/Profesión")
            empresa_trabajo = st.text_input("Empresa de Trabajo")
            tipo_empresa = st.text_input("Tipo de Empresa")
            ingresos_mensuales = st.text_input("Ingresos Mensuales")
            nivel_educacion = st.text_input("Nivel de Educación")
            fumador = st.selectbox("Fumador", ["Sí", "No"])
            actividades_riesgo = st.text_area("Actividades de Riesgo")
            historial_medico = st.text_area("Historial Médico")
            historial_siniestros = st.text_area("Historial de Siniestros")
            vehiculos_registrados = st.text_area("Vehículos Registrados")
            propiedades = st.text_area("Propiedades")
            tipo_contribuyente = st.text_input("Tipo de Contribuyente")
            representante_legal_id = st.text_input("ID Representante Legal")
            observaciones_legales = st.text_area("Observaciones Legales")
            canal_preferido_contacto = st.text_input("Canal Preferido de Contacto")
            notas_adicionales = st.text_area("Notas Adicionales")
            fecha_registro = st.date_input("Fecha de Registro")
            ultima_actualizacion = st.date_input("Última Actualización")

            if st.button("Crear Cliente"):
                if nombres and apellidos and numero_documento and correo_electronico:
                    result = create_client(
                        tipo_cliente=tipo_cliente,
                        nombres=nombres,
                        apellidos=apellidos,
                        razon_social=razon_social,
                        tipo_documento=tipo_documento,
                        numero_documento=numero_documento,
                        fecha_nacimiento=fecha_nacimiento.strftime("%Y-%m-%d"),
                        nacionalidad=nacionalidad,
                        sexo=sexo,
                        estado_civil=estado_civil,
                        correo_electronico=correo_electronico,
                        telefono_movil=telefono_movil,
                        telefono_fijo=telefono_fijo,
                        direccion_domicilio=direccion_domicilio,
                        provincia=provincia,
                        ciudad=ciudad,
                        codigo_postal=codigo_postal,
                        ocupacion_profesion=ocupacion_profesion,
                        empresa_trabajo=empresa_trabajo,
                        tipo_empresa=tipo_empresa,
                        ingresos_mensuales=ingresos_mensuales,
                        nivel_educacion=nivel_educacion,
                        fumador=fumador,
                        actividades_riesgo=actividades_riesgo,
                        historial_medico=historial_medico,
                        historial_siniestros=historial_siniestros,
                        vehiculos_registrados=vehiculos_registrados,
                        propiedades=propiedades,
                        tipo_contribuyente=tipo_contribuyente,
                        representante_legal_id=representante_legal_id,
                        observaciones_legales=observaciones_legales,
                        canal_preferido_contacto=canal_preferido_contacto,
                        notas_adicionales=notas_adicionales,
                        fecha_registro=fecha_registro.strftime("%Y-%m-%d"),
                        ultima_actualizacion=ultima_actualizacion.strftime("%Y-%m-%d")
                    )
                    st.success(result) if "exitosamente" in result else st.error(result)
                else:
                    st.error("Completa todos los campos obligatorios.")

        elif operation == "Leer":
            st.subheader("Lista de Clientes")
            clients = read_clients()
            if clients:
                # Mostrar todos los campos de los clientes with barra horizontal
                st.write([client for client in clients])
            else:
                st.info("No hay clientes registrados.")

        elif operation == "Modificar":
            st.subheader("Modificar Cliente")
            clients = read_clients()
            client_ids = [client["id"] for client in clients]
            selected_client_id = st.selectbox("Selecciona un cliente", client_ids)

            if selected_client_id:
                client_data = next(client for client in clients if client["id"] == selected_client_id)
                nombres = st.text_input("Nombres", value=client_data["nombres"])
                apellidos = st.text_input("Apellidos", value=client_data["apellidos"])
                correo_electronico = st.text_input("Correo Electrónico", value=client_data["correo_electronico"])
                telefono_movil = st.text_input("Teléfono Móvil", value=client_data["telefono_movil"])
                direccion_domicilio = st.text_area("Dirección Domicilio", value=client_data["direccion_domicilio"])

                if st.button("Actualizar Cliente"):
                    result = update_client(
                        client_id=selected_client_id,
                        nombres=nombres,
                        apellidos=apellidos,
                        correo_electronico=correo_electronico,
                        telefono_movil=telefono_movil,
                        direccion_domicilio=direccion_domicilio
                    )
                    st.success(result) if "exitosamente" in result else st.error(result)

        elif operation == "Borrar":
            st.subheader("Eliminar Cliente")
            clients = read_clients()
            client_ids = [client["id"] for client in clients]
            selected_client_id = st.selectbox("Selecciona un cliente para eliminar", client_ids)

            if st.button("Eliminar Cliente"):
                result = delete_client(selected_client_id)
                st.success(result) if "exitosamente" in result else st.error(result)

    elif module == "Roles":
        st.subheader("Gestión de Roles")
        operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

        if operation == "Crear":
            role_name = st.text_input("Nombre del Rol")
            if st.button("Crear Rol"):
                if role_name:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("INSERT INTO roles (name) VALUES (?)", (role_name,))
                        conn.commit()
                        if role_name.lower() != "administrador":  # Skip dashboard creation for "Administrador"
                            create_dashboard(role_name)
                        cursor.execute("INSERT INTO role_logs (role_name, action) VALUES (?, ?)", (role_name, "Creación"))
                        conn.commit()
                        st.success("Rol creado exitosamente")
                    except sqlite3.IntegrityError:
                        st.error("El rol ya existe.")
                    finally:
                        conn.close()
                else:
                    st.error("Ingresa un nombre para el rol.")

        elif operation == "Leer":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM roles")
            roles = cursor.fetchall()
            conn.close()
            for role in roles:
                st.write(f"ID: {role[0]}, Nombre: {role[1]}")

        elif operation == "Modificar":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM roles")
            roles = cursor.fetchall()
            conn.close()

            selected_role = st.selectbox("Selecciona un rol", roles, format_func=lambda x: x[1])
            new_name = st.text_input("Nuevo nombre del rol")

            if st.button("Modificar Rol"):
                if new_name:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("UPDATE roles SET name = ? WHERE id = ?", (new_name, selected_role[0]))
                        conn.commit()
                        st.success("Rol actualizado exitosamente")
                    except sqlite3.IntegrityError:
                        st.error("El nuevo nombre ya existe.")
                    finally:
                        conn.close()
                else:
                    st.error("Ingresa un nuevo nombre.")

        elif operation == "Borrar":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM roles")
            roles = cursor.fetchall()
            conn.close()

            selected_role = st.selectbox("Selecciona un rol para eliminar", roles, format_func=lambda x: x[1])

            if st.button("Eliminar Rol"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM roles WHERE id = ?", (selected_role[0],))
                    conn.commit()
                    cursor.execute("INSERT INTO role_logs (role_name, action) VALUES (?, ?)", (selected_role[1], "Eliminación"))
                    conn.commit()
                    st.success("Rol eliminado exitosamente")
                except sqlite3.IntegrityError:
                    st.error("No se puede eliminar el rol asignado a usuarios.")
                finally:
                    conn.close()

    elif module == "Pólizas":
        st.subheader("Gestión de Pólizas de Seguro")
        operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

        if operation == "Crear":
            numero_poliza = st.text_input("Número de Póliza")

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombres || ' ' || apellidos AS nombre_completo FROM clients")
            clientes = cursor.fetchall()
            cursor.execute("SELECT id, username FROM users")
            usuarios = cursor.fetchall()
            cursor.execute("SELECT id, razon_social FROM aseguradoras")
            aseguradoras = cursor.fetchall()
            cursor.execute("SELECT id, nombre FROM ramos_seguros")
            ramos_seguros = cursor.fetchall()
            # Obtener ejecutivos comerciales (asegúrate de que este campo existe en la base de datos)
            cursor.execute("SELECT id, username FROM users WHERE lower(role) IN ('ejecutivo comercial', 'ejecutivo_comercial', 'ejecutivocomercial', 'seller')")
            ejecutivos_comerciales = cursor.fetchall()
            conn.close()

            cliente_seleccionado = st.selectbox("Selecciona un Cliente", clientes, format_func=lambda x: x[1], key="cliente_poliza")
            usuario_seleccionado = st.selectbox("Selecciona un Gestor", usuarios, format_func=lambda x: x[1], key="gestor_poliza")
            aseguradora_seleccionada = st.selectbox("Selecciona una Aseguradora", aseguradoras, format_func=lambda x: x[1], key="aseguradora_poliza")
            ramo_seleccionado = st.selectbox("Selecciona un Ramo de Seguros", ramos_seguros, format_func=lambda x: x[1], key="ramo_poliza")
            ejecutivo_comercial_seleccionado = st.selectbox(
                "Selecciona un Ejecutivo Comercial",
                ejecutivos_comerciales,
                format_func=lambda x: x[1],
                key="ejecutivo_comercial_poliza"
            )
            tipo_poliza = st.selectbox("Tipo de Póliza", ["Nueva", "Renovación"], key="tipo_poliza")
            cobertura = st.text_area("Cobertura", key="cobertura_poliza")
            prima = st.text_input("Prima", key="prima_poliza")
            fecha_inicio_vigencia = st.date_input("Fecha de Inicio Vigencia", key="fecha_inicio_poliza")
            fecha_fin_vigencia = st.date_input("Fecha de Fin Vigencia", key="fecha_fin_poliza")
            estado = st.selectbox("Estado", ["Activa", "Inactiva", "Cancelada"], key="estado_poliza")
            fecha_emision = st.date_input("Fecha de emisión", key="fecha_emision_poliza")
            linea_negocio = st.text_input("Línea de negocio", key="linea_negocio_poliza")
            suma_asegurada = st.text_input("Suma Asegurada", key="suma_asegurada_poliza")
            deducible = st.text_input("Deducible", key="deducible_poliza")
            sucursal = st.text_input("Sucursal", key="sucursal_poliza")
            tipo_facturacion = st.selectbox("Tipo de Facturación", ["Contado", "Débito", "Cuota Directa"], key="tipo_facturacion_poliza")
            numero_factura = st.text_input("Nº de factura", key="numero_factura_poliza")
            numero_anexo = st.text_area("Nº de Anexo (puedes ingresar varios separados por coma o salto de línea)", key="numero_anexo_poliza")
            tipo_anexo = st.text_input("Tipo de anexo", key="tipo_anexo_poliza")

            if st.button("Crear Póliza", key="crear_poliza_btn"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                existing_columns = [row[1] for row in cursor.execute("PRAGMA table_info(polizas)").fetchall()]
                if "ejecutivo_comercial_id" not in existing_columns:
                    cursor.execute("ALTER TABLE polizas ADD COLUMN ejecutivo_comercial_id INTEGER")
                try:
                    cursor.execute("""
                        INSERT INTO polizas (
                            numero_poliza, cliente_id, usuario_id, aseguradora_id, ramo_id, tipo_poliza, cobertura, prima,
                            fecha_inicio, fecha_fin, estado, fecha_emision, suma_asegurada, deducible, sucursal,
                            tipo_facturacion, linea_negocio, numero_factura, numero_anexo, tipo_anexo, ejecutivo_comercial_id
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        numero_poliza,
                        cliente_seleccionado[0],
                        usuario_seleccionado[0],
                        aseguradora_seleccionada[0],
                        ramo_seleccionado[0],
                        tipo_poliza,
                        cobertura,
                        prima,
                        fecha_inicio_vigencia.strftime("%Y-%m-%d"),
                        fecha_fin_vigencia.strftime("%Y-%m-%d"),
                        estado,
                        fecha_emision.strftime("%Y-%m-%d"),
                        suma_asegurada,
                        deducible,
                        sucursal,
                        tipo_facturacion,
                        linea_negocio,
                        numero_factura,
                        numero_anexo,
                        tipo_anexo,
                        ejecutivo_comercial_seleccionado[0] if ejecutivo_comercial_seleccionado else None
                    ))
                    conn.commit()
                    st.success("Póliza creada exitosamente")
                    st.experimental_rerun()
                except sqlite3.IntegrityError:
                    st.error("El número de póliza ya existe o los datos seleccionados no son válidos.")
                finally:
                    conn.close()

        elif operation == "Leer":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.numero_poliza, c.nombres || ' ' || c.apellidos AS cliente, 
                       u.username AS usuario, p.tipo_poliza, p.cobertura, p.prima, 
                       p.fecha_inicio, p.fecha_fin, p.estado, 
                       (SELECT username FROM users WHERE id = p.ejecutivo_comercial_id) AS ejecutivo_comercial
                FROM polizas p
                JOIN clients c ON p.cliente_id = c.id
                JOIN users u ON p.usuario_id = u.id
            """)
            polizas = cursor.fetchall()
            conn.close()

            if polizas:
                st.write([{
                    "ID": poliza[0],
                    "Número de Póliza": poliza[1],
                    "Cliente": poliza[2],
                    "Usuario": poliza[3],
                    "Tipo de Póliza": poliza[4],
                    "Cobertura": poliza[5],
                    "Prima": poliza[6],
                    "Fecha de Inicio": poliza[7],
                    "Fecha de Fin": poliza[8],
                    "Estado": poliza[9],
                    "Ejecutivo Comercial": poliza[10]
                } for poliza in polizas])
            else:
                st.info("No hay pólizas registradas.")

        elif operation == "Modificar":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, numero_poliza FROM polizas")
            polizas = cursor.fetchall()
            cursor.execute("SELECT id, username FROM users")
            usuarios = cursor.fetchall()
            cursor.execute("SELECT id, username FROM users WHERE lower(role) IN ('ejecutivo comercial', 'ejecutivo_comercial', 'ejecutivocomercial', 'seller')")
            ejecutivos_comerciales = cursor.fetchall()
            conn.close()

            selected_poliza = st.selectbox("Selecciona una póliza", polizas, format_func=lambda x: x[1])
            if selected_poliza:
                # Obtener datos actuales de la póliza
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM polizas WHERE id=?", (selected_poliza[0],))
                poliza_data = cursor.fetchone()
                conn.close()
                if not poliza_data:
                    st.error("No se encontró la póliza seleccionada.")
                    return

                numero_poliza = st.text_input("Número de Póliza", value=poliza_data[1])
                tipo_poliza = st.text_input("Tipo de Póliza", value=poliza_data[4])
                cobertura = st.text_area("Cobertura", value=poliza_data[5])
                prima = st.text_input("Prima", value=poliza_data[6])
                fecha_inicio = st.date_input("Fecha de Inicio", value=poliza_data[7])
                fecha_fin = st.date_input("Fecha de Fin", value=poliza_data[8])
                estado = st.selectbox("Estado", ["Activa", "Inactiva", "Cancelada"], index=["Activa", "Inactiva", "Cancelada"].index(poliza_data[9]))
                usuario_seleccionado = st.selectbox("Selecciona un Usuario", usuarios, format_func=lambda x: x[1], index=next((i for i, u in enumerate(usuarios) if u[0] == poliza_data[3]), 0))
                ejecutivo_comercial_seleccionado = st.selectbox("Ejecutivo Comercial", ejecutivos_comerciales, format_func=lambda x: x[1], index=next((i for i, e in enumerate(ejecutivos_comerciales) if e[0] == poliza_data[10]), 0) if poliza_data[10] else 0)

                if st.button("Actualizar Póliza"):
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            UPDATE polizas
                            SET numero_poliza = ?, tipo_poliza = ?, cobertura = ?, prima = ?, fecha_inicio = ?, fecha_fin = ?, estado = ?, usuario_id = ?, ejecutivo_comercial_id = ?
                            WHERE id = ?
                        """, (
                            numero_poliza, tipo_poliza, cobertura, prima, fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d"), estado, usuario_seleccionado[0], ejecutivo_comercial_seleccionado[0], selected_poliza[0]
                        ))
                        conn.commit()
                        st.success("Póliza actualizada exitosamente")
                    except sqlite3.IntegrityError:
                        st.error("Error al actualizar la póliza.")
                    finally:
                        conn.close()

        elif operation == "Borrar":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, numero_poliza FROM polizas")
            polizas = cursor.fetchall()
            conn.close()

            selected_poliza = st.selectbox("Selecciona una póliza para eliminar", polizas, format_func=lambda x: x[1])

            if st.button("Eliminar Póliza"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM polizas WHERE id = ?", (selected_poliza[0],))
                    conn.commit()
                    st.success("Póliza eliminada exitosamente")
                except sqlite3.IntegrityError:
                    st.error("Error al eliminar la póliza.")
                finally:
                    conn.close()

    elif module == "Agrupadores":  # Replace "Empresas" with "Agrupadores"
        st.subheader("Gestión de Agrupadores")  # Update header
        operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

        if operation == "Crear":
            with st.form("crear_agrupador"):  # Wrap fields in a form
                name = st.text_input("Nombre del Agrupador")  # Update label
                address = st.text_area("Dirección")
                phone = st.text_input("Teléfono")
                email = st.text_input("Correo Electrónico")
                submit_button = st.form_submit_button("Crear Agrupador")  # Add submit button
                if submit_button:  # Check if the form is submitted
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            INSERT INTO companies (name, address, phone, email)
                            VALUES (?, ?, ?, ?)
                        """, (name, address, phone, email))
                        conn.commit()
                        st.success("Agrupador creado exitosamente")  # Update success message
                    except sqlite3.IntegrityError:
                        st.error("El nombre del agrupador ya existe.")  # Update error message
                    finally:
                        conn.close()

        elif operation == "Leer":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, address, phone, email FROM companies")
            columns = [col[0] for col in cursor.description]
            agrupadores = [dict(zip(columns, row)) for row in cursor.fetchall()]
            conn.close()
            if agrupadores:
                st.write([agrupador for agrupador in agrupadores])
            else:
                st.info("No hay agrupadores registrados.")

        elif operation == "Modificar":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM companies")
            agrupadores = cursor.fetchall()  # Update variable name
            conn.close()
            selected_agrupador = st.selectbox("Selecciona un agrupador", agrupadores, format_func=lambda x: x[1])
            if selected_agrupador:
                name = st.text_input("Nombre del Agrupador", value=selected_agrupador[1])  # Update label
                address = st.text_area("Dirección")
                phone = st.text_input("Teléfono")
                email = st.text_input("Correo Electrónico")
                if st.button("Actualizar Agrupador"):  # Update button text
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            UPDATE companies
                            SET name = ?, address = ?, phone = ?, email = ?
                            WHERE id = ?
                        """, (name, address, phone, email, selected_agrupador[0]))
                        conn.commit()
                        st.success("Agrupador actualizado exitosamente")  # Update success message
                    except sqlite3.IntegrityError:
                        st.error("Error al actualizar el agrupador.")  # Update error message
                    finally:
                        conn.close()

        elif operation == "Borrar":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM companies")
            agrupadores = cursor.fetchall()  # Update variable name
            conn.close()
            selected_agrupador = st.selectbox("Selecciona un agrupador para eliminar", agrupadores, format_func=lambda x: x[1])
            if st.button("Eliminar Agrupador"):  # Update button text
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM companies WHERE id = ?", (selected_agrupador[0],))
                    conn.commit()
                    st.success("Agrupador eliminado exitosamente")  # Update success message
                except sqlite3.IntegrityError:
                    st.error("No se puede eliminar el agrupador asignado a usuarios.")  # Update error message
                finally:
                    conn.close()

    elif module == "Aseguradoras":
        st.subheader("Gestión de Aseguradoras")
        action = st.selectbox("Seleccione una acción", ["Crear", "Leer", "Actualizar", "Eliminar"])

        if action == "Crear":
            with st.form("crear_aseguradora"):  # Wrap fields in a form
                tipo_contribuyente = st.text_input("Tipo de Contribuyente")
                tipo_identificacion = st.text_input("Tipo de Identificación")
                identificacion = st.text_input("Identificación")
                razon_social = st.text_input("Razón Social")
                nombre_comercial = st.text_input("Nombre Comercial")
                pais = st.text_input("País")
                representante_legal = st.text_input("Representante Legal")
                aniversario = st.date_input("Aniversario").strftime("%Y-%m-%d")
                web = st.text_input("Web")
                correo_electronico = st.text_input("Correo Electrónico")
                
                # Fetch available Ramos de Seguros
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre FROM ramos_seguros")
                ramos = cursor.fetchall()
                conn.close()
                
                ramo_ids = [ramo[0] for ramo in st.multiselect("Seleccione Ramos de Seguros", ramos, format_func=lambda x: x[1])]
                
                submit_button = st.form_submit_button("Crear Aseguradora")  # Add submit button
                if submit_button:  # Check if the form is submitted
                    aseguradora_data = (
                        tipo_contribuyente,
                        tipo_identificacion,
                        identificacion,
                        razon_social,
                        nombre_comercial,
                        pais,
                        representante_legal,
                        aniversario,
                        web,
                        correo_electronico
                    )
                    result = create_aseguradora(aseguradora_data, ramo_ids)  # Pass data and ramo_ids as separate arguments
                    st.success(result) if "exitosamente" in result else st.error(result)

        elif action == "Leer":
            aseguradoras = read_aseguradoras()
            if aseguradoras:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                data = []
                for aseguradora in aseguradoras:
                    cursor.execute("""
                        SELECT rs.nombre 
                        FROM ramos_seguros rs
                        JOIN aseguradora_ramos ar ON rs.id = ar.ramo_id
                        WHERE ar.aseguradora_id = ?
                    """, (aseguradora[0],))
                    ramos = [ramo[0] for ramo in cursor.fetchall()]
                    data.append({
                        "ID": aseguradora[0],
                        "Tipo de Contribuyente": aseguradora[1],
                        "Tipo de Identificación": aseguradora[2],
                        "Identificación": aseguradora[3],
                        "Razón Social": aseguradora[4],
                        "Nombre Comercial": aseguradora[5],
                        "País": aseguradora[6],
                        "Representante Legal": aseguradora[7],
                        "Aniversario": aseguradora[8],
                        "Web": aseguradora[9],
                        "Correo Electrónico": aseguradora[10],
                        "Ramos de Seguros": ", ".join(ramos)
                    })
                conn.close()
                st.dataframe(data)  # Display data as a Streamlit dataframe
            else:
                st.info("No hay aseguradoras registradas.")

        elif action == "Actualizar":
            aseguradoras = read_aseguradoras()
            if aseguradoras:
                aseguradora_names = {aseguradora[4]: aseguradora[0] for aseguradora in aseguradoras}  # Map name to ID
                selected_name = st.selectbox("Seleccione una aseguradora", list(aseguradora_names.keys()))
                selected_id = aseguradora_names[selected_name]
                aseguradora = next(a for a in aseguradoras if a[0] == selected_id)
                with st.form("actualizar_aseguradora"):  # Wrap fields in a form
                    tipo_contribuyente = st.text_input("Tipo de Contribuyente", value=aseguradora[1])
                    tipo_identificacion = st.text_input("Tipo de Identificación", value=aseguradora[2])
                    identificacion = st.text_input("Identificación", value=aseguradora[3])
                    razon_social = st.text_input("Razón Social", value=aseguradora[4])
                    nombre_comercial = st.text_input("Nombre Comercial", value=aseguradora[5])
                    pais = st.text_input("País", value=aseguradora[6])
                    representante_legal = st.text_input("Representante Legal", value=aseguradora[7])
                    aniversario = st.date_input(
                        "Aniversario", 
                        value=aseguradora[8] if aseguradora[8] else None  # Use raw string for date
                    )
                    web = st.text_input("Web", value=aseguradora[9])
                    correo_electronico = st.text_input("Correo Electrónico", value=aseguradora[10])
                    
                    # Fetch available Ramos de Seguros
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, nombre FROM ramos_seguros")
                    ramos = cursor.fetchall()
                    
                    # Fetch currently associated Ramos de Seguros
                    cursor.execute("""
                        SELECT ramo_id 
                        FROM aseguradora_ramos 
                        WHERE aseguradora_id = ?
                    """, (selected_id,))
                    current_ramo_ids = [row[0] for row in cursor.fetchall()]
                    conn.close()
                    
                    ramo_ids = [ramo[0] for ramo in st.multiselect(
                        "Seleccione Ramos de Seguros", 
                        ramos, 
                        default=[r for r in ramos if r[0] in current_ramo_ids],
                        format_func=lambda x: x[1]
                    )]
                    
                    submit_button = st.form_submit_button("Actualizar Aseguradora")  # Add submit button
                    if submit_button:  # Check if the form is submitted
                        result = update_aseguradora(selected_id, (
                            tipo_contribuyente, tipo_identificacion, identificacion, razon_social,
                            nombre_comercial, pais, representante_legal, aniversario.strftime("%Y-%m-%d") if aniversario else None,
                            web, correo_electronico
                        ), ramo_ids)  # Pass ramo_ids as an argument
                        st.success(result) if "exitosamente" in result else st.error(result)
            else:
                st.info("No hay aseguradoras registradas.")

        elif action == "Eliminar":
            aseguradoras = read_aseguradoras()
            if aseguradoras:
                aseguradora_names = {aseguradora[4]: aseguradora[0] for aseguradora in aseguradoras}  # Map name to ID
                selected_name = st.selectbox("Seleccione una aseguradora para eliminar", list(aseguradora_names.keys()))
                if st.button("Eliminar"):
                    selected_id = aseguradora_names[selected_name]
                    result = delete_aseguradora(selected_id)
                    st.success(result) if "exitosamente" in result else st.error(result)
            else:
                st.info("No hay aseguradoras registradas.")

    elif module == "Ramos de Seguros":
        st.subheader("Gestión de Ramos de Seguros")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Selector for CRUD operations
        action = st.selectbox("Seleccione una acción para Ramos de Seguros", ["Crear", "Leer", "Actualizar", "Eliminar"])

        if action == "Crear":
            st.subheader("Agregar Ramo de Seguro")
            with st.form("add_ramo_seguro"):
                nombre = st.text_input("Nombre")
                descripcion = st.text_area("Descripción")
                if st.form_submit_button("Agregar"):
                    try:
                        cursor.execute("INSERT INTO ramos_seguros (nombre, descripcion) VALUES (?, ?)",
                                       (nombre, descripcion))
                        conn.commit()
                        st.success("Ramo de Seguro agregado exitosamente.")
                    except sqlite3.IntegrityError:
                        st.error("El nombre del ramo de seguro ya existe.")

        elif action == "Leer":
            st.subheader("Lista de Ramos de Seguros")
            cursor.execute("SELECT id, nombre, descripcion FROM ramos_seguros")
            ramos = cursor.fetchall()
            if ramos:
                # Convert the data into a list for better formatting
                st.write([{
                    "ID": ramo[0],
                    "Nombre": ramo[1],
                    "Descripción": ramo[2]
                } for ramo in ramos])
            else:
                st.info("No hay ramos de seguros registrados.")

        elif action == "Actualizar":
            st.subheader("Actualizar Ramo de Seguro")
            cursor.execute("SELECT id, nombre FROM ramos_seguros")
            ramos = cursor.fetchall()
            selected_ramo = st.selectbox("Selecciona un Ramo de Seguro", ramos, format_func=lambda x: x[1])

            if selected_ramo:
                new_nombre = st.text_input("Nuevo Nombre", value=selected_ramo[1])
                cursor.execute("SELECT descripcion FROM ramos_seguros WHERE id=?", (selected_ramo[0],))
                current_descripcion = cursor.fetchone()[0]
                new_descripcion = st.text_area("Nueva Descripción", value=current_descripcion)

                if st.button("Actualizar"):
                    cursor.execute("UPDATE ramos_seguros SET nombre=?, descripcion=? WHERE id=?",
                                   (new_nombre, new_descripcion, selected_ramo[0]))
                    conn.commit()
                    st.success("Ramo de Seguro actualizado exitosamente.")

        elif action == "Eliminar":
            st.subheader("Eliminar Ramo de Seguro")
            cursor.execute("SELECT id, nombre FROM ramos_seguros")
            ramos = cursor.fetchall()
            selected_ramo = st.selectbox("Selecciona un Ramo de Seguro para eliminar", ramos, format_func=lambda x: x[1])

            if selected_ramo:
                if st.button("Eliminar"):
                    cursor.execute("DELETE FROM ramos_seguros WHERE id=?", (selected_ramo[0],))
                    conn.commit()
                    st.success("Ramo de Seguro eliminado exitosamente.")

        conn.close()

    # Botón de Logout
    if st.sidebar.button("Logout"):
        del st.session_state["token"]  # Eliminar el token de la sesión
        st.success("Sesión cerrada exitosamente")
        st.rerun()  # Recargar la página para volver al login
