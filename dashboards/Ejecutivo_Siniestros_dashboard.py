# Dashboard para el rol: Ejecutivo Siniestros
import streamlit as st
import sqlite3
import sys
import os

# Agregar el directorio padre al path si es necesario
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dbconfig import DB_FILE
except ImportError:
    # Si no puede importar, usar una ruta por defecto
    DB_FILE = "broker.db"
    st.warning("No se pudo importar dbconfig, usando base de datos por defecto")

# Importar funciones CRUD de siniestros
from crud.siniestro_crud import (
    create_siniestro, 
    read_siniestros, 
    update_siniestro, 
    delete_siniestro,
    get_siniestro_by_id
)

def welcome_message():
    st.header("Bienvenido al dashboard del rol: :red[Ejecutivo Siniestros]")

def manage_modules():
    # Selector en el sidebar para tipo de siniestro
    st.sidebar.markdown("---")
    st.sidebar.subheader("Tipo de Siniestro")
    tipo_siniestro = st.sidebar.radio(
        "Selecciona el área:",
        ["🚗 Siniestros de Vehículos", "❤️ Siniestros de Vida y Salud"],
        index=0
    )
    st.sidebar.markdown("---")
    
    # Mostrar módulos según el tipo seleccionado
    if tipo_siniestro == "🚗 Siniestros de Vehículos":
        gestionar_siniestros_vehiculos()
    else:
        gestionar_siniestros_vida_salud()
    
    # Botón de logout
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
        del st.session_state["token"]
        st.success("Sesión cerrada exitosamente")
        st.rerun()

def get_clients():
    """Obtiene la lista de clientes desde la base de datos"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombres, apellidos FROM clients ORDER BY nombres")
        clients = cursor.fetchall()
        conn.close()
        return clients
    except Exception as e:
        st.error(f"Error al obtener clientes: {str(e)}")
        return []

def get_policies_by_client(client_id):
    """Obtiene las pólizas de un cliente específico"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Primero obtener el nombre completo del cliente por su ID
        cursor.execute("SELECT nombres, apellidos FROM clients WHERE id = ?", (client_id,))
        client_data = cursor.fetchone()
        
        if not client_data:
            conn.close()
            return []
        
        # Construir el nombre completo del cliente
        client_full_name = f"{client_data[0]} {client_data[1]}"
        
        # Buscar pólizas que contengan el nombre del cliente en tomador_nombre
        cursor.execute("""
            SELECT p.id, p.numero_poliza, p.ramo_id, p.estado, 
                   COALESCE(a.razon_social, 'Sin aseguradora') as aseguradora
            FROM polizas p
            LEFT JOIN aseguradoras a ON p.aseguradora_id = a.id
            WHERE p.tomador_nombre LIKE ?
            ORDER BY p.numero_poliza
        """, (f"%{client_full_name}%",))
        policies = cursor.fetchall()
        conn.close()
        return policies
    except Exception as e:
        st.error(f"Error al obtener pólizas: {str(e)}")
        return []

