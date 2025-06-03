# filepath: f:\CODECODIX\MILLENIAL_BROKER_project\dashboards\user_dashboard.py
# Dashboard para el rol: user

import streamlit as st
from crud.user_crud import get_user_details

def welcome_message():
    print("Bienvenido al dashboard del rol: user")

def manage_modules():
    # Aquí se gestionarán los módulos necesarios para este rol
    print("Gestionando módulos para el rol: user")

def user_dashboard():
    # Retrieve username from session state
    username = st.session_state.get("username")
    user_details = get_user_details(username) if username else None

    # Display header with avatar, name, and group
    st.sidebar.image("avatar.png", width=100)  # Replace with the path to your avatar image
    st.sidebar.markdown(f"**Usuario:** {user_details['full_name'] if user_details else 'Desconocido'}")
    st.sidebar.markdown(f"**Afiliación:** {user_details['company_name'] if user_details else 'Sin afiliación'}")

if __name__ == "__main__":
    welcome_message()
    manage_modules()