import streamlit as st
from datetime import datetime

import base64
st.set_page_config(
    page_title="Presentación del Proyecto",
    page_icon="📊",
    layout="wide"
)

# Function to encode image as base64 to set as background
def get_base64_of_bin_file(bin_file):
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()

    # Encode the background image
img_base64 = get_base64_of_bin_file('5134336.jpg')

    # Set the background image using the encoded base64 string
st.markdown(
    f"""
    <style>
    .stApp {{
        background: url('data:image/jpeg;base64,{img_base64}') no-repeat center center fixed;
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)


# --- Sidebar ---
st.sidebar.title("🚀 Navegación")
page = st.sidebar.radio("Ir a:", [
    "Inicio",
    "Metodología",
    "Cronograma",
    "Herramientas",
    "Fases del Proyecto",
    "Asistente Virtual",
    "Beneficios",
    "Contacto"
])

# --- Home ---
if page == "Inicio":
    st.title("Sistema de Gestión con Asistente Virtual Embebido")
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo.png", width=120)
    with col2:
        st.subheader("Millennial Broker — Manta, Ecuador")
        st.markdown("""
    ### 👋 Bienvenido
    Esta es una presentación interactiva del proyecto de desarrollo del sistema para la gestión de clientes, pólizas y siniestros, con integración de un asistente virtual inteligente.
    
    Explora el menú lateral para conocer más sobre la metodología, cronograma y arquitectura del proyecto.
    """)

# --- Metodología ---
elif page == "Metodología":
    st.header("🧠 Metodología de Desarrollo")
    st.markdown("""
    ### Enfoque Ágil
    Se utilizará una metodología ágil, basada en **Scrum** y ciclos iterativos de una semana.

    **Objetivos:**
    - Entregas funcionales constantes
    - Flexibilidad ante cambios
    - Feedback continuo con el cliente
    - Incremento de valor desde el inicio
    """)

    with st.expander("🔁 Iteración Semanal"):
        st.markdown("""
        - Lunes: Planificación
        - Martes a Jueves: Desarrollo y pruebas
        - Viernes: Demo + Feedback del cliente
        - Sábado: Ajustes finales y documentación
        """)

# --- Cronograma ---
elif page == "Cronograma":
    st.header("📅 Cronograma de Trabajo")
    cronograma = {
        "Semana 1": "Descubrimiento y Diseño",
        "Semana 2": "Setup Técnico y Login",
        "Semana 3": "Módulo de Administración",
        "Semana 4": "Dashboards por Rol",
        "Semana 5": "Módulo de Gestión de Pólizas",
        "Semana 6": "Módulo de Siniestros",
        "Semana 7": "Integración del Asistente Virtual",
        "Semana 8": "Pruebas, Documentación y Despliegue"
    }

    for semana, tarea in cronograma.items():
        st.write(f"**{semana}:** {tarea}")

# --- Herramientas ---
elif page == "Herramientas":
    st.header("🛠️ Herramientas Utilizadas")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - **Lenguaje:** Python
        - **Framework:** Streamlit
        - **Base de datos:** SQLite
        - **Control de versiones:** Git + GitHub
        """)
    with col2:
        st.markdown("""
        - **Despliegue:** Streamlit Cloud
        - **IA:** Modelos OpenAI / LLMs
        - **Gestión del proyecto:** Trello / Notion
        """)

# --- Fases del Proyecto ---
elif page == "Fases del Proyecto":
    st.header("⚙️ Fases del Proyecto")
    fases = {
        "Fase 1": "Relevamiento de requerimientos y diseño de flujos",
        "Fase 2": "Login y autenticación por roles",
        "Fase 3": "Dashboard administrativo",
        "Fase 4": "Dashboards personalizados por rol",
        "Fase 5": "Gestión de pólizas",
        "Fase 6": "Gestión de siniestros",
        "Fase 7": "Integración del asistente virtual",
        "Fase 8": "QA, documentación y despliegue"
    }
    for fase, detalle in fases.items():
        with st.expander(fase):
            st.write(detalle)

# --- Asistente Virtual ---
elif page == "Asistente Virtual":
    st.header("🤖 Asistente Virtual Embebido")
    st.markdown("""
    El asistente virtual se integrará para responder preguntas frecuentes, guiar a usuarios y brindar soporte básico dentro del sistema, usando modelos LLM (Language Models).

    **Capacidades:**
    - Respuestas automáticas sobre pólizas, siniestros y procesos.
    - Entrenado con la documentación interna de la correduría.
    - Interfaz integrada en cada dashboard según el rol.
    """)

# --- Beneficios ---
elif page == "Beneficios":
    st.header("📈 Beneficios del Proyecto")
    st.markdown("""
    - Automatización de procesos manuales.
    - Mayor trazabilidad y control.
    - Mejora en la atención al cliente.
    - Aumento en la eficiencia operativa.
    - Asistente virtual que reduce la carga operativa.
    - Accesibilidad desde cualquier dispositivo.
    """)

# --- Contacto ---
elif page == "Contacto":
    st.header("📞 Contacto")
    st.markdown("""
    ### ¿Deseas agendar una reunión o conocer más?
    - 👨‍💼 Imanol Asolo
    - 📧 jjusturi@gmail.com
    - 🌐 [www.codecodix.com](https://www.codecodix.com)
    - 📍 Manta, Ecuador
    """)

    st.button("Solicitar propuesta completa", use_container_width=True)

    st.markdown("---")
    st.caption(f"Presentación generada el {datetime.now().strftime('%d/%m/%Y')}")
    st.text("Desarrollado por Imanol Asolo y el equipo de CodeCodix")