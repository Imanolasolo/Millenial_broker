# filepath: f:\CODECODIX\MILLENIAL_BROKER_project\dashboards\Back Office - Operacion_dashboard.py
# Dashboard para el rol: Back Office - Operacion

import streamlit as st
import sqlite3
from crud.user_crud import get_user_details
from dbconfig import DB_FILE

def welcome_message():
    st.markdown("### **Bienvenido al dashboard del rol: :red[Back Office - Operación]**")

def manage_modules():
    # Sidebar custom styles (same as admin_dashboard)
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            background-color: #3A92AB !important;
        }
        [data-testid="stSidebar"] button {
            background-color: white !important;
            color: black !important;
            border: 1px solid #007BFF !important;
        }
        [data-testid="stSidebar"] button:hover {
            background-color: #e6e6e6 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Sidebar con avatar, usuario y afiliación
    username = st.session_state.get("username")
    user_details = get_user_details(username) if username else None

    st.sidebar.image("assets/logo.png", width=80)
    st.sidebar.image("assets/avatar.png", width=100)
    st.sidebar.markdown(f"**Usuario:** {user_details['full_name'] if user_details and 'full_name' in user_details else username or 'Desconocido'}")
    st.sidebar.markdown(f"**Afiliación:** {user_details['company_name'] if user_details and 'company_name' in user_details else 'Sin afiliación'}")
    st.sidebar.markdown("---")

    # Sidebar: Gestión de módulos para Back Office
    st.sidebar.title("Módulos Back Office")
    modulo = st.sidebar.selectbox(
        "Selecciona un módulo",
        [
            "Gestión de Documentos",
            "Control de Operaciones",
            "Reportes",
            "Automatizaciones",
            "Configuración"
        ],
        key="backoffice_modulo"
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout"):
        del st.session_state["token"]
        st.success("Sesión cerrada exitosamente")
        st.rerun()

    st.write(f"### Módulo seleccionado: {modulo}")

    # Contenido principal según módulo seleccionado
    if modulo == "Gestión de Documentos":
        st.info("Aquí irá la gestión de documentos para Back Office.")
    elif modulo == "Control de Operaciones":
        st.info("Aquí irá el control de operaciones para Back Office.")
    elif modulo == "Reportes":
        st.info("Aquí irán los reportes para Back Office.")
    elif modulo == "Automatizaciones":
        st.subheader("Automatizaciones Back Office")
        automatizacion = st.selectbox(
            "Selecciona una automatización",
            [
                "Gestionar pólizas por cliente",
                "Crear póliza por cliente"
            ],
            key="backoffice_automatizacion"
        )

        if automatizacion == "Gestionar pólizas por cliente":
            # 1. Selección de cliente
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombres || ' ' || apellidos AS nombre_completo FROM clients")
            clientes = cursor.fetchall()
            conn.close()
            if not clientes:
                st.info("No hay clientes registrados.")
                return

            def cliente_format(x):
                if isinstance(x, (list, tuple)) and len(x) > 1:
                    return x[1]
                return str(x) if x else "Desconocido"

            cliente_seleccionado = st.selectbox("Selecciona un cliente", clientes, format_func=cliente_format)
            if cliente_seleccionado:
                # 2. Mostrar pólizas del cliente seleccionado
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, numero_poliza FROM polizas
                    WHERE cliente_id = ?
                """, (cliente_seleccionado[0],))
                polizas = cursor.fetchall()
                conn.close()

                if not polizas:
                    st.info("Este cliente no tiene pólizas registradas.")
                    return

                def poliza_format(x):
                    if isinstance(x, (list, tuple)) and len(x) > 1:
                        return x[1]
                    return str(x) if x else "Desconocido"

                poliza_seleccionada = st.selectbox("Selecciona una póliza para modificar", polizas, format_func=poliza_format)
                if poliza_seleccionada:
                    # 3. Mostrar y permitir modificar los datos de la póliza seleccionada
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT numero_poliza, tipo_poliza, cobertura, prima, fecha_inicio, fecha_fin, estado
                        FROM polizas WHERE id = ?
                    """, (poliza_seleccionada[0],))
                    datos = cursor.fetchone()
                    conn.close()
                    if datos:
                        numero_poliza = st.text_input("Número de Póliza", value=datos[0])
                        tipo_poliza = st.selectbox("Tipo de Póliza", ["Nueva", "Renovación"], index=["Nueva", "Renovación"].index(datos[1]) if datos[1] in ["Nueva", "Renovación"] else 0)
                        cobertura = st.text_area("Cobertura", value=datos[2])
                        prima = st.text_input("Prima", value=datos[3])
                        fecha_inicio = st.date_input("Fecha de Inicio Vigencia", value=datos[4])
                        fecha_fin = st.date_input("Fecha de Fin Vigencia", value=datos[5])
                        estado = st.selectbox("Estado", ["Activa", "Inactiva", "Cancelada"], index=["Activa", "Inactiva", "Cancelada"].index(datos[6]) if datos[6] in ["Activa", "Inactiva", "Cancelada"] else 0)

                        if st.button("Actualizar Póliza"):
                            conn = sqlite3.connect(DB_FILE)
                            cursor = conn.cursor()
                            try:
                                cursor.execute("""
                                    UPDATE polizas
                                    SET numero_poliza = ?, tipo_poliza = ?, cobertura = ?, prima = ?, fecha_inicio = ?, fecha_fin = ?, estado = ?
                                    WHERE id = ?
                                """, (
                                    numero_poliza, tipo_poliza, cobertura, prima,
                                    fecha_inicio.strftime("%Y-%m-%d"),
                                    fecha_fin.strftime("%Y-%m-%d"),
                                    estado, poliza_seleccionada[0]
                                ))
                                conn.commit()
                                st.success("Póliza actualizada exitosamente.")
                            except Exception as e:
                                st.error(f"Error al actualizar la póliza: {e}")
                            finally:
                                conn.close()
        elif automatizacion == "Crear póliza por cliente":
            st.subheader("Crear Póliza por Cliente")
            # Obtener lista de clientes
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id,
                    CASE
                        WHEN razon_social IS NOT NULL AND razon_social != ''
                            THEN razon_social
                        ELSE COALESCE(nombres, '') || ' ' || COALESCE(apellidos, '')
                    END AS nombre_completo
                FROM clients
            """)
            clientes = cursor.fetchall()
            cursor.execute("SELECT id, username, role FROM users")
            usuarios_roles = cursor.fetchall()
            cursor.execute("SELECT id, razon_social FROM aseguradoras")
            aseguradoras = cursor.fetchall()
            cursor.execute("SELECT id, nombre FROM ramos_seguros")
            ramos_seguros = cursor.fetchall()
            conn.close()

            usuarios = [(u[0], u[1]) for u in usuarios_roles]
            ejecutivos_comerciales = [(u[0], u[1]) for u in usuarios_roles if u[2] and u[2].strip().lower().replace(" ", "_") in ["ejecutivo_comercial", "seller"]]

            def cliente_format(x):
                if isinstance(x, (list, tuple)) and len(x) > 1:
                    return x[1]
                return str(x) if x else "Desconocido"

            def usuario_format(x):
                if isinstance(x, (list, tuple)) and len(x) > 1:
                    return x[1]
                return str(x) if x else "Desconocido"

            def aseguradora_format(x):
                if isinstance(x, (list, tuple)) and len(x) > 1:
                    return x[1]
                return str(x) if x else "Desconocido"

            def ramo_format(x):
                if isinstance(x, (list, tuple)) and len(x) > 1:
                    return x[1]
                return str(x) if x else "Desconocido"

            def ejecutivo_format(x):
                if isinstance(x, (list, tuple)) and len(x) > 1:
                    return x[1]
                return str(x) if x else "No hay ejecutivos comerciales"

            cliente_seleccionado = st.selectbox("Selecciona un Cliente", clientes, format_func=cliente_format, key="crear_poliza_cliente")
            usuario_seleccionado = st.selectbox("Selecciona un Gestor", usuarios, format_func=usuario_format, key="crear_poliza_gestor")
            aseguradora_seleccionada = st.selectbox("Selecciona una Aseguradora", aseguradoras, format_func=aseguradora_format, key="crear_poliza_aseguradora")
            ramo_seleccionado = st.selectbox("Selecciona un Ramo de Seguros", ramos_seguros, format_func=ramo_format, key="crear_poliza_ramo")
            ejecutivo_comercial_seleccionado = st.selectbox(
                "Selecciona un Ejecutivo Comercial",
                ejecutivos_comerciales if ejecutivos_comerciales else [("", "No hay ejecutivos comerciales")],
                format_func=ejecutivo_format,
                key="crear_poliza_ejecutivo"
            )

            numero_poliza = st.text_input("Número de Póliza", key="crear_poliza_numero")
            tipo_poliza = st.selectbox("Tipo de Póliza", ["Nueva", "Renovación"], key="crear_poliza_tipo")
            cobertura = st.text_area("Cobertura", key="crear_poliza_cobertura")
            prima = st.text_input("Prima", key="crear_poliza_prima")
            fecha_inicio_vigencia = st.date_input("Fecha de Inicio Vigencia", key="crear_poliza_inicio")
            fecha_fin_vigencia = st.date_input("Fecha de Fin Vigencia", key="crear_poliza_fin")
            estado = st.selectbox("Estado", ["Activa", "Inactiva", "Cancelada"], key="crear_poliza_estado")
            fecha_emision = st.date_input("Fecha de emisión", key="crear_poliza_emision")
            linea_negocio = st.text_input("Línea de negocio", key="crear_poliza_linea")
            suma_asegurada = st.text_input("Suma Asegurada", key="crear_poliza_suma")
            deducible = st.text_input("Deducible", key="crear_poliza_deducible")
            sucursal = st.text_input("Sucursal", key="crear_poliza_sucursal")
            tipo_facturacion = st.selectbox("Tipo de Facturación", ["Contado", "Débito", "Cuota Directa"], key="crear_poliza_facturacion")
            numero_factura = st.text_input("Nº de factura", key="crear_poliza_factura")
            numero_anexo = st.text_area("Nº de Anexo (puedes ingresar varios separados por coma o salto de línea)", key="crear_poliza_anexo")
            tipo_anexo = st.text_input("Tipo de anexo", key="crear_poliza_tipoanexo")

            if st.button("Crear Póliza", key="crear_poliza_btn"):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                try:
                    cursor.execute("""
                        INSERT INTO polizas (numero_poliza, cliente_id, usuario_id, aseguradora_id, ramo_id, tipo_poliza, cobertura, prima, fecha_inicio, fecha_fin, estado, fecha_emision, suma_asegurada, deducible, sucursal, tipo_facturacion, linea_negocio, numero_factura, numero_anexo, tipo_anexo, ejecutivo_comercial_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        numero_poliza, cliente_seleccionado[0], usuario_seleccionado[0], aseguradora_seleccionada[0], ramo_seleccionado[0],
                        tipo_poliza, cobertura, prima,
                        fecha_inicio_vigencia.strftime("%Y-%m-%d"),
                        fecha_fin_vigencia.strftime("%Y-%m-%d"),
                        estado, fecha_emision.strftime("%Y-%m-%d"), suma_asegurada, deducible, sucursal, tipo_facturacion, linea_negocio, numero_factura, numero_anexo, tipo_anexo, ejecutivo_comercial_seleccionado[0]
                    ))
                    conn.commit()
                    st.success("Póliza creada exitosamente")
                except sqlite3.IntegrityError:
                    st.error("El número de póliza ya existe o los datos seleccionados no son válidos.")
                finally:
                    conn.close()
    elif modulo == "Configuración":
        st.info("Aquí irá la configuración para Back Office.")

if __name__ == "__main__":
    welcome_message()
    manage_modules()