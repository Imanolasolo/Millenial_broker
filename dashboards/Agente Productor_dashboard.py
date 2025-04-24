# filepath: f:\CODECODIX\MILLENIAL_BROKER_project\dashboards\Agente Productor_dashboard.py
# Dashboard para el rol: Agente Productor

import streamlit as st

def welcome_message():
    st.header("Bienvenido al dashboard del rol: :red[ Agente Productor ]")

def manage_modules():
    # Aquí se gestionarán los módulos necesarios para este rol
    st.write("Gestionando módulos para el rol: Agente Productor")

    if st.button("Logout"):
        del st.session_state["token"]  # Eliminar el token de la sesión
        st.success("Sesión cerrada exitosamente")
        st.rerun()  # Recargar la página para volver al login

if __name__ == "__main__":
    welcome_message()
    manage_modules()
