# filepath: f:\CODECODIX\MILLENIAL_BROKER_project\dashboards\Back Office- Operacion_dashboard.py
# Dashboard para el rol: Back Office- Operacion
import streamlit as st
def welcome_message():
    st.header("Bienvenido al dashboard del rol: :red[ Back Office- Operacion ]")

def manage_modules():
    # Aqu� se gestionar�n los modulos necesarios para este rol
    st.write("Gestionando modulos para el rol: Back Office- Operacion")

    if st.button("Logout"):
        del st.session_state["token"]  # Eliminar el token de la sesi�n
        st.success("Sesion cerrada exitosamente")
        st.rerun()  # Recargar la p�gina para volver al login