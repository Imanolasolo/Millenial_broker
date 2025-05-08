import streamlit as st
import sqlite3
import jwt
import datetime
import bcrypt
import base64
import os
from dashboards.admin_dashboard import admin_dashboard
from dbconfig import DB_FILE, SECRET_KEY, initialize_database
from user_dashboard import user_dashboard
from user_crud import initialize_users_table

# Configuración inicial
st.set_page_config(page_icon="logo.png", page_title="Millenial Broker", layout="wide")

initialize_users_table()

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
img_base64 = get_base64_of_bin_file('5134336.jpg')

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

# Crear la base de datos y tabla de usuarios
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Crear tabla de usuarios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')
    # Verificar si el usuario admin existe, si no, crearlo
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        hashed_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ("admin", hashed_pw, "admin"))
        conn.commit()

    # Crear tabla de aseguradoras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aseguradoras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            direccion TEXT,
            telefono TEXT,
            email TEXT
        )
    ''')
    conn.commit()

    # Crear tabla de ramos de seguros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ramos_seguros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            descripcion TEXT
        )
    ''')
    conn.commit()

    conn.close()

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

    if bcrypt.checkpw(password.encode(), user[2].encode()):  # ✅ FIXED LINE
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
        st.image("logo.png", width=100)
    with col2:
        st.title("Iniciar Sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Login"):
        token = authenticate(username, password)
        if token:
            st.success("Autenticación exitosa!")
            st.rerun()

# Verificar sesión y redirigir a dashboards
def main():
    init_db()
    if "token" in st.session_state:
        try:
            payload = jwt.decode(st.session_state["token"], SECRET_KEY, algorithms=["HS256"])
            username = payload["username"]
            role = payload["role"]
            if role.lower() == "admin":
                admin_dashboard()
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