def gestionar_siniestros_vehiculos():
    """
    Módulos y funcionalidades específicas para siniestros de vehículos
    """
    st.subheader("🚗 Gestión de Siniestros de Vehículos")
    
    opcion = st.selectbox(
        "Selecciona una opción:",
        [
            "Registrar Nuevo Siniestro",
            "Consultar Siniestros",
            "Actualizar Estado de Siniestro",
            "Gestionar Talleres",
            "Reportes de Siniestros Vehiculares"
        ]
    )
    
    if opcion == "Registrar Nuevo Siniestro":
        st.markdown("### Registrar Nuevo Siniestro Vehicular")
        
        # Obtener lista de clientes
        clients = get_clients()
        
        if not clients:
            st.warning("No hay clientes registrados en el sistema.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Selector de cliente
            client_options = {f"{c[1]} {c[2]} (ID: {c[0]})": c[0] for c in clients}
            selected_client = st.selectbox("Seleccionar Cliente", list(client_options.keys()))
            client_id = client_options[selected_client]
            
            # Obtener pólizas del cliente seleccionado
            policies = get_policies_by_client(client_id)
            
            if not policies:
                st.warning(f"El cliente seleccionado no tiene pólizas activas.")
                policy_id = None
            else:
                # Filtrar pólizas de vehículos
                # Verificar tanto si ramo_id es número (ID del ramo) como si es texto (nombre del ramo)
                vehicle_policies = [
                    p for p in policies 
                    if p[2] and (str(p[2]).strip() in ['77', '77.0'] or 
                                any(keyword in str(p[2]).lower() for keyword in ['vehicular', 'vehículo', 'auto', 'carro']))
                ]
                
                if not vehicle_policies:
                    st.warning("El cliente no tiene pólizas de vehículos activas.")
                    policy_id = None
                else:
                    policy_options = {
                        f"{p[1]} - Ramo: {p[2]} ({p[4]})": p[0] 
                        for p in vehicle_policies
                    }
                    selected_policy = st.selectbox("Seleccionar Póliza de Vehículo", list(policy_options.keys()))
                    policy_id = policy_options[selected_policy]
            
            placa = st.text_input("Placa del Vehículo")
            fecha_siniestro = st.date_input("Fecha del Siniestro")
            lugar = st.text_input("Lugar del Siniestro")
        
        with col2:
            tipo_dano = st.selectbox("Tipo de Daño", ["Choque", "Robo", "Incendio", "Vandalismo", "Otro"])
            descripcion = st.text_area("Descripción del Siniestro")
            monto_estimado = st.number_input("Monto Estimado del Daño", min_value=0.0, step=100.0)
            archivos = st.file_uploader("Cargar Fotos del Siniestro", accept_multiple_files=True)
        
        if st.button("💾 Registrar Siniestro", disabled=not policy_id):
            if policy_id:
                # Crear siniestro en la base de datos
                success, message, siniestro_id = create_siniestro(
                    poliza_id=policy_id,
                    cliente_id=client_id,
                    tipo_siniestro="Vehicular",
                    fecha_siniestro=fecha_siniestro.strftime('%Y-%m-%d'),
                    placa_vehiculo=placa,
                    lugar_siniestro=lugar,
                    tipo_dano=tipo_dano,
                    descripcion=descripcion,
                    monto_estimado=monto_estimado,
                    estado="En Proceso",
                    usuario_registro_id=st.session_state.get("user_id")
                )
                
                if success:
                    st.success(message)
                    st.balloons()
                else:
                    st.error(message)
            else:
                st.error("Debe seleccionar una póliza válida")
    
    elif opcion == "Consultar Siniestros":
        st.markdown("### Consultar Siniestros Vehiculares")
        siniestros = read_siniestros(tipo_siniestro="Vehicular")
        
        if siniestros:
            import pandas as pd
            df = pd.DataFrame(siniestros)
            st.dataframe(
                df[['codigo_siniestro', 'numero_poliza', 'nombres', 'apellidos', 'fecha_siniestro', 'estado', 'monto_estimado']],
                use_container_width=True
            )
        else:
            st.info("No hay siniestros vehiculares registrados")
    
    elif opcion == "Actualizar Estado de Siniestro":
        st.markdown("### Actualizar Estado de Siniestro")
        siniestro_id = st.selectbox("Seleccionar Siniestro", [s[0] for s in read_siniestros(tipo_siniestro="Vehicular")])
        nuevo_estado = st.selectbox("Nuevo Estado", ["En Proceso", "En Reparación", "Cerrado", "Rechazado"])
        observaciones = st.text_area("Observaciones")
        
        if st.button("✅ Actualizar Estado"):
            # Actualizar siniestro
            success, message = update_siniestro(
                siniestro_id=siniestro_id,
                estado=nuevo_estado,
                observaciones=observaciones,
                usuario_modificacion_id=st.session_state.get("user_id")
            )
            
            if success:
                st.success("Estado actualizado correctamente")
            else:
                st.error(message)
    
    elif opcion == "Gestionar Talleres":
        st.markdown("### Gestión de Talleres")
        st.info("Aquí se gestionarán los talleres asociados")
        # Lógica para gestionar talleres
    
    elif opcion == "Reportes de Siniestros Vehiculares":
        st.markdown("### Reportes y Estadísticas")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Siniestros Activos", "45")
        with col2:
            st.metric("Siniestros Cerrados", "120")
        with col3:
            st.metric("Pendientes de Revisión", "12")

def gestionar_siniestros_vida_salud():
    """
    Módulos y funcionalidades específicas para siniestros de vida y salud
    """
    st.subheader("❤️ Gestión de Siniestros de Vida y Salud")
    
    # Menú de opciones para vida y salud
    opcion = st.selectbox(
        "Selecciona una opción:",
        [
            "Registrar Nuevo Siniestro",
            "Consultar Siniestros",
            "Actualizar Estado de Siniestro",
            "Gestionar Clínicas/Hospitales",
            "Reportes de Siniestros Médicos"
        ]
    )
    
    if opcion == "Registrar Nuevo Siniestro":
        st.markdown("### Registrar Nuevo Siniestro de Vida/Salud")
        
        # Obtener lista de clientes
        clients = get_clients()
        
        if not clients:
            st.warning("No hay clientes registrados en el sistema.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Selector de cliente
            client_options = {f"{c[1]} {c[2]} (ID: {c[0]})": c[0] for c in clients}
            selected_client = st.selectbox("Seleccionar Cliente/Asegurado", list(client_options.keys()))
            client_id = client_options[selected_client]
            
            # Obtener pólizas del cliente seleccionado
            policies = get_policies_by_client(client_id)
            
            if not policies:
                st.warning(f"El cliente seleccionado no tiene pólizas activas.")
                policy_id = None
            else:
                # Filtrar pólizas de vida y salud
                health_policies = []
                for p in policies:
                    ramo_id_value = str(p[2]).strip() if p[2] else ""
                    
                    # Verificar si contiene palabras clave de vida/salud
                    if any(keyword in ramo_id_value.lower() for keyword in ['vida', 'salud', 'médico', 'hospitalización', 'seguro de vida']):
                        health_policies.append(p)
                
                if not health_policies:
                    st.warning("El cliente no tiene pólizas de vida/salud activas.")
                    policy_id = None
                else:
                    policy_options = {
                        f"{p[1]} - Ramo ID: {p[2]} ({p[4]})": p[0] 
                        for p in health_policies
                    }
                    selected_policy = st.selectbox("Seleccionar Póliza de Vida/Salud", list(policy_options.keys()))
                    policy_id = policy_options[selected_policy]
            
            st.date_input("Fecha del Evento")
            st.selectbox("Tipo de Cobertura", ["Hospitalización", "Cirugía", "Emergencia", "Consulta", "Fallecimiento"])
        
        with col2:
            st.text_input("Centro Médico")
            st.number_input("Monto Reclamado", min_value=0.0, step=100.0)
            st.text_area("Diagnóstico/Descripción")
            st.file_uploader("Cargar Documentos Médicos", accept_multiple_files=True)
        
        if st.button("💾 Registrar Siniestro", disabled=not policy_id):
            if policy_id:
                st.success(f"Siniestro de vida/salud registrado exitosamente para póliza ID: {policy_id}")
            else:
                st.error("Debe seleccionar una póliza válida")
    
    elif opcion == "Consultar Siniestros":
        st.markdown("### Consultar Siniestros de Vida y Salud")
        st.info("Aquí se mostrarán los siniestros médicos registrados")
        # Aquí irá la lógica para mostrar tabla de siniestros
    
    elif opcion == "Actualizar Estado de Siniestro":
        st.markdown("### Actualizar Estado de Siniestro")
        st.selectbox("Seleccionar Siniestro", ["SIN-SAL-001", "SIN-SAL-002"])
        st.selectbox("Nuevo Estado", ["En Revisión", "Aprobado", "Pagado", "Rechazado"])
        st.text_area("Observaciones Médicas")
        if st.button("✅ Actualizar Estado"):
            st.success("Estado actualizado correctamente")
    
    elif opcion == "Gestionar Clínicas/Hospitales":
        st.markdown("### Gestión de Centros Médicos")
        st.info("Aquí se gestionarán las clínicas y hospitales asociados")
        # Lógica para gestionar centros médicos
    
    elif opcion == "Reportes de Siniestros Médicos":
        st.markdown("### Reportes y Estadísticas")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Siniestros Activos", "32")
        with col2:
            st.metric("Siniestros Pagados", "95")
        with col3:
            st.metric("Monto Total Reclamado", "$45,000")
