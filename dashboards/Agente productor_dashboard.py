# filepath: f:\CODECODIX\MILLENIAL_BROKER_project\dashboards\Agente productor_dashboard.py
# Dashboard para el rol: Agente productor
import streamlit as st

def welcome_message():
    st.markdown("### **Bienvenido al dashboard del rol: :red[Agente productor]**")  # Usar st.markdown para encabezado en negrita
    
def manage_modules():
    # Aquí se gestionarán los módulos necesarios para este rol
    st.write("Gestionando módulos para el rol: Agente productor")

    if st.button("Logout"):
        del st.session_state["token"]  # Eliminar el token de la sesión
        st.success("Sesión cerrada exitosamente")
        st.rerun()  # Recargar la página para volver al login

if __name__ == "__main__":
    welcome_message()
    manage_modules()
