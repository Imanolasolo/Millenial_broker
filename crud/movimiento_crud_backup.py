"""
Archivo limpiado: se ha eliminado la implementación de obtención y gestión de movimientos
por petición del usuario. Este módulo ahora deja un placeholder informativo para evitar
que la UI muestre el sidebar o funcionalidad relacionada con movimientos.

Si necesita restaurar el comportamiento previo, consulte el archivo de respaldo o el
historial de git: `movimiento_crud_backup.py` (versión anterior) o el commit correspondiente.
"""

import streamlit as st

def crud_movimientos():
    """Placeholder: la gestión de movimientos ha sido removida.

    Esta función mantiene la API (llamada desde otras partes del proyecto) pero no
    renderiza ni ejecuta ninguna operación sobre la base de datos.
    """
    st.warning(
        "La gestión de movimientos ha sido eliminada de este archivo. "
        "Si la necesitas, restaura `movimiento_crud_backup.py` desde el historial de git."
    )
    return

__all__ = ["crud_movimientos"]

