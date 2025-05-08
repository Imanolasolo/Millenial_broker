import streamlit as st
import sqlite3
import jwt
import datetime
import bcrypt
import base64
from dashboards.admin_dashboard import admin_dashboard
from dashboards.user_dashboard import user_dashboard
from dbconfig import DB_FILE, SECRET_KEY, initialize_database

# Configurar la app
st.set_page_config(page_icon="logo.png", page_title="Millenial Broker", layout="wide")

# Función para codificar imagen de fondo
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"Error al leer el archivo '{bin_file}': {e}")
        return None

# Fondo
img_base64 = get_base64_of_bin_file('5134336.jpg')
if img_base64:
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

# Inicializar DB
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    ''')

    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        hashed_pw = bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ("admin", hashed_pw, "admin"))
        conn.commit()

    conn.close()

# Función de autenticación
def authenticate(username, password):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        st.error("Usuario no encontrado.")
        return None

    hashed_password = user[2]  # guardado como str (debe haber sido .decode() al guardar)
    if bcrypt.checkpw(password.encode(), hashed_password.encode()):
        token = jwt.encode(
            {
                "username": user[1],
                "role": user[3],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            },
            SECRET_KEY,
            algorithm="HS256"
        )
        st.session_state["token"] = token
        return token
    else:
        st.error("Contraseña incorrecta.")
        return None

# Página de login
def login_page():
    st.image("logo.png", width=150)
    st.title("Iniciar Sesión")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        token = authenticate(username, password)
        if token:
            st.success("¡Bienvenido!")
            st.rerun()

# Lógica principal
def main():
    init_db()
    if "token" in st.session_state:
        try:
            payload = jwt.decode(st.session_state["token"], SECRET_KEY, algorithms=["HS256"])
            role = payload.get("role", "").lower()

            if role == "admin":
                admin_dashboard()
            else:
                user_dashboard(role=role)
        except jwt.ExpiredSignatureError:
            st.error("Sesión expirada. Inicie sesión nuevamente.")
            del st.session_state["token"]
            st.rerun()
    else:
        login_page()

if __name__ == "__main__":
    initialize_database()
    main()
