import streamlit as st
import sqlite3
from dbconfig import DB_FILE
from user_crud import create_user, read_users, update_user, delete_user
from client_crud import create_client, read_clients, update_client, delete_client
from create_dashboard import create_dashboard

def initialize_database():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_cliente TEXT,
                nombres TEXT,
                apellidos TEXT,
                razon_social TEXT,
                tipo_documento TEXT,
                numero_documento TEXT,
                fecha_nacimiento TEXT,
                nacionalidad TEXT,
                sexo TEXT,
                estado_civil TEXT,
                correo_electronico TEXT,
                telefono_movil TEXT,
                telefono_fijo TEXT,
                direccion_domicilio TEXT,
                provincia TEXT,
                ciudad TEXT,
                codigo_postal TEXT,
                ocupacion_profesion TEXT,
                empresa_trabajo TEXT,
                tipo_empresa TEXT,
                ingresos_mensuales TEXT,
                nivel_educacion TEXT,
                fumador TEXT,
                actividades_riesgo TEXT,
                historial_medico TEXT,
                historial_siniestros TEXT,
                vehiculos_registrados TEXT,
                propiedades TEXT,
                tipo_contribuyente TEXT,
                numero_ruc TEXT,
                representante_legal_id INTEGER,
                observaciones_legales TEXT,
                canal_preferido_contacto TEXT,
                notas_adicionales TEXT,
                fecha_registro TEXT,
                ultima_actualizacion TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS role_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_name TEXT NOT NULL,
                action TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS polizas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_poliza TEXT UNIQUE NOT NULL,
                cliente_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                tipo_poliza TEXT NOT NULL,
                cobertura TEXT,
                prima TEXT,
                fecha_inicio TEXT NOT NULL,
                fecha_fin TEXT NOT NULL,
                estado TEXT NOT NULL
            )
        ''')
        # Add missing columns if they don't exist
        existing_columns = [row[1] for row in cursor.execute("PRAGMA table_info(users)").fetchall()]
        required_columns = {
            "correo": "TEXT",
            "nombres": "TEXT",
            "apellidos": "TEXT",
            "telefono": "TEXT",
            "fecha_registro": "TEXT",
            "ultima_actualizacion": "TEXT"
        }
        for column, column_type in required_columns.items():
            if column not in existing_columns:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {column} {column_type}")
        conn.commit()
    except Exception as e:
        st.error(f"Error al inicializar la base de datos: {e}")
    finally:
        conn.close()

initialize_database()

def admin_dashboard():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo.png", width=100)
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
        7. **Logout**: Cierra sesión.
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

    if "module" not in st.session_state:
        st.session_state["module"] = None

    st.sidebar.title("Navegación")
    st.sidebar.image("logo.png", width=80)
    if st.sidebar.button("Usuarios"):
        st.session_state["module"] = "Usuarios"
    if st.sidebar.button("Clientes"):
        st.session_state["module"] = "Clientes"
    if st.sidebar.button("Roles"):
        st.session_state["module"] = "Roles"
    if st.sidebar.button("Pólizas"):
        st.session_state["module"] = "Pólizas"
    
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

            if st.button("Crear Usuario"):
                if username and password and correo and nombres and apellidos and telefono and role:
                    result = create_user(
                        username=username,
                        password=password,
                        role=role,
                        correo=correo,
                        nombres=nombres,
                        apellidos=apellidos,
                        telefono=telefono,
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

                    if st.button("Actualizar Usuario"):
                        if username and correo and nombres and apellidos and telefono and role:
                            result = update_user(
                                username=username,
                                password=new_password if new_password else user_data[2],
                                role=role,
                                correo=correo,
                                nombres=nombres,
                                apellidos=apellidos,
                                telefono=telefono,
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
            tipo_documento = st.selectbox("Tipo de Documento", ["DNI", "Pasaporte", "RUC"])
            numero_documento = st.text_input("Número de Documento")
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
            numero_ruc = st.text_input("Número RUC")
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
                        numero_ruc=numero_ruc,
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
                # Mostrar todos los campos de los clientes con barra horizontal
                st.dataframe(clients, use_container_width=True)
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

            # Obtener lista de clientes
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombres || ' ' || apellidos AS nombre_completo FROM clients")
            clientes = cursor.fetchall()
            cursor.execute("SELECT id, username FROM users")
            usuarios = cursor.fetchall()
            conn.close()

            cliente_seleccionado = st.selectbox("Selecciona un Cliente", clientes, format_func=lambda x: x[1])
            usuario_seleccionado = st.selectbox("Selecciona un Usuario", usuarios, format_func=lambda x: x[1])

            tipo_poliza = st.text_input("Tipo de Póliza")
            cobertura = st.text_area("Cobertura")
            prima = st.text_input("Prima")
            fecha_inicio = st.date_input("Fecha de Inicio")
            fecha_fin = st.date_input("Fecha de Fin")
            estado = st.selectbox("Estado", ["Activa", "Inactiva", "Cancelada"])

            if st.button("Crear Póliza"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO polizas (numero_poliza, cliente_id, usuario_id, tipo_poliza, cobertura, prima, fecha_inicio, fecha_fin, estado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (numero_poliza, cliente_seleccionado[0], usuario_seleccionado[0], tipo_poliza, cobertura, prima, fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d"), estado))
                    conn.commit()
                    st.success("Póliza creada exitosamente")
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
                       p.fecha_inicio, p.fecha_fin, p.estado
                FROM polizas p
                JOIN clients c ON p.cliente_id = c.id
                JOIN users u ON p.usuario_id = u.id
            """)
            polizas = cursor.fetchall()
            conn.close()

            if polizas:
                # Convertir los resultados en un DataFrame para una mejor visualización
                import pandas as pd
                df = pd.DataFrame(polizas, columns=[
                    "ID", "Número de Póliza", "Cliente", "Usuario", "Tipo de Póliza", 
                    "Cobertura", "Prima", "Fecha de Inicio", "Fecha de Fin", "Estado"
                ])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No hay pólizas registradas.")

        elif operation == "Modificar":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, numero_poliza FROM polizas")
            polizas = cursor.fetchall()
            conn.close()

            selected_poliza = st.selectbox("Selecciona una póliza", polizas, format_func=lambda x: x[1])
            if selected_poliza:
                numero_poliza = st.text_input("Número de Póliza", value=selected_poliza[1])
                tipo_poliza = st.text_input("Tipo de Póliza")
                cobertura = st.text_area("Cobertura")
                prima = st.text_input("Prima")
                fecha_inicio = st.date_input("Fecha de Inicio")
                fecha_fin = st.date_input("Fecha de Fin")
                estado = st.selectbox("Estado", ["Activa", "Inactiva", "Cancelada"])

                if st.button("Actualizar Póliza"):
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            UPDATE polizas
                            SET numero_poliza = ?, tipo_poliza = ?, cobertura = ?, prima = ?, fecha_inicio = ?, fecha_fin = ?, estado = ?
                            WHERE id = ?
                        """, (numero_poliza, tipo_poliza, cobertura, prima, fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d"), estado, selected_poliza[0]))
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

    # Botón de Logout
    if st.sidebar.button("Logout"):
        del st.session_state["token"]  # Eliminar el token de la sesión
        st.success("Sesión cerrada exitosamente")
        st.rerun()  # Recargar la página para volver al login