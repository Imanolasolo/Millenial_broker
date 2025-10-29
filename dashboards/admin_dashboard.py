import streamlit as st
import fitz  # PyMuPDF
#from langchain_text_splitters import RecursiveCharacterTextSplitter
#from langchain.embeddings import OpenAIEmbeddings
#from langchain.vectorstores import FAISS
#from langchain.memory import ConversationBufferMemory
#from langchain.chains import ConversationalRetrievalChain
#from langchain.chat_models import ChatOpenAI 
#from htmlTemplates import css, bot_template, user_template
import os
import datetime as dt
import re

# Importa los CRUD UI desde el folder crud
from crud.user_crud import crud_usuarios, get_user_details
from crud.client_crud import crud_clientes
from crud.aseguradora_crud import crud_aseguradoras
from crud.agencias_crud import crud_agencias
from crud.role_crud import crud_roles
from crud.poliza_crud import crud_polizas
from crud.ramos_crud import crud_ramos
from crud.movimiento_crud import crud_movimientos

def get_pdf_text(pdf_list):
    text = ""
    for pdf_path in pdf_list:
        pdf_document = fitz.open(pdf_path)
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
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