import streamlit as st

def user_dashboard():
    st.title("Dashboard de Usuario")
    st.write("Bienvenido, usuario")

    # Reintroducir botones de Reportes y Configuración en el sidebar
    st.sidebar.button("Reportes")
    st.sidebar.button("Configuración")

    # Botón de Logout
    if st.button("Logout"):
        del st.session_state["token"]  # Eliminar el token de la sesión
        st.success("Sesión cerrada exitosamente")
        st.rerun()  # Recargar la página para volver al login
