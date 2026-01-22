# ============================================================================
# DASHBOARD DE ADMINISTRADOR - admin_dashboard.py
# ============================================================================
# Panel de control principal para usuarios con rol de administrador
# Proporciona acceso completo a todos los módulos CRUD del sistema
# ============================================================================

# Importaciones de librerías
import streamlit as st  # Framework de interfaz de usuario
import fitz  # PyMuPDF para procesamiento de PDFs
import os  # Operaciones del sistema operativo
import datetime as dt  # Manejo de fechas
import re  # Expresiones regulares

# Importaciones comentadas: funcionalidad de IA/Chat deshabilitada
#from langchain_text_splitters import RecursiveCharacterTextSplitter
#from langchain.embeddings import OpenAIEmbeddings
#from langchain.vectorstores import FAISS
#from langchain.memory import ConversationBufferMemory
#from langchain.chains import ConversationalRetrievalChain
#from langchain.chat_models import ChatOpenAI 
#from htmlTemplates import css, bot_template, user_template

# ============================================================================
# IMPORTACIONES DE MÓDULOS CRUD
# ============================================================================
# Importa todas las interfaces CRUD desde el directorio crud/
from crud.user_crud import crud_usuarios, get_user_details  # Gestión de usuarios
from crud.client_crud import crud_clientes  # Gestión de clientes
from crud.aseguradoras_crud import crud_aseguradoras  # Gestión de aseguradoras - CORREGIDO
from crud.agencias_crud import crud_agencias  # Gestión de agencias
from crud.role_crud import crud_roles  # Gestión de roles
from crud.poliza_crud import crud_polizas  # Gestión de pólizas
from crud.ramos_crud import crud_ramos  # Gestión de ramos de seguros
from crud.movimiento_crud import crud_movimientos  # Gestión de movimientos

# ============================================================================
# FUNCIÓN: get_pdf_text
# Extrae texto de una lista de archivos PDF
# ============================================================================
def get_pdf_text(pdf_list):
    """
    Extrae y concatena el texto de múltiples archivos PDF
    
    Parámetros:
        pdf_list (list): Lista de rutas a archivos PDF
    
    Retorna:
        str: Texto concatenado de todos los PDFs
    """
    text = ""  # String para acumular el texto extraído
    
    # Iterar sobre cada archivo PDF
    for pdf_path in pdf_list:
        # Abrir el documento PDF con PyMuPDF (fitz)
        pdf_document = fitz.open(pdf_path)
        
        # Iterar sobre cada página del documento
        for page_num in range(len(pdf_document)):
            # Cargar la página actual
            page = pdf_document.load_page(page_num)
            # Extraer y concatenar el texto de la página
            text += page.get_text()
    
    return text



# ============================================================================
# FUNCIÓN: admin_dashboard
# Renderiza el dashboard completo del administrador
# ============================================================================
def admin_dashboard():
    """
    Muestra la interfaz principal del administrador con acceso a todos los módulos
    Incluye información del usuario, menús de navegación e instrucciones
    """
    # ============================================================================
    # OBTENER INFORMACIÓN DEL USUARIO ACTUAL
    # ============================================================================
    # Recuperar nombre de usuario desde la sesión de Streamlit
    username = st.session_state.get("username")
    # Obtener detalles completos del usuario (nombre, empresa, etc.)
    user_details = get_user_details(username) if username else None

    # ============================================================================
    # BARRA LATERAL: Información del usuario
    # ============================================================================
    # Mostrar avatar del usuario
    st.sidebar.image("assets/avatar.png", width=100)
    # Mostrar nombre completo del usuario
    st.sidebar.markdown(f"**Usuario:** {user_details['full_name'] if user_details else 'Desconocido'}")
    # Mostrar empresa/afiliación del usuario
    st.sidebar.markdown(f"**Afiliación:** {user_details['company_name'] if user_details else 'Sin afiliación'}")

    # ============================================================================
    # ENCABEZADO PRINCIPAL
    # ============================================================================
    # Crear dos columnas: pequeña para logo, grande para título
    col1, col2 = st.columns([1, 4])
    with col1:
        # Logo de la aplicación
        st.image("assets/logo.png", width=100)
    with col2:
        # Título del dashboard
        st.title("Dashboard de Administrador")
    
    # Mensaje de bienvenida
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
        ("Movimientos", "Movimientos"),
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
        crud_usuarios()
    elif module == "Clientes":
        crud_clientes()
    elif module == "Aseguradoras":
        crud_aseguradoras()
    elif module == "Agencias":
        crud_agencias()
    elif module == "Roles":
        crud_roles()
    elif module == "Pólizas":
        crud_polizas()
    elif module == "Ramos de Seguros":
        crud_ramos()
    elif module == "Movimientos":
        crud_movimientos()
    # ...puedes agregar más elif para otros módulos si creas sus archivos...

    # Botón de Logout
    if st.sidebar.button("Logout"):
        del st.session_state["token"]  # Eliminar el token de la sesión
        st.success("Sesión cerrada exitosamente")
        st.rerun()  # Recargar la página para volver al login

# Asegurar que la función esté disponible para importación
__all__ = ['admin_dashboard']