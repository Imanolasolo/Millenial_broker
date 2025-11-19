# ============================================================================
# DASHBOARD DE USUARIO ESTÁNDAR - user_dashboard.py
# ============================================================================
# Panel de control para usuarios estándar (no administradores)
# Proporciona acceso limitado a funcionalidades básicas
# ============================================================================

import streamlit as st  # Framework de interfaz de usuario

# ============================================================================
# FUNCIÓN: user_dashboard
# Renderiza el dashboard para usuarios estándar
# ============================================================================
def user_dashboard():
    """
    Muestra la interfaz principal para usuarios con rol estándar
    Incluye opciones básicas de reportes, configuración y logout
    """
    # ============================================================================
    # ENCABEZADO
    # ============================================================================
    st.title("Dashboard de Usuario")
    st.write("Bienvenido, usuario")

    # ============================================================================
    # BARRA LATERAL: Opciones disponibles para el usuario
    # ============================================================================
    # Botón para acceder a reportes (funcionalidad a implementar)
    st.sidebar.button("Reportes")
    # Botón para acceder a configuración (funcionalidad a implementar)
    st.sidebar.button("Configuración")

    # ============================================================================
    # OPCIÓN DE CIERRE DE SESIÓN
    # ============================================================================
    # Botón para cerrar sesión
    if st.button("Logout"):
        # Eliminar el token JWT de la sesión de Streamlit
        del st.session_state["token"]
        # Mostrar mensaje de confirmación
        st.success("Sesión cerrada exitosamente")
        # Recargar la página para volver a la pantalla de login
        st.rerun()
