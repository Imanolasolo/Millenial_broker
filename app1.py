import streamlit as st
import sqlite3
import jwt
import datetime
import bcrypt
import base64
import os
from dashboards.admin_dashboard import admin_dashboard
from dbconfig import DB_FILE, SECRET_KEY
from user_dashboard import user_dashboard
from crud.user_crud import create_user, read_users, update_user, delete_user, get_user_details
from database_config import initialize_database

# Configuración inicial
st.set_page_config(page_icon="logo.png", page_title="Millenial Broker", layout="wide")

# Function to encode image as base64 to set as background
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"Error al leer el archivo '{bin_file}': {e}")
        return None

# Encode the background image
img_base64 = get_base64_of_bin_file('assets/5134336.jpg')

if img_base64:
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

# Función para autenticar usuarios
def authenticate(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        st.error("Usuario no encontrado.")
        return None

    # Ensure the stored password is in bytes format
    stored_password = user[2].encode() if isinstance(user[2], str) else user[2]

    if bcrypt.checkpw(password.encode(), stored_password):
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
            st.session_state["username"] = user[1]
            st.session_state["token"] = token
            return token
        except Exception as e:
            st.error(f"Error al generar el token: {e}")
            return None

    st.error("Contraseña incorrecta.")
    return None

# Página de login y redirigir a dashboards
def login_page():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("assets/logo.png", width=100)
    with col2:
        st.title("Bienvenidos al :orange[BCS] de :blue[MILLENNIAL BROKER] - Iniciar Sesión")
    # --- CAMBIO: dropdown para usuarios ---
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    user_list = [row[0] for row in cursor.fetchall()]
    conn.close()
    username = st.selectbox("Usuario", user_list) if user_list else st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Login"):
        token = authenticate(username, password)
        if token:
            st.success("Autenticación exitosa!")
            st.rerun()

# Verificar sesión y redirigir a dashboards
def main():
    initialize_database()
    if "token" in st.session_state:
        try:
            payload = jwt.decode(st.session_state["token"], SECRET_KEY, algorithms=["HS256"])
            username = payload["username"]
            role = payload["role"]
            # Normalizar el rol para comparación robusta
            normalized_role = role.lower().replace(" ", "").replace("_", "").replace("-", "")
            # Redirigir según el rol
            if normalized_role == "admin":
                admin_dashboard()
            elif normalized_role in ["ejecutivocomercial", "seller"]:
                from dashboards.Ejecutivo_Comercial_dashboard import welcome_message, manage_modules
                welcome_message()
                manage_modules()
            elif normalized_role in ["backofficeoperacion"]:
                from dashboards.Back_Office_Operacion_dashboard import welcome_message, manage_modules
                welcome_message()
                manage_modules()
            else:
                user_dashboard()
        except jwt.ExpiredSignatureError:
            st.error("Sesión expirada, por favor inicie sesión nuevamente")
            del st.session_state["token"]
            st.rerun()
    else:
        login_page()

if __name__ == "__main__":
    initialize_database()
    main()
