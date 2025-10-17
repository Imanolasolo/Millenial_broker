import streamlit as st
import sys
import os

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="Test Ramos CRUD", layout="wide")

st.title("🧪 Test - CRUD Ramos de Seguros")

# Test directo del módulo
try:
    from crud.ramos_crud import show_ramos_crud
    st.success("✅ Módulo ramos_crud importado correctamente")
    
    # Llamar directamente la función
    show_ramos_crud()
    
except ImportError as e:
    st.error(f"❌ Error de importación: {e}")
    st.info("Verificando estructura de archivos...")
    
    # Mostrar estructura de archivos
    current_dir = os.getcwd()
    st.code(f"Directorio actual: {current_dir}")
    
    # Verificar si existe la carpeta crud
    crud_path = os.path.join(current_dir, "crud")
    if os.path.exists(crud_path):
        st.success("✅ Carpeta 'crud' existe")
        
        # Verificar archivos en crud
        files = os.listdir(crud_path)
        st.write("Archivos en crud/:", files)
        
        ramos_file = os.path.join(crud_path, "ramos_crud.py")
        if os.path.exists(ramos_file):
            st.success("✅ Archivo 'ramos_crud.py' existe")
        else:
            st.error("❌ Archivo 'ramos_crud.py' no existe")
    else:
        st.error("❌ Carpeta 'crud' no existe")
        
except Exception as e:
    st.error(f"❌ Error general: {e}")
