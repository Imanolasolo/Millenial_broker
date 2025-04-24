# filepath: f:\CODECODIX\MILLENIAL_BROKER_project\dashboards\Agente Productor_dashboard.py
# Dashboard para el rol: Agente Productor
import streamlit as st
def welcome_message():
    st.header("Bienvenido al dashboard del rol: :red[ Agente Productor ]")

def manage_modules():
    # Aquí se gestionarán los modulos necesarios para este rol
    st.write("Gestionando modulos para el rol: Agente Productor")

    if st.button("Logout"):
<<<<<<< HEAD:dashboards/Agente productor_dashboard.py
        del st.session_state["token"]  # Eliminar el token de la sesión
        st.success("Sesion cerrada exitosamente")
        st.rerun()  # Recargar la página para volver al login
=======
        del st.session_state["token"]  # Eliminar el token de la sesiÃ³n
        st.success("SesiÃ³n cerrada exitosamente")
        st.rerun()  # Recargar la pÃ¡gina para volver al login

if __name__ == "__main__":
    welcome_message()
    manage_modules()
>>>>>>> 1e35ae50a9141576324d2af3605c8e5440b88dd4:dashboards/Agente Productor_dashboard.py
