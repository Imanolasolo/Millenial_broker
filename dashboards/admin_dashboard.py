import streamlit as st
import sqlite3
from dbconfig import DB_FILE
from crud.user_crud import create_user, read_users, update_user, delete_user, get_user_details
from crud.client_crud import create_client, read_clients, update_client, delete_client
from create_dashboard import create_dashboard
from crud.aseguradora_crud import create_aseguradora, read_aseguradoras, update_aseguradora, delete_aseguradora
import fitz  # PyMuPDF
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI 
from htmlTemplates import css, bot_template, user_template
import os
import datetime as dt
import re

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
                ultima_actualizacion TEXT,
                correo_empresa TEXT,
                sector_mercado TEXT,
                tipo_empresa_categoria TEXT,
                tipo_persona_juridica TEXT,
                subactividad_economica TEXT,
                pagina_web TEXT,
                fecha_aniversario TEXT,
                contacto_autorizado_id TEXT
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
                role TEXT NOT NULL,
                company_id INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS polizas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_poliza TEXT UNIQUE NOT NULL,
                cliente_id INTEGER NOT NULL,
                usuario_id INTEGER NOT NULL,
                aseguradora_id INTEGER NOT NULL,
                ramo_id INTEGER NOT NULL,
                tipo_poliza TEXT NOT NULL,
                cobertura TEXT,
                prima TEXT,
                fecha_inicio TEXT NOT NULL,
                fecha_fin TEXT NOT NULL,
                estado TEXT NOT NULL,
                fecha_emision TEXT,
                suma_asegurada TEXT,
                deducible TEXT,
                sucursal TEXT,
                tipo_facturacion TEXT,
                linea_negocio TEXT,
                numero_factura TEXT,
                numero_anexo TEXT,
                tipo_anexo TEXT,
                ejecutivo_comercial_id INTEGER
            )
        ''')
        existing_columns = [row[1] for row in cursor.execute("PRAGMA table_info(polizas)").fetchall()]
        if "fecha_emision" not in existing_columns:
            cursor.execute("ALTER TABLE polizas ADD COLUMN fecha_emision TEXT")
        if "suma_asegurada" not in existing_columns:
            cursor.execute("ALTER TABLE polizas ADD COLUMN suma_asegurada TEXT")
        if "deducible" not in existing_columns:
            cursor.execute("ALTER TABLE polizas ADD COLUMN deducible TEXT")
        if "sucursal" not in existing_columns:
            cursor.execute("ALTER TABLE polizas ADD COLUMN sucursal TEXT")
        if "tipo_facturacion" not in existing_columns:
            cursor.execute("ALTER TABLE polizas ADD COLUMN tipo_facturacion TEXT")
        if "aseguradora_id" not in existing_columns:
            cursor.execute("ALTER TABLE polizas ADD COLUMN aseguradora_id INTEGER")
        if "ramo_id" not in existing_columns:
            cursor.execute("ALTER TABLE polizas ADD COLUMN ramo_id INTEGER")
        if "linea_negocio" not in existing_columns:
            cursor.execute("ALTER TABLE polizas ADD COLUMN linea_negocio TEXT")
        if "numero_factura" not in existing_columns:
            cursor.execute("ALTER TABLE polizas ADD COLUMN numero_factura TEXT")
        if "numero_anexo" not in existing_columns:
            cursor.execute("ALTER TABLE polizas ADD COLUMN numero_anexo TEXT")
        if "tipo_anexo" not in existing_columns:
            cursor.execute("ALTER TABLE polizas ADD COLUMN tipo_anexo TEXT")
        if "ejecutivo_comercial_id" not in existing_columns:
            cursor.execute("ALTER TABLE polizas ADD COLUMN ejecutivo_comercial_id INTEGER")
        conn.commit()
    except Exception as e:
        st.error(f"Error al inicializar la base de datos: {e}")
    finally:
        conn.close()

initialize_database()

def get_pdf_text(pdf_list):
    text = ""
    for pdf_path in pdf_list:
        pdf_document = fitz.open(pdf_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
    return text

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    if not text_chunks:
        st.warning("Please upload the textual PDF file - this is PDF files of image")
        return None
    embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["OPEN_AI_APIKEY"])
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vector_store):
    llm = ChatOpenAI(openai_api_key=st.secrets["OPEN_AI_APIKEY"])
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory=memory
    )
    return conversation_chain

def handle_userInput(user_question):
    response = st.session_state.conversation({'question': user_question})
    # Solo mostrar la última respuesta del bot
    bot_reply = response['chat_history'][-1].content if response['chat_history'] else ""
    st.write(bot_template.replace("{{MSG}}", bot_reply), unsafe_allow_html=True)
    # No guardar ni mostrar el historial completo

if "conversation" not in st.session_state:
        st.session_state.conversation = None
if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

if "pdf_text" not in st.session_state:
        st.session_state.pdf_text = ""

sample_pdf_path = os.path.join(os.getcwd(), "Base_conocimiento_proceso_admin.pdf")
st.session_state.pdf_files = [sample_pdf_path]

raw_text = get_pdf_text(st.session_state.pdf_files)
st.session_state.pdf_text = raw_text
text_chunks = get_text_chunks(raw_text)
vector_store = get_vector_store(text_chunks)
st.session_state.conversation = get_conversation_chain(vector_store)

def admin_dashboard():
    # Retrieve username from session state
    username = st.session_state.get("username")
    user_details = get_user_details(username) if username else None

    # Display header with avatar, name, and group
    st.sidebar.image("assets/avatar.png", width=100)  # Replace with the path to your avatar image
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
    col1, col2 = st.columns([2, 2])

    with col1:
        with st.expander("Instrucciones Básicas"):
            st.markdown("""
            ### Cómo usar el Dashboard:        
            1. **Usuarios**: Gestiona los usuarios del sistema (crear, leer, modificar, borrar).
            2. **Clientes**: Administra la información de los clientes.
            3. **Reportes**: Genera y visualiza reportes.
            4. **Configuración**: Ajusta el sistema.
            5. **Roles**: Gestiona los roles disponibles.
            6. **Pólizas**: Gestiona las pólizas de seguro.
            7. **Agencias**: Gestiona las agencias.
            8. **Aseguradoras**: Gestiona las aseguradoras.
            9. **Ramos de Seguros**: Gestiona los ramos de seguros.
            10. **Logout**: Cierra sesión.
            """)
    with col2:
        with st.expander(" Guia de proceso IA"):
                st.write("Pregunta a nuestro chat acerca de como manejar este panel de administracion y sus módulos")
                
                user_question = st.text_input(label="", placeholder="Dinos quien eres y te podremos ayudar mejor...")
                if user_question:
                    handle_userInput(user_question)

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
        /* El selector siguiente NO funciona porque Streamlit no asigna el id del key al input HTML */
        /* cliente_nombres input { width:22px !important;} */
        </style>
    """, unsafe_allow_html=True)

    if "module" not in st.session_state:
        st.session_state["module"] = None

    st.sidebar.title("Navegación")
    st.sidebar.image("assets/logo.png", width=80)

    # Selector "Actores del BCS"
    actores = [
        ("Usuarios", "Usuarios"),
        ("Clientes", "Clientes"),
        ("Roles", "Roles"),
        ("Agencias", "Agencias"),
        ("Aseguradoras", "Aseguradoras"),
    ]
    selected_actor = st.sidebar.selectbox(
        "Actores del BCS",
        [a[0] for a in actores],
        index=None,
        key="actores_bcs_selectbox",
        placeholder="Selecciona un módulo"
    )
    if selected_actor:
        st.session_state["module"] = dict(actores)[selected_actor]

    # Selector "Producción"
    produccion_modulos = [
        ("Pólizas", "Pólizas"),
        ("Ramos de Seguros", "Ramos de Seguros"),
    ]
    selected_produccion = st.sidebar.selectbox(
        "Producción",
        [p[0] for p in produccion_modulos],
        index=None,
        key="produccion_selectbox",
        placeholder="Selecciona un módulo"
    )
    if selected_produccion:
        st.session_state["module"] = dict(produccion_modulos)[selected_produccion]

    module = st.session_state["module"]

    if module == "Usuarios":
        st.subheader("Gestión de Usuarios")
        operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

        if operation == "Crear":
            import sqlite3  # <-- Asegura que sqlite3 esté importado en este scope
            from dbconfig import DB_FILE  # <-- Asegura que DB_FILE esté importado en este scope
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
            import sqlite3  # <-- Asegura que sqlite3 esté importado en este scope
            from dbconfig import DB_FILE  # <-- Asegura que DB_FILE esté importado en este scope
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
            import sqlite3  # <-- Asegura que sqlite3 esté importado en este scope
            from dbconfig import DB_FILE  # <-- Asegura que DB_FILE esté importado en este scope
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
            if tipo_cliente == "Individual":
                with st.form("form_cliente_individual"):
                    # Obtener tipos de documento únicos de la base de datos
                    import sqlite3
                    from dbconfig import DB_FILE
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("SELECT DISTINCT tipo_documento FROM clients WHERE tipo_documento IS NOT NULL AND tipo_documento != ''")
                    tipos_documento_db = [row[0] for row in cursor.fetchall()]
                    conn.close()
                    tipos_documento = tipos_documento_db if tipos_documento_db else ["Cédula", "Pasaporte", "RUC"]

                    col1, col2 = st.columns(2)
                    with col1:
                        nombres = st.text_input("Nombres (máx 50 caracteres)", key="cliente_nombres")
                    with col2:
                        apellidos = st.text_input("Apellidos (máx 50 caracteres)")
                    # Validación de longitud
                    if nombres and len(nombres) > 50:
                        st.error("El campo 'Nombres' no puede exceder 50 caracteres.")
                    if apellidos and len(apellidos) > 50:
                        st.error("El campo 'Apellidos' no puede exceder 50 caracteres.")
                    col1, col2 = st.columns(2)
                    with col1:
                        tipo_documento = st.selectbox("Tipo de Documento", tipos_documento)
                    with col2:
                        numero_documento = st.text_input(f"Número de {tipo_documento}")
                    # Validación para cédula
                    if tipo_documento == "Cédula" and numero_documento and len(numero_documento) != 10:
                        st.error("El número de Cédula debe tener exactamente 10 caracteres.")
                    col1, col2 = st.columns(2)
                    with col1:    
                        fecha_nacimiento = st.date_input(
                            "Fecha de Nacimiento",
                            min_value=dt.date(1900, 1, 1),
                            max_value=dt.date.today()
                        )
                    if fecha_nacimiento > dt.date.today():
                        st.error("La fecha de nacimiento no puede ser mayor que hoy.")
                    with col2:
                        nacionalidad = st.text_input("Nacionalidad")
                    col1, col2 = st.columns(2)
                    with col1:
                        genero = st.selectbox("Género", ["Masculino", "Femenino", "Otro"])
                    with col2:
                        estado_civil = st.selectbox("Estado Civil", ["Soltero", "Casado", "Divorciado", "Viudo"])
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        correo_electronico = st.text_input("Correo Electrónico Contacto")
                    # Validación de email
                    email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
                    if correo_electronico and not re.match(email_pattern, correo_electronico):
                        st.error("El correo electrónico no tiene un formato válido.")
                    with col2:
                        telefono_movil = st.text_input("Teléfono Móvil")
                    with col3:
                        telefono_fijo = st.text_input("Teléfono Fijo")
                    # Validación de formato internacional Ecuador +593XXXXXXXXX
                    phone_pattern = r"^\+593\d{9}$"
                    if telefono_movil and not re.match(phone_pattern, telefono_movil):
                        st.error("El Teléfono Móvil debe tener el formato internacional +593XXXXXXXXX")
                    if telefono_fijo and telefono_fijo.strip() and not re.match(phone_pattern, telefono_fijo):
                        st.error("El Teléfono Fijo debe tener el formato internacional +593XXXXXXXXX")
                    direccion_domicilio = st.text_area("Dirección de Domicilio")
                    col1, col2,col3 = st.columns(3)
                    with col1:
                        provincia = st.text_input("Provincia")
                    with col2:
                        ciudad = st.text_input("Ciudad")
                    with col3:
                        codigo_postal = st.text_input("Código Postal")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        ocupacion_profesional = st.text_input("Ocupación / Profesión")
                    with col2:
                        empresa_trabajo = st.text_input("Empresa donde trabaja")
                    with col3:
                        tipo_empresa = st.selectbox("Tipo de Empresa", ["Pública", "Privada", "Emprendedor"])
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        ingresos_mensuales = st.text_input("Ingresos Mensuales")
                    with col2: 
                        nivel_educacion = st.selectbox("Nivel de Educación", ["Primaria", "Secundaria", "Superior", "Postgrado"])
                    with col3:
                        fumador = st.selectbox("Fumador", ["Sí", "No"])
                    actividades_riesgo = st.text_area("Actividades de Riesgo")
                    historial_medico = st.text_area("Historial Médico")
                    historial_siniestros = st.text_area("Historial de Siniestros")
                    vehiculos_registrados = st.text_area("Vehículos Registrados")
                    propiedades = st.text_area("Propiedades")
                    tipo_contribuyente = st.selectbox("Tipo de Contribuyente", ["Natural", "Jurídica"])
                    numero_ruc = st.text_input("Número de RUC")
                    representante_legal_id = st.text_input("ID del Representante Legal")
                    # Validación: 10 dígitos numéricos
                    if representante_legal_id and (not representante_legal_id.isdigit() or len(representante_legal_id) != 10):
                        st.error("El ID Representante Legal debe tener exactamente 10 dígitos numéricos.")
                    contacto_autorizado_id = st.text_input("ID Contacto Autorizado")
                    # Validación: 10 dígitos numéricos
                    if contacto_autorizado_id and (not contacto_autorizado_id.isdigit() or len(contacto_autorizado_id) != 10):
                        st.error("El ID Contacto Autorizado debe tener exactamente 10 dígitos numéricos.")
                    observaciones_legales = st.text_area("Observaciones Legales")
                    canal_preferido_contacto = st.selectbox("Canal Preferido de Contacto", ["Correo Electrónico", "Teléfono", "WhatsApp"])
                    notas_adicionales = st.text_area("Notas Adicionales")
                    fecha_registro = st.date_input("Fecha de Registro")
                    ultima_actualizacion = st.date_input("Última Actualización")
                    pagina_web = st.text_input("Página web")
                    url_pattern = r"^(https?://)?([\w\-]+\.)+[\w\-]+(/[\w\-./?%&=]*)?$"
                    if pagina_web and not re.match(url_pattern, pagina_web):
                        st.error("La Página web debe tener formato URL válido (ej: https://www.ejemplo.com)")
                    fecha_aniversario = st.date_input("Fecha de Aniversario (opcional)", value=None)

                    submitted = st.form_submit_button("Crear Cliente")
                    if submitted:
                        if (nombres and len(nombres) > 50) or (apellidos and len(apellidos) > 50):
                            st.error("El campo 'Nombres' y/o 'Apellidos' no puede exceder 50 caracteres.")
                        elif tipo_documento == "Cédula" and numero_documento and len(numero_documento) != 10:
                            st.error("El número de Cédula debe tener exactamente 10 caracteres.")
                        elif fecha_nacimiento > dt.date.today():
                            st.error("La fecha de nacimiento no puede ser mayor que hoy.")
                        elif correo_electronico and not re.match(email_pattern, correo_electronico):
                            st.error("El correo electrónico no tiene un formato válido.")
                        elif telefono_movil and not re.match(phone_pattern, telefono_movil):
                            st.error("El Teléfono Móvil debe tener el formato internacional +593XXXXXXXXX")
                        elif telefono_fijo and telefono_fijo.strip() and not re.match(phone_pattern, telefono_fijo):
                            st.error("El Teléfono Fijo debe tener el formato internacional +593XXXXXXXXX")
                        elif pagina_web and not re.match(url_pattern, pagina_web):
                            st.error("La Página web debe tener formato URL válido (ej: https://www.ejemplo.com)")
                        elif nombres and apellidos and numero_documento and correo_electronico:
                            result = create_client(
                                tipo_cliente=tipo_cliente,
                                nombres=nombres,
                                apellidos=apellidos,
                                razon_social=None,
                                tipo_documento=tipo_documento,
                                numero_documento=numero_documento,
                                fecha_nacimiento=fecha_nacimiento.strftime("%Y-%m-%d"),
                                nacionalidad=nacionalidad,
                                sexo=genero,
                                estado_civil=estado_civil,
                                correo_electronico=correo_electronico,
                                telefono_movil=telefono_movil,
                                telefono_fijo=telefono_fijo,
                                direccion_domicilio=direccion_domicilio,
                                provincia=None,
                                ciudad=None,
                                codigo_postal=None,
                                ocupacion_profesion=None,
                                empresa_trabajo=None,
                                tipo_empresa=None,
                                ingresos_mensuales=None,
                                nivel_educacion=None,
                                fumador=None,
                                actividades_riesgo=None,
                                historial_medico=None,
                                historial_siniestros=None,
                                vehiculos_registrados=None,
                                propiedades=None,
                                tipo_contribuyente=None,
                                representante_legal_id=None,
                                observaciones_legales=None,
                                canal_preferido_contacto=None,
                                notas_adicionales=None,
                                fecha_registro=fecha_nacimiento.strftime("%Y-%m-%d"),
                                ultima_actualizacion=fecha_nacimiento.strftime("%Y-%m-%d"),
                                pagina_web=pagina_web,
                                fecha_aniversario=fecha_aniversario.strftime("%Y-%m-%d") if fecha_aniversario else None,
                                contacto_autorizado_id=contacto_autorizado_id
                            )
                            st.success(result) if "exitosamente" in result else st.error(result)
                        else:
                            st.error("Completa todos los campos obligatorios.")
            else:  # Empresa
                with st.form("form_cliente_empresa"):
                    razon_social = st.text_input("Razón Social")
                    tipo_documento = st.selectbox("Tipo de Documento", ["RUC"])
                    numero_documento = st.text_input("Número de RUC")
                    # Validación: RUC exactamente 13 dígitos
                    if numero_documento and len(numero_documento) != 13:
                        st.error("El Número de RUC debe tener exactamente 13 dígitos.")
                    representante_legal_id = st.text_input("ID Representante Legal")
                    # Validación: 10 dígitos numéricos
                    if representante_legal_id and (not representante_legal_id.isdigit() or len(representante_legal_id) != 10):
                        st.error("El ID Representante Legal debe tener exactamente 10 dígitos numéricos.")
                    contacto_autorizado_id = st.text_input("ID Contacto Autorizado")
                    # Validación: 10 dígitos numéricos
                    if contacto_autorizado_id and (not contacto_autorizado_id.isdigit() or len(contacto_autorizado_id) != 10):
                        st.error("El ID Contacto Autorizado debe tener exactamente 10 dígitos numéricos.")
                    correo_electronico = st.text_input("Correo Electrónico Contacto")
                    correo_empresa = st.text_input("Correo Empresa")
                    # Validación de email para ambos campos
                    email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
                    if correo_electronico and not re.match(email_pattern, correo_electronico):
                        st.error("El correo electrónico de contacto no tiene un formato válido.")
                    if correo_empresa and not re.match(email_pattern, correo_empresa):
                        st.error("El correo empresa no tiene un formato válido.")
                    # Sector/Mercado dropdown
                    sector_mercado = st.selectbox(
                        "Sector/Mercado",
                        ["Publico", "Privado", "Mixto", "ONG", "Cooperativo", "Educativo", "Salud"]
                    )
                    # Tipo Empresa dropdown
                    tipo_empresa_categoria = st.selectbox(
                        "Tipo Empresa",
                        ["Microempresa", "Pequeña Empresa", "Mediana Empresa", "Gran Empresa"]
                    )
                    # Tipo Persona Jurídica dropdown
                    tipo_persona_juridica_options = [
                        "SCVS - Sociedad Anónima (S.A.)",
                        "SCVS - Compañía Ltda.",
                        "SCVS - S.A.S. (Sociedad por Acciones Simplificadas)",
                        "SCVS - Sucursal Extranjera",
                        "SCVS - Compañía en Comandita / Colectiva",
                        "SEPS - Cooperativa de Ahorro y Crédito",
                        "SEPS - Asociación",
                        "SEPS - Fundación",
                        "SB - Banco Privado",
                        "SB - Aseguradora",
                        "Otro - Empresa Pública",
                        "Otro - ONG",
                        "Otro - Institución Educativa",
                        "SCVS - S.A.S.",
                        "SCVS - Sucursal Extranjera",
                        "SCVS - Comandita / Colectiva",
                        "SEPS - Cooperativa",
                        "SEPS - Asociación",
                        "SEPS - Fundación",
                        "SB - Banco Privado",
                        "SB - Aseguradora",
                        "Otro - Empresa Pública",
                        "Otro - ONG",
                        "Otro - Institución Educativa"
                    ]
                    tipo_persona_juridica = st.selectbox(
                        "Tipo Persona Jurídica",
                        tipo_persona_juridica_options
                    )
                    # Subactividad Económica
                    subactividad_economica = st.text_input("Subactividad Económica")
                    telefono_fijo = st.text_input("Teléfono Fijo")  # <-- Asegura que este campo esté definido
                    direccion_domicilio = st.text_area("Dirección de la Empresa")
                    tipo_empresa = st.text_input("Tipo de Empresa")
                    ingresos_mensuales = st.text_input("Ingresos Mensuales")
                    observaciones_legales = st.text_area("Observaciones Legales")
                    pagina_web = st.text_input("Página web")
                    url_pattern = r"^(https?://)?([\w\-]+\.)+[\w\-]+(/[\w\-./?%&=]*)?$"
                    if pagina_web and not re.match(url_pattern, pagina_web):
                        st.error("La Página web debe tener formato URL válido (ej: https://www.ejemplo.com)")
                    fecha_aniversario = st.date_input("Fecha de Aniversario (opcional)", value=None)
                    submitted = st.form_submit_button("Crear Cliente")
                    if submitted:
                        if razon_social and numero_documento and correo_electronico:
                            result = create_client(
                                tipo_cliente=tipo_cliente,
                                nombres=None,
                                apellidos=None,
                                razon_social=razon_social,
                                tipo_documento=tipo_documento,
                                numero_documento=numero_documento,
                                fecha_nacimiento=None,
                                nacionalidad=None,
                                sexo=None,
                                estado_civil=None,
                                correo_electronico=correo_electronico,
                                correo_empresa=correo_empresa,
                                sector_mercado=sector_mercado,
                                tipo_empresa_categoria=tipo_empresa_categoria,
                                tipo_persona_juridica=tipo_persona_juridica,
                                subactividad_economica=subactividad_economica,
                                telefono_fijo=telefono_fijo,
                                direccion_domicilio=direccion_domicilio,
                                tipo_empresa=tipo_empresa,
                                ingresos_mensuales=ingresos_mensuales,
                                observaciones_legales=observaciones_legales,
                                pagina_web=pagina_web,
                                fecha_aniversario=fecha_aniversario.strftime("%Y-%m-%d") if fecha_aniversario else None,
                                representante_legal_id=representante_legal_id,
                                contacto_autorizado_id=contacto_autorizado_id
                                # ...otros campos si es necesario...
                            )
                            st.success(result) if "exitosamente" in result else st.error(result)
                        else:
                            st.error("Completa todos los campos obligatorios.")

        elif operation == "Leer":
            st.subheader("Lista de Clientes")
            clients = read_clients()
            if clients:
                # Convertir los datos a un DataFrame de Streamlit
                import pandas as pd
                df = pd.DataFrame(clients)
                st.dataframe(df)  # Mostrar como tabla interactiva
            else:
                st.info("No hay clientes registrados.")

        elif operation == "Modificar":
            st.subheader("Modificar Cliente")
            from dbconfig import DB_FILE
            import sqlite3
            clients = read_clients()
            client_options = []
            for client in clients:
                if client.get("tipo_cliente") == "Empresa":
                    label = f"{client.get('razon_social', '')} (Empresa)"
                else:
                    label = f"{client.get('nombres', '')} {client.get('apellidos', '')} (Individual)"
                client_options.append((client["id"], label))
            selected_client = st.selectbox("Selecciona un cliente", client_options, format_func=lambda x: x[1] if x else "")
            selected_client_id = selected_client[0] if selected_client else None

            if selected_client_id:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM clients WHERE id = ?", (selected_client_id,))
                client_data = cursor.fetchone()
                cursor.execute("PRAGMA table_info(clients)")
                columns = [col[1] for col in cursor.fetchall()]
                conn.close()

                if client_data:
                    client_dict = dict(zip(columns, client_data))
                    tipo_cliente = client_dict.get("tipo_cliente", "Individual")
                    with st.form("form_modificar_cliente"):
                        tipo_cliente_val = st.selectbox("Tipo de Cliente", ["Individual", "Empresa"], index=0 if tipo_cliente == "Individual" else 1, disabled=True)
                        if tipo_cliente == "Empresa":
                            col1, col2 = st.columns(2)
                            with col1:
                                razon_social = st.text_input("Razón Social", value=client_dict.get("razon_social", ""))
                            with col2:
                                nombres = None
                                apellidos = None
                        else:
                            col1, col2 = st.columns(2)
                            with col1:
                                nombres = st.text_input("Nombres", value=client_dict.get("nombres", ""))
                            with col2:
                                apellidos = st.text_input("Apellidos", value=client_dict.get("apellidos", ""))
                            razon_social = None
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            tipo_documento = st.text_input("Tipo de Documento", value=client_dict.get("tipo_documento", ""))
                        with col2:
                            numero_documento = st.text_input("Número de Documento", value=client_dict.get("numero_documento", ""))
                        with col3:
                            fecha_nacimiento = st.date_input(
                                "Fecha de Nacimiento",
                                value=dt.datetime.strptime(client_dict["fecha_nacimiento"], "%Y-%m-%d").date() if client_dict.get("fecha_nacimiento") else dt.date.today()
                            )
                        col1,col2,col3 = st.columns(3)
                        with col1:
                            nacionalidad = st.text_input("Nacionalidad", value=client_dict.get("nacionalidad", ""))
                        with col2:
                            sexo = st.text_input("Sexo", value=client_dict.get("sexo", ""))
                        with col3:
                            estado_civil = st.text_input("Estado Civil", value=client_dict.get("estado_civil", ""))
                        col1, col2 = st.columns(2)
                        with col1:
                            correo_electronico = st.text_input("Correo Electrónico", value=client_dict.get("correo_electronico", ""))
                        with col2:
                            correo_empresa = st.text_input("Correo Empresa", value=client_dict.get("correo_empresa", ""))
                        col1, col2 = st.columns(2)
                        with col1:
                            telefono_movil = st.text_input("Teléfono Móvil", value=client_dict.get("telefono_movil", ""))
                        with col2:
                            telefono_fijo = st.text_input("Teléfono Fijo", value=client_dict.get("telefono_fijo", ""))
                        direccion_domicilio = st.text_area("Dirección Domicilio", value=client_dict.get("direccion_domicilio", ""))
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            provincia = st.text_input("Provincia", value=client_dict.get("provincia", ""))
                        with col2:
                            ciudad = st.text_input("Ciudad", value=client_dict.get("ciudad", ""))
                        with col3:
                            codigo_postal = st.text_input("Código Postal", value=client_dict.get("codigo_postal", ""))
                        ocupacion_profesion = st.text_input("Ocupación/Profesión", value=client_dict.get("ocupacion_profesion", ""))
                        empresa_trabajo = st.text_input("Empresa donde trabaja", value=client_dict.get("empresa_trabajo", ""))
                        tipo_empresa = st.text_input("Tipo de Empresa", value=client_dict.get("tipo_empresa", ""))
                        ingresos_mensuales = st.text_input("Ingresos Mensuales", value=client_dict.get("ingresos_mensuales", ""))
                        nivel_educacion = st.text_input("Nivel de Educación", value=client_dict.get("nivel_educacion", ""))
                        fumador = st.text_input("Fumador", value=client_dict.get("fumador", ""))
                        actividades_riesgo = st.text_area("Actividades de Riesgo", value=client_dict.get("actividades_riesgo", ""))
                        historial_medico = st.text_area("Historial Médico", value=client_dict.get("historial_medico", ""))
                        historial_siniestros = st.text_area("Historial Siniestros", value=client_dict.get("historial_siniestros", ""))
                        vehiculos_registrados = st.text_area("Vehículos Registrados", value=client_dict.get("vehiculos_registrados", ""))
                        propiedades = st.text_area("Propiedades", value=client_dict.get("propiedades", ""))
                        tipo_contribuyente = st.text_input("Tipo Contribuyente", value=client_dict.get("tipo_contribuyente", ""))
                        numero_ruc = st.text_input("Número RUC", value=client_dict.get("numero_ruc", ""))
                        representante_legal_id = st.text_input("ID Representante Legal", value=client_dict.get("representante_legal_id", ""))
                        observaciones_legales = st.text_area("Observaciones Legales", value=client_dict.get("observaciones_legales", ""))
                        canal_preferido_contacto = st.text_input("Canal Preferido de Contacto", value=client_dict.get("canal_preferido_contacto", ""))
                        notas_adicionales = st.text_area("Notas Adicionales", value=client_dict.get("notas_adicionales", ""))
                        fecha_registro = st.date_input(
                            "Fecha de Registro",
                            value=dt.datetime.strptime(client_dict["fecha_registro"], "%Y-%m-%d").date() if client_dict.get("fecha_registro") else dt.date.today()
                        )
                        ultima_actualizacion = st.date_input(
                            "Última Actualización",
                            value=dt.datetime.strptime(client_dict["ultima_actualizacion"], "%Y-%m-%d").date() if client_dict.get("ultima_actualizacion") else dt.date.today()
                        )
                        sector_mercado = st.text_input("Sector/Mercado", value=client_dict.get("sector_mercado", ""))
                        tipo_empresa_categoria = st.text_input("Tipo Empresa Categoría", value=client_dict.get("tipo_empresa_categoria", ""))
                        tipo_persona_juridica = st.text_input("Tipo Persona Jurídica", value=client_dict.get("tipo_persona_juridica", ""))
                        subactividad_economica = st.text_input("Subactividad Económica", value=client_dict.get("subactividad_economica", ""))
                        pagina_web = st.text_input("Página Web", value=client_dict.get("pagina_web", ""))
                        fecha_aniversario = st.date_input(
                            "Fecha de Aniversario",
                            value=dt.datetime.strptime(client_dict["fecha_aniversario"], "%Y-%m-%d").date() if client_dict.get("fecha_aniversario") else dt.date.today()
                        )
                        contacto_autorizado_id = st.text_input("ID Contacto Autorizado", value=client_dict.get("contacto_autorizado_id", ""))

                        submitted = st.form_submit_button("Actualizar Cliente")
                        if submitted:
                            update_fields = {
                                "tipo_cliente": tipo_cliente,
                                "nombres": nombres,
                                "apellidos": apellidos,
                                "razon_social": razon_social,
                                "tipo_documento": tipo_documento,
                                "numero_documento": numero_documento,
                                "fecha_nacimiento": fecha_nacimiento.strftime("%Y-%m-%d") if fecha_nacimiento else None,
                                "nacionalidad": nacionalidad,
                                "sexo": sexo,
                                "estado_civil": estado_civil,
                                "correo_electronico": correo_electronico,
                                "correo_empresa": correo_empresa,
                                "telefono_movil": telefono_movil,
                                "telefono_fijo": telefono_fijo,
                                "direccion_domicilio": direccion_domicilio,
                                "provincia": provincia,
                                "ciudad": ciudad,
                                "codigo_postal": codigo_postal,
                                "ocupacion_profesion": ocupacion_profesion,
                                "empresa_trabajo": empresa_trabajo,
                                "tipo_empresa": tipo_empresa,
                                "ingresos_mensuales": ingresos_mensuales,
                                "nivel_educacion": nivel_educacion,
                                "fumador": fumador,
                                "actividades_riesgo": actividades_riesgo,
                                "historial_medico": historial_medico,
                                "historial_siniestros": historial_siniestros,
                                "vehiculos_registrados": vehiculos_registrados,
                                "propiedades": propiedades,
                                "tipo_contribuyente": tipo_contribuyente,
                                "numero_ruc": numero_ruc,
                                "representante_legal_id": representante_legal_id,
                                "observaciones_legales": observaciones_legales,
                                "canal_preferido_contacto": canal_preferido_contacto,
                                "notas_adicionales": notas_adicionales,
                                "fecha_registro": fecha_registro.strftime("%Y-%m-%d") if fecha_registro else None,
                                "ultima_actualizacion": ultima_actualizacion.strftime("%Y-%m-%d") if ultima_actualizacion else None,
                                "sector_mercado": sector_mercado,
                                "tipo_empresa_categoria": tipo_empresa_categoria,
                                "tipo_persona_juridica": tipo_persona_juridica,
                                "subactividad_economica": subactividad_economica,
                                "pagina_web": pagina_web,
                                "fecha_aniversario": fecha_aniversario.strftime("%Y-%m-%d") if fecha_aniversario else None,
                                "contacto_autorizado_id": contacto_autorizado_id
                            }
                            set_clause = ", ".join([f"{k} = ?" for k in update_fields.keys()])
                            values = list(update_fields.values())
                            values.append(selected_client_id)
                            try:
                                conn = sqlite3.connect(DB_FILE)
                                cursor = conn.cursor()
                                cursor.execute(f"UPDATE clients SET {set_clause} WHERE id = ?", values)
                                conn.commit()
                                conn.close()
                                st.success("Cliente actualizado exitosamente.")
                            except Exception as e:
                                st.error(f"Error al actualizar el cliente: {e}")

        elif operation == "Borrar":
            st.subheader("Eliminar Cliente")
            # Asegura que sqlite3 y DB_FILE estén importados en este scope
            import sqlite3
            from dbconfig import DB_FILE
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombres, apellidos FROM clients")
            clients = cursor.fetchall()
            conn.close()

            # Crear un selectbox con las opciones de cliente (guardar tupla (id, label))
            client_options = [(client[0], f"{client[1]} {client[2]} (ID: {client[0]})") for client in clients]
            selected_client = st.selectbox("Selecciona un cliente para eliminar", client_options, format_func=lambda x: x[1] if x else "")
            selected_client_id = selected_client[0] if selected_client else None

            if st.button("Eliminar Cliente"):
                if selected_client_id:
                    result = delete_client(selected_client_id)
                    st.success(result) if "exitosamente" in result else st.error(result)
                else:
                    st.error("Debes seleccionar un cliente para eliminar.")

    elif module == "Roles":
        st.subheader("Gestión de Roles")
        operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

        import sqlite3  # <-- Asegura que sqlite3 esté importado en este scope
        from dbconfig import DB_FILE  # <-- Asegura que DB_FILE esté importado en este scope

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
            if roles:
                st.table([{"ID": role[0], "Nombre": role[1]} for role in roles])
            else:
                st.info("No hay roles registrados.")

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

        import sqlite3  # <-- Asegura que sqlite3 esté importado en este scope
        from dbconfig import DB_FILE  # <-- Asegura que DB_FILE esté importado en este scope

        if operation == "Crear":
            numero_poliza = st.text_input("Número de Póliza")
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombres || ' ' || apellidos AS nombre_completo FROM clients")
            clientes = cursor.fetchall()
            cursor.execute("SELECT id, username, role FROM users")
            usuarios_roles = cursor.fetchall()
            cursor.execute("SELECT id, razon_social FROM aseguradoras")
            aseguradoras = cursor.fetchall()
            cursor.execute("SELECT id, nombre FROM ramos_seguros")
            ramos_seguros = cursor.fetchall()
            conn.close()
            usuarios = [(u[0], u[1]) for u in usuarios_roles]
            ejecutivos_comerciales = [(u[0], u[1]) for u in usuarios_roles if u[2] and u[2].strip().lower().replace(" ", "_") in ["ejecutivo_comercial", "seller"]]
            cliente_seleccionado = st.selectbox("Selecciona un Cliente", clientes, format_func=lambda x: x[1])
            usuario_seleccionado = st.selectbox("Selecciona un Gestor", usuarios, format_func=lambda x: x[1])
            aseguradora_seleccionada = st.selectbox("Selecciona una Aseguradora", aseguradoras, format_func=lambda x: x[1])
            ramo_seleccionado = st.selectbox("Selecciona un Ramo de Seguros", ramos_seguros, format_func=lambda x: x[1])
            ejecutivo_comercial_seleccionado = st.selectbox(
                "Selecciona un Ejecutivo Comercial",
                ejecutivos_comerciales if ejecutivos_comerciales else [("", "No hay ejecutivos comerciales")],
                format_func=lambda x: x[1] if x and x[1] else "No hay ejecutivos comerciales"
            )
            tipo_poliza = st.selectbox("Tipo de Póliza", ["Nueva", "Renovación"])
            cobertura = st.text_area("Cobertura")
            prima = st.text_input("Prima")
            fecha_inicio_vigencia = st.date_input("Fecha de Inicio Vigencia")
            fecha_fin_vigencia = st.date_input("Fecha de Fin Vigencia")
            estado = st.selectbox("Estado", ["Activa", "Inactiva", "Cancelada"])
            fecha_emision = st.date_input("Fecha de emisión")
            linea_negocio = st.text_input("Línea de negocio")
            suma_asegurada = st.text_input("Suma Asegurada")
            deducible = st.text_input("Deducible")
            sucursal = st.text_input("Sucursal")
            tipo_facturacion = st.selectbox("Tipo de Facturación", ["Contado", "Débito", "Cuota Directa"])
            numero_factura = st.text_input("Nº de factura")
            numero_anexo = st.text_area("Nº de Anexo (puedes ingresar varios separados por coma o salto de línea)")
            tipo_anexo = st.text_input("Tipo de anexo")
            if st.button("Crear Póliza"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO polizas (numero_poliza, cliente_id, usuario_id, aseguradora_id, ramo_id, tipo_poliza, cobertura, prima, fecha_inicio, fecha_fin, estado, fecha_emision, suma_asegurada, deducible, sucursal, tipo_facturacion, linea_negocio, numero_factura, numero_anexo, tipo_anexo, ejecutivo_comercial_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        numero_poliza, cliente_seleccionado[0], usuario_seleccionado[0], aseguradora_seleccionada[0], ramo_seleccionado[0],
                        tipo_poliza, cobertura, prima,
                        fecha_inicio_vigencia.strftime("%Y-%m-%d"),
                        fecha_fin_vigencia.strftime("%Y-%m-%d"),
                        estado, fecha_emision.strftime("%Y-%m-%d"), suma_asegurada, deducible, sucursal, tipo_facturacion, linea_negocio, numero_factura, numero_anexo, tipo_anexo, ejecutivo_comercial_seleccionado[0]
                    ))
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
                SELECT 
                    p.id, p.numero_poliza, 
                    c.nombres || ' ' || c.apellidos AS cliente, 
                    u.username AS gestor, 
                    a.razon_social AS aseguradora,
                    r.nombre AS ramo,
                    p.tipo_poliza, p.cobertura, p.prima, 
                    p.fecha_inicio, p.fecha_fin, p.estado, 
                    p.fecha_emision, p.suma_asegurada, p.deducible, p.sucursal, 
                    p.tipo_facturacion, p.linea_negocio, p.numero_factura, 
                    p.numero_anexo, p.tipo_anexo,
                    (SELECT username FROM users WHERE id = p.ejecutivo_comercial_id) AS ejecutivo_comercial
                FROM polizas p
                JOIN clients c ON p.cliente_id = c.id
                JOIN users u ON p.usuario_id = u.id
                JOIN aseguradoras a ON p.aseguradora_id = a.id
                JOIN ramos_seguros r ON p.ramo_id = r.id
            """)
            polizas = cursor.fetchall()
            conn.close()
            if polizas:
                st.write([{
                    "ID": poliza[0],
                    "Número de Póliza": poliza[1],
                    "Cliente": poliza[2],
                    "Gestor": poliza[3],
                    "Aseguradora": poliza[4],
                    "Ramo": poliza[5],
                    "Tipo de Póliza": poliza[6],
                    "Cobertura": poliza[7],
                    "Prima": poliza[8],
                    "Fecha de Inicio Vigencia": poliza[9],
                    "Fecha de Fin Vigencia": poliza[10],
                    "Estado": poliza[11],
                    "Fecha de emisión": poliza[12],
                    "Suma Asegurada": poliza[13],
                    "Deducible": poliza[14],
                    "Sucursal": poliza[15],
                    "Tipo de Facturación": poliza[16],
                    "Línea de negocio": poliza[17],
                    "Nº de factura": poliza[18],
                    "Nº de Anexo": poliza[19],
                    "Tipo de anexo": poliza[20],
                    "Ejecutivo Comercial": poliza[21]
                } for poliza in polizas])
            else:
                st.info("No hay pólizas registradas.")

        elif operation == "Modificar":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.id, p.numero_poliza, p.tipo_poliza, p.cobertura, p.prima, 
                       p.fecha_inicio, p.fecha_fin, p.estado, p.aseguradora_id, p.ramo_id, 
                       p.fecha_emision, p.suma_asegurada, p.deducible, p.sucursal, 
                       p.tipo_facturacion, p.linea_negocio, p.numero_factura, p.numero_anexo, p.tipo_anexo, p.ejecutivo_comercial_id
                FROM polizas p
            """)
            polizas = cursor.fetchall()
            cursor.execute("SELECT id, razon_social FROM aseguradoras")
            aseguradoras = cursor.fetchall()
            cursor.execute("SELECT id, nombre FROM ramos_seguros")
            ramos_seguros = cursor.fetchall()
            cursor.execute("SELECT id, username FROM users")
            ejecutivos_comerciales = cursor.fetchall()
            conn.close()
            if not polizas:
                st.warning("No hay pólizas registradas.")
                return
            selected_poliza = st.selectbox("Selecciona una póliza", polizas, format_func=lambda x: x[1])
            if selected_poliza:
                if len(selected_poliza) < 20:
                    st.error("Error: Los datos de la póliza seleccionada están incompletos.")
                    return
                numero_poliza = st.text_input("Número de Póliza", value=selected_poliza[1])
                tipo_poliza = st.selectbox(
                    "Tipo de Póliza",
                    ["Nueva", "Renovación"],
                    index=["Nueva", "Renovación"].index(selected_poliza[2]) if selected_poliza[2] in ["Nueva", "Renovación"] else 0
                )
                cobertura = st.text_area("Cobertura", value=selected_poliza[3])
                prima = st.text_input("Prima", value=selected_poliza[4])
                fecha_inicio_vigencia = st.date_input("Fecha de Inicio Vigencia", value=selected_poliza[5])
                fecha_fin_vigencia = st.date_input("Fecha de Fin Vigencia", value=selected_poliza[6])
                estado = st.selectbox("Estado", ["Activa", "Inactiva", "Cancelada"], index=["Activa", "Inactiva", "Cancelada"].index(selected_poliza[7]))
                aseguradora_index = next((i for i, aseguradora in enumerate(aseguradoras) if aseguradora[0] == selected_poliza[8]), 0)
                aseguradora_seleccionada = st.selectbox("Selecciona una Aseguradora", aseguradoras, format_func=lambda x: x[1], index=aseguradora_index)
                ramo_index = next((i for i, ramo in enumerate(ramos_seguros) if ramo[0] == selected_poliza[9]), 0)
                ramo_seleccionado = st.selectbox("Selecciona un Ramo de Seguros", ramos_seguros, format_func=lambda x: x[1], index=ramo_index)
                ejecutivo_comercial_index = next((i for i, ejecutivo in enumerate(ejecutivos_comerciales) if ejecutivo[0] == selected_poliza[19]), 0)
                ejecutivo_comercial_seleccionado = st.selectbox("Selecciona un Ejecutivo Comercial", ejecutivos_comerciales, format_func=lambda x: x[1], index=ejecutivo_comercial_index)
                import datetime
                try:
                    fecha_emision_value = datetime.datetime.strptime(selected_poliza[10], "%Y-%m-%d").date() if selected_poliza[10] else None
                except Exception:
                    fecha_emision_value = None
                fecha_emision = st.date_input("Fecha de emisión", value=fecha_emision_value)
                suma_asegurada = st.text_input("Suma Asegurada", value=selected_poliza[11])
                deducible = st.text_input("Deducible", value=selected_poliza[12])
                sucursal = st.text_input("Sucursal", value=selected_poliza[13])
                tipo_facturacion = st.selectbox(
                    "Tipo de Facturación",
                    ["Contado", "Débito", "Cuota Directa"],
                    index=["Contado", "Débito", "Cuota Directa"].index(selected_poliza[14]) if selected_poliza[14] in ["Contado", "Débito", "Cuota Directa"] else 0
                )
                linea_negocio = st.text_input("Línea de negocio", value=selected_poliza[15])
                numero_factura = st.text_input("Nº de factura", value=selected_poliza[16])
                numero_anexo = st.text_area("Nº de Anexo (puedes ingresar varios separados por coma o salto de línea)", value=selected_poliza[17])
                tipo_anexo = st.text_input("Tipo de anexo", value=selected_poliza[18])
                if st.button("Actualizar Póliza"):
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            UPDATE polizas
                            SET numero_poliza = ?, tipo_poliza = ?, cobertura = ?, prima = ?, 
                                fecha_inicio = ?, fecha_fin = ?, estado = ?, aseguradora_id = ?, 
                                ramo_id = ?, fecha_emision = ?, suma_asegurada = ?, deducible = ?, 
                                sucursal = ?, tipo_facturacion = ?, linea_negocio = ?, numero_factura = ?, numero_anexo = ?, tipo_anexo = ?, ejecutivo_comercial_id = ?
                            WHERE id = ?
                        """, (
                            numero_poliza, tipo_poliza, cobertura, prima,
                            fecha_inicio_vigencia.strftime("%Y-%m-%d"),
                            fecha_fin_vigencia.strftime("%Y-%m-%d"),
                            estado, aseguradora_seleccionada[0], ramo_seleccionado[0], fecha_emision.strftime("%Y-%m-%d") if fecha_emision else "", suma_asegurada, deducible, sucursal, tipo_facturacion, linea_negocio, numero_factura, numero_anexo, tipo_anexo, ejecutivo_comercial_seleccionado[0], selected_poliza[0]
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

    elif module == "Agencias":  # Cambiado de "Agrupadores" a "Agencias"
        st.subheader("Gestión de Agencias")  # Cambiado de "Agrupadores" a "Agencias"
        operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"])

        import sqlite3  # <-- Asegura que sqlite3 esté importado en este scope
        from dbconfig import DB_FILE  # <-- Asegura que DB_FILE esté importado en este scope

        if operation == "Crear":
            with st.form("crear_agencia"):
                name = st.text_input("Nombre de la Agencia")
                address = st.text_area("Dirección")
                phone = st.text_input("Teléfono")
                email = st.text_input("Correo Electrónico")
                submit_button = st.form_submit_button("Crear Agencia")
                if submit_button:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            INSERT INTO companies (name, address, phone, email)
                            VALUES (?, ?, ?, ?)
                        """, (name, address, phone, email))
                        conn.commit()
                        st.success("Agencia creada exitosamente")
                    except sqlite3.IntegrityError:
                        st.error("El nombre de la agencia ya existe.")
                    finally:
                        conn.close()

        elif operation == "Leer":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, address, phone, email FROM companies")
            columns = [col[0] for col in cursor.description]
            agencias = [dict(zip(columns, row)) for row in cursor.fetchall()]
            conn.close()
            if agencias:
                import pandas as pd
                df = pd.DataFrame(agencias)
                st.dataframe(df)
            else:
                st.info("No hay agencias registradas.")

        elif operation == "Modificar":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM companies")
            agencias = cursor.fetchall()
            conn.close()
            selected_agencia = st.selectbox("Selecciona una agencia", agencias, format_func=lambda x: x[1])
            if selected_agencia:
                name = st.text_input("Nombre de la Agencia", value=selected_agencia[1])
                address = st.text_area("Dirección")
                phone = st.text_input("Teléfono")
                email = st.text_input("Correo Electrónico")
                if st.button("Actualizar Agencia"):
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            UPDATE companies
                            SET name = ?, address = ?, phone = ?, email = ?
                            WHERE id = ?
                        """, (name, address, phone, email, selected_agencia[0]))
                        conn.commit()
                        st.success("Agencia actualizada exitosamente")
                    except sqlite3.IntegrityError:
                        st.error("Error al actualizar la agencia.")
                    finally:
                        conn.close()

        elif operation == "Borrar":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM companies")
            agencias = cursor.fetchall()
            conn.close()
            selected_agencia = st.selectbox("Selecciona una agencia para eliminar", agencias, format_func=lambda x: x[1])
            if st.button("Eliminar Agencia"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                try:
                    cursor.execute("DELETE FROM companies WHERE id = ?", (selected_agencia[0],))
                    conn.commit()
                    st.success("Agencia eliminada exitosamente")
                except sqlite3.IntegrityError:
                    st.error("No se puede eliminar la agencia asignada a usuarios.")
                finally:
                    conn.close()

    elif module == "Aseguradoras":
        st.subheader("Gestión de Aseguradoras")
        action = st.selectbox("Seleccione una acción", ["Crear", "Leer", "Actualizar", "Eliminar"])

        import sqlite3  # <-- Asegura que sqlite3 esté importado en este scope
        from dbconfig import DB_FILE  # <-- Asegura que DB_FILE esté importado en este scope

        if action == "Crear":
            with st.form("crear_aseguradora"):
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
                submit_button = st.form_submit_button("Crear Aseguradora")
                if submit_button:
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
                    result = create_aseguradora(aseguradora_data, ramo_ids)
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
                st.dataframe(data)
            else:
                st.info("No hay aseguradoras registradas.")

        elif action == "Actualizar":
            aseguradoras = read_aseguradoras()
            if aseguradoras:
                aseguradora_names = {aseguradora[4]: aseguradora[0] for aseguradora in aseguradoras}
                selected_name = st.selectbox("Seleccione una aseguradora", list(aseguradora_names.keys()))
                selected_id = aseguradora_names[selected_name]
                aseguradora = next(a for a in aseguradoras if a[0] == selected_id)
                with st.form("actualizar_aseguradora"):
                    tipo_contribuyente = st.text_input("Tipo de Contribuyente", value=aseguradora[1])
                    tipo_identificacion = st.text_input("Tipo de Identificación", value=aseguradora[2])
                    identificacion = st.text_input("Identificación", value=aseguradora[3])
                    razon_social = st.text_input("Razón Social", value=aseguradora[4])
                    nombre_comercial = st.text_input("Nombre Comercial", value=aseguradora[5])

                    pais = st.text_input("País", value=aseguradora[6])
                    representante_legal = st.text_input("Representante Legal", value=aseguradora[7])

                    aniversario = st.date_input("Aniversario", value=aseguradora[8] if aseguradora[8] else None)



                    web = st.text_input("Web", value=aseguradora[9])
                    correo_electronico = st.text_input("Correo Electrónico", value=aseguradora[10])
                    # Fetch available Ramos de Seguros
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, nombre FROM ramos_seguros")
                    ramos = cursor.fetchall()
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
                    submit_button = st.form_submit_button("Actualizar Aseguradora")
                    if submit_button:
                        result = update_aseguradora(selected_id, (
                            tipo_contribuyente, tipo_identificacion, identificacion, razon_social,
                            nombre_comercial, pais, representante_legal, aniversario.strftime("%Y-%m-%d") if aniversario else None,
                            web, correo_electronico
                        ), ramo_ids)
                        st.success(result) if "exitosamente" in result else st.error(result)
            else:
                st.info("No hay aseguradoras registradas.")

        elif action == "Eliminar":
            aseguradoras = read_aseguradoras()
            if aseguradoras:
                aseguradora_names = {aseguradora[4]: aseguradora[0] for aseguradora in aseguradoras}
                selected_name = st.selectbox("Seleccione una aseguradora para eliminar", list(aseguradora_names.keys()))
                if st.button("Eliminar"):
                    selected_id = aseguradora_names[selected_name]
                    result = delete_aseguradora(selected_id)
                    st.success(result) if "exitosamente" in result else st.error(result)
            else:
                st.info("No hay aseguradoras registradas.")

    elif module == "Ramos de Seguros":
        st.subheader("Gestión de Ramos de Seguros")

        import sqlite3  # <-- Asegura que sqlite3 esté importado en este scope
        from dbconfig import DB_FILE  # <-- Asegura que DB_FILE esté importado en este scope

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
            columns = [col[0] for col in cursor.description]
            ramos = [dict(zip(columns, row)) for row in cursor.fetchall()]
            if ramos:
                import pandas as pd
                df = pd.DataFrame(ramos)
                st.dataframe(df)
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