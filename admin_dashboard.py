import streamlit as st
import sys
import os

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar el CRUD de ramos
try:
    from crud.ramos_crud import show_ramos_crud
except ImportError as e:
    st.error(f"Error al importar ramos_crud: {e}")
    show_ramos_crud = None

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Administrativo - Millennial Broker",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header principal
    st.markdown("""
    <div class="main-header">
        <h1>🏢 Dashboard Administrativo</h1>
        <p>Millennial Broker - Sistema de Gestión</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar para navegación
    st.sidebar.title("📋 Menú Principal")
    st.sidebar.markdown("---")
    
    # Opciones del menú
    menu_options = [
        "🏠 Dashboard Principal",
        "🛡️ Ramos de Seguros",
        "👥 Gestión de Usuarios", 
        "📊 Reportes",
        "💼 Pólizas",
        "🏢 Compañías Aseguradoras",
        "⚙️ Configuración"
    ]
    
    selected_option = st.sidebar.selectbox("Seleccionar módulo:", menu_options)
    
    # Mostrar información del usuario
    st.sidebar.markdown("---")
    st.sidebar.info("👤 **Usuario:** Administrador\n🕐 **Sesión activa**")
    
    # Contenido principal basado en la selección
    try:
        if selected_option == "🏠 Dashboard Principal":
            show_dashboard_home()
        elif selected_option == "🛡️ Ramos de Seguros":
            if show_ramos_crud:
                show_ramos_crud()
            else:
                st.error("Error: No se pudo cargar el módulo de Ramos de Seguros")
                st.info("Verifica que el archivo crud/ramos_crud.py existe y está correctamente configurado")
        elif selected_option == "👥 Gestión de Usuarios":
            show_users_management()
        elif selected_option == "📊 Reportes":
            show_reports()
        elif selected_option == "💼 Pólizas":
            show_policies_management()
        elif selected_option == "🏢 Compañías Aseguradoras":
            show_insurance_companies()
        elif selected_option == "⚙️ Configuración":
            show_settings()
    except Exception as e:
        st.error(f"Error al cargar el módulo: {str(e)}")
        st.info("Verifica que todos los archivos estén en su lugar correcto.")
        # Mostrar información de debug
        st.code(f"Current directory: {os.getcwd()}")
        st.code(f"Python path: {sys.path}")

def show_dashboard_home():
    """Mostrar la página principal del dashboard"""
    st.title("🏠 Dashboard Principal")
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📋 Total Pólizas",
            value="1,234",
            delta="12"
        )
    
    with col2:
        st.metric(
            label="👥 Clientes Activos", 
            value="856",
            delta="23"
        )
    
    with col3:
        st.metric(
            label="🛡️ Ramos Activos",
            value="40",
            delta="2"
        )
    
    with col4:
        st.metric(
            label="💰 Ingresos del Mes",
            value="$125,430",
            delta="8.2%"
        )
    
    st.markdown("---")
    
    # Gráficos y información adicional
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Tendencias de Ventas")
        st.line_chart({
            'Enero': 100,
            'Febrero': 120,
            'Marzo': 140,
            'Abril': 110,
            'Mayo': 160
        })
    
    with col2:
        st.subheader("🏆 Top Ramos de Seguros")
        st.bar_chart({
            'Vehículos': 45,
            'Vida Individual': 32,
            'Multiriesgo Hogar': 28,
            'Responsabilidad Civil': 22
        })

def show_users_management():
    """Gestión de usuarios"""
    st.title("👥 Gestión de Usuarios")
    st.info("Módulo de gestión de usuarios en desarrollo")

def show_reports():
    """Módulo de reportes"""
    st.title("📊 Reportes")
    st.info("Módulo de reportes en desarrollo")

def show_policies_management():
    """Gestión de pólizas"""
    st.title("💼 Gestión de Pólizas")
    st.info("Módulo de gestión de pólizas en desarrollo")

def show_insurance_companies():
    """Gestión de compañías aseguradoras"""
    st.title("🏢 Compañías Aseguradoras")
    st.info("Módulo de compañías aseguradoras en desarrollo")

def show_settings():
    """Configuración del sistema"""
    st.title("⚙️ Configuración del Sistema")
    st.info("Módulo de configuración en desarrollo")

if __name__ == "__main__":
    main()
