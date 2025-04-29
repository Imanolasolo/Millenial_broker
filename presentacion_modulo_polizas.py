import streamlit as st

st.set_page_config(page_title="Proceso de Creación de Póliza", layout="wide")

st.title("📄 Proceso de Creación de una Póliza de Seguros")
st.subheader("Millennial Broker")

with st.expander("📌 Introducción"):
    st.write("""
    El objetivo de esta presentación es explicar de forma clara y estructurada el proceso de creación de una póliza de seguros, 
    resaltando las entidades involucradas y su función en el sistema.
    """)

with st.expander("🧩 Entidades Clave del Proceso"):
    st.markdown("""
    **1. Proceso Póliza (Entidad Central)**  
    Representa el flujo de creación, emisión y gestión de pólizas.

    **2. Cobertura**  
    Define los riesgos o eventos que serán cubiertos por la póliza.

    **3. Cliente**  
    Persona natural o jurídica que contrata la póliza.

    **4. Usuario**  
    Agente, ejecutivo o empleado que gestiona la póliza.

    **5. Ramo**  
    Categoría del seguro: vida, salud, autos, etc.

    **6. Aseguradora**  
    Empresa responsable del respaldo financiero de la póliza.
    """)

with st.expander("⚙️ Flujo del Proceso de Creación"):
    st.markdown("""
    **Paso 1: Registro del Cliente**  
    Se recopila y valida la información del cliente.

    **Paso 2: Selección del Ramo**  
    Se define el tipo de seguro (vida, salud, etc.).

    **Paso 3: Asignación de Aseguradora**  
    Se asocia una aseguradora a la póliza.

    **Paso 4: Definición de Coberturas**  
    Se determinan los riesgos que serán cubiertos.

    **Paso 5: Creación de la Póliza**  
    Se genera el documento y se emite formalmente.

    **Paso 6: Asignación del Usuario Responsable**  
    El usuario encargado queda vinculado al proceso.
    """)

with st.expander("🧠 Beneficios del Modelo"):
    st.markdown("""
    - 🔄 Trazabilidad completa del proceso  
    - 🔐 Seguridad de la información  
    - 📊 Facilita reportes y análisis  
    - ⚖️ Cumplimiento normativo  
    """)

with st.expander("📌 Conclusión"):
    st.write("""
    Este modelo garantiza una estructura robusta y escalable para gestionar pólizas de forma digital. 
    Mejora la experiencia del cliente, facilita la gestión interna y asegura el cumplimiento normativo.
    """)

with st.expander("Proceso graficado"):
    st.image("Proceso_poliza.png", caption="Proceso de creación de póliza de seguros", width=500)
    st.write("El proceso de creación de póliza de seguros se puede graficar como un flujo de trabajo, donde cada paso es esencial para garantizar la correcta emisión y gestión de la póliza.")
