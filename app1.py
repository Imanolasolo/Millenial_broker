import streamlit as st
import sqlite3
import jwt
import datetime
import bcrypt
import base64
import importlib.util
import os
from dashboards.admin_dashboard import admin_dashboard
from dbconfig import DB_FILE, SECRET_KEY, initialize_database  # Import the function
from user_dashboard import user_dashboard  # Import the refactored function

# Configuración inicial
st.set_page_config(page_icon="logo.png", page_title="Millenial Broker", layout="wide")

# Llamar a la función para inicializar la base de datos
initialize_database()

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


# Crear la base de datos y tabla de usuarios
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT
                      )''')
    conn.commit()
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        hashed_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ("admin", hashed_pw, "admin"))
        conn.commit()
    conn.close()

# Función para autenticar usuarios
SECRET_KEY = "your_secret_key"  # Ensure SECRET_KEY is defined

def authenticate(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username.strip(),))  # Strip whitespace
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        st.error("Usuario no encontrado. Verifique su nombre de usuario.")
        return None
    
    if len(user) < 4:
        st.error("Estructura de usuario inválida en la base de datos. Contacte al administrador.")
        return None
    
    hashed_password = user[2].encode() if isinstance(user[2], str) else user[2]  # Ensure bytes type
    if bcrypt.checkpw(password.encode(), hashed_password):  # Compare password correctly
        try:
            token = jwt.encode(
                {
                    "username": user[1],
                    "role": user[3],
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
                },
                SECRET_KEY,
                algorithm="HS256"
            )
        except Exception as e:
            st.error(f"Error al generar el token de autenticación: {e}")
            return None
        
        return token
    
    st.error("Contraseña incorrecta. Inténtelo de nuevo.")
    return None

# Página de login
def login_page():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo.png", width=100)
    with col2:
        st.title("Iniciar Sesión")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Login"):
        token = authenticate(username, password)
        if token:
            st.session_state["token"] = token
            st.success("Autenticación exitosa!")
            st.rerun()
        else:
            st.error("Credenciales incorrectas")

# Verificar sesión y redirigir a dashboards
def main():
    init_db()
    if "token" in st.session_state:
        try:
            payload = jwt.decode(st.session_state["token"], SECRET_KEY, algorithms=["HS256"])
            username = payload["username"]
            role = payload["role"]
            
            # Redirect to admin_dashboard if username is "admin" or role is "Administrador"
            if username.lower() == "admin" or role.lower() == "administrador":
                admin_dashboard()
            else:
                # Dynamically construct the dashboard path
                dashboard_path = os.path.join(os.path.dirname(__file__), "dashboards", f"{role}_dashboard.py")
                
                if os.path.exists(dashboard_path):
                    spec = importlib.util.spec_from_file_location(f"{role}_dashboard", dashboard_path)
                    dashboard_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(dashboard_module)
                    # Call these methods only if they exist in the module
                    if hasattr(dashboard_module, "welcome_message"):
                        dashboard_module.welcome_message()
                    if hasattr(dashboard_module, "manage_modules"):
                        dashboard_module.manage_modules()
                else:
                    st.error(f"No se encontró un dashboard para el rol: {role}. Contacte al administrador.")
        except jwt.ExpiredSignatureError:
            st.error("Sesión expirada, por favor inicie sesión nuevamente")
            del st.session_state["token"]
            st.rerun()
    else:
        login_page()

if __name__ == "__main__":
    main()
