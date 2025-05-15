# filepath: f:\CODECODIX\MILLENIAL_BROKER_project\dashboards\Ejecutivo Comercial_dashboard.py
# Dashboard para el rol: Ejecutivo Comercial
import streamlit as st
def welcome_message():
    st.header("Bienvenido al dashboard del rol: :red[ Ejecutivo Comercial ]")

def manage_modules():
    # Aquí se gestionarán los modulos necesarios para este rol
    st.write("Gestionando modulos para el rol: Ejecutivo Comercial")

    if st.button("Logout"):
        del st.session_state["token"]  # Eliminar el token de la sesión
        st.success("Sesion cerrada exitosamente")
        st.rerun()  # Recargar la página para volver al login