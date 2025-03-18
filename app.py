import streamlit as st
import base64

# Configuración inicial
st.set_page_config(page_title="Millenial Broker", layout="wide")

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

# Simulación de usuarios
users = {
    "admin": {"password": "admin123", "role": "Administrador"},
    "superuser": {"password": "superuser123", "role": "Superusuario"},
    "asesor": {"password": "asesor123", "role": "Asesor"}
}

# Función de autenticación
def authenticate(username, password):
    user = users.get(username)
    if user and user["password"] == password:
        return user["role"]
    return None

# Inicializar sesión
if "role" not in st.session_state:
    st.session_state["role"] = None

# Interfaz de login
col1, col2 = st.columns([1,2])
with col1:
    st.image("logo.png", width=200)
with col2:
    st.title("Business Core - :orange[Millennial Broker]")

if st.session_state["role"] is None:
    st.subheader("Inicio de Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar Sesión"):
        role = authenticate(username, password)
        if role:
            st.session_state["role"] = role
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

# Redirección a módulos según rol
else:
    role = st.session_state["role"]
    st.warning(f"Bienvenido, {role}")
    
    if role == "Administrador":
        st.header("Módulo de Administración")
        st.write("Gestión de usuarios, configuración general y reportes administrativos.")
    elif role == "Superusuario":
        st.header("Módulo de Supervisión")
        st.write("Gestión avanzada de siniestros, cartera y supervisión de asesores.")
    elif role == "Asesor":
        st.header("Módulo de Asesoría")
        st.write("Consulta y gestión de pólizas, clientes y prospección de ventas.")
    
    if st.button("Cerrar Sesión"):
        st.session_state["role"] = None
        st.rerun()