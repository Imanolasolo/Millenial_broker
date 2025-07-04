import sqlite3
import os
from dbconfig import DB_FILE
from database_config import initialize_database, reset_database
import streamlit as st
import datetime as dt
import re
from assets.actividad_economica import actividad_economica_options

# Update the create_client function to handle all fields
def create_client(**data):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        # Validar longitud del número de documento
        if data['tipo_documento'].lower() == 'cedula' and len(data['numero_documento']) != 10:
            return "El número de cédula debe tener exactamente 10 dígitos."
        if data['tipo_documento'].lower() == 'ruc' and len(data['numero_documento']) != 13:
            return "El número de RUC debe tener exactamente 13 dígitos."

        # Verificar duplicados en nombres, apellidos, número de documento y correo electrónico
        cursor.execute(
            "SELECT * FROM clients WHERE nombres=? AND apellidos=? AND numero_documento=? AND correo_electronico=?",
            (data['nombres'], data['apellidos'], data['numero_documento'], data['correo_electronico'])
        )
        if cursor.fetchone():
            return f"El cliente con nombre '{data['nombres']} {data['apellidos']}', número de documento '{data['numero_documento']}' y correo '{data['correo_electronico']}' ya existe."

        # Insertar cliente si no hay duplicados
        fields = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        cursor.execute(f'''
            INSERT INTO clients ({fields})
            VALUES ({placeholders})
        ''', tuple(data.values()))
        conn.commit()
        # Mensaje personalizado según tipo_cliente
        if data.get("tipo_cliente") == "Empresa":
            nombre_cliente = data.get("razon_social", "Empresa sin nombre")
        else:
            nombre_cliente = f"{data.get('nombres', 'N/A')} {data.get('apellidos', 'N/A')}"
        return f"Cliente '{nombre_cliente}' creado exitosamente."
    except Exception as e:
        return f"Error al crear el cliente: {e}"
    finally:
        conn.close()

# Update the read_clients function to fetch all fields
def read_clients():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM clients")
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        conn.close()

# Update the update_client function to handle all fields
def update_client(email, **updates):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        fields = ', '.join([f"{field}=?" for field in updates.keys()])
        values = list(updates.values()) + [email]
        cursor.execute(f"UPDATE clients SET {fields} WHERE correo_electronico=?", values)
        conn.commit()
        return f"Cliente con correo '{email}' modificado exitosamente."
    except Exception as e:
        return f"Error al modificar el cliente: {e}"
    finally:
        conn.close()

# Update the delete_client function to delete by client ID
def delete_client(client_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
        if cursor.rowcount == 0:
            return f"No se encontró un cliente con ID '{client_id}'."
        conn.commit()
        return f"Cliente con ID '{client_id}' borrado exitosamente."
    except Exception as e:
        return f"Error al borrar el cliente: {e}"
    finally:
        conn.close()

# Add a function to reset the database
def reset_database():
    # Eliminar el archivo de la base de datos si existe y crear las tablas nuevamente
    reset_database()

def crud_clientes():
    st.subheader("Gestión de Clientes")
    operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Borrar"], key="crud_clientes_operation")

    if operation == "Crear":
        tipo_cliente = st.selectbox("Tipo de Cliente", ["Individual", "Empresa"])
        if tipo_cliente == "Individual":
            with st.form("form_cliente_individual"):
                tipo_documento = st.selectbox("Tipo de Documento", ["Cédula", "Pasaporte"])
                col1, col2 = st.columns(2)
                with col1:
                    nombres = st.text_input("Nombres (máx 50 caracteres)", key="cliente_nombres")
                with col2:
                    apellidos = st.text_input("Apellidos (máx 50 caracteres)")
                if nombres and len(nombres) > 50:
                    st.error("El campo 'Nombres' no puede exceder 50 caracteres.")
                if apellidos and len(apellidos) > 50:
                    st.error("El campo 'Apellidos' no puede exceder 50 caracteres.")
                col1, col2 = st.columns(2)
                with col1:
                    st.text(f"Tipo de Documento: {tipo_documento}")
                with col2:
                    numero_documento = st.text_input("Número de Cédula/Pasaporte")
                if tipo_documento == "Cédula" and numero_documento and len(numero_documento) != 10:
                    st.error("El número de Cédula debe tener exactamente 10 caracteres.")
                col1, col2 = st.columns(2)
                with col1:    
                    fecha_nacimiento = st.date_input(
                        "Fecha de Nacimiento",
                        min_value=dt.date(1900, 1, 1),
                        max_value=dt.date.today()
                    )
                if fecha_nacimiento > dt.date.today():
                    st.error("La fecha de nacimiento no puede ser mayor que hoy.")
                with col2:
                    nacionalidad = st.text_input("Nacionalidad")
                col1, col2 = st.columns(2)
                with col1:
                    genero = st.selectbox("Género", ["Masculino", "Femenino", "Otro"])
                with col2:
                    estado_civil = st.selectbox("Estado Civil", ["Soltero", "Casado", "Divorciado", "Viudo"])
                col1, col2, col3 = st.columns(3)
                with col1:
                    correo_electronico = st.text_input("Correo Electrónico Contacto")
                email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
                if correo_electronico and not re.match(email_pattern, correo_electronico):
                    st.error("El correo electrónico no tiene un formato válido.")
                with col2:
                    telefono1 = st.text_input("Teléfono 1")
                with col3:
                    telefono2 = st.text_input("Teléfono 2")
                phone_pattern = r"^\+593\d{9}$"
                if telefono1 and not re.match(phone_pattern, telefono1):
                    st.error("El Teléfono 1 debe tener el formato internacional +593XXXXXXXXX")
                if telefono2 and telefono2.strip() and not re.match(phone_pattern, telefono2):
                    st.error("El Teléfono 2 debe tener el formato internacional +593XXXXXXXXX")
                col1, col2, col3 = st.columns(3)
                with col1:
                    provincias_ecuador = [
                        "Azuay", "Bolívar", "Cañar", "Carchi", "Chimborazo", "Cotopaxi", "El Oro", "Esmeraldas",
                        "Galápagos", "Guayas", "Imbabura", "Loja", "Los Ríos", "Manabí", "Morona Santiago",
                        "Napo", "Orellana", "Pastaza", "Pichincha", "Santa Elena", "Santo Domingo de los Tsáchilas",
                        "Sucumbíos", "Tungurahua", "Zamora Chinchipe"
                    ]
                    provincia_ecuador = st.selectbox("Provincia (en caso de Ciudadano o residente ecuatoriano)", provincias_ecuador)
                with col2:
                    provincia_extranjero = st.text_input("Provincia (en caso de extranjero con Pasaporte)")
                with col3:
                    ciudad = st.text_input("Ciudad")
                direccion_domicilio = st.text_area("Dirección de Domicilio")
                col1, col2 = st.columns(2)
               
                with col1:
                    # Cambiar a selectbox usando las opciones importadas
                    actividad_economica = st.selectbox("Actividad Económica", actividad_economica_options)
                with col2:
                    subactividad_economica = st.text_input("Subactividad Económica")
                col1,col2 = st.columns(2)
                with col1:
                    fecha_registro = st.date_input("Fecha de Registro")
                with col2:
                    ultima_actualizacion = st.date_input("Última Actualización")
                # Página web eliminada para cliente individual
                # fecha_aniversario eliminada para cliente individual
                # fecha_aniversario = st.date_input("Fecha de Aniversario (opcional)", value=None)
                submitted = st.form_submit_button("Crear Cliente")
                if submitted:
                    provincia = ""
                    if tipo_documento == "Cédula":
                        provincia = provincia_ecuador
                    elif tipo_documento == "Pasaporte":
                        provincia = provincia_extranjero if provincia_extranjero.strip() else "Extranjero"
                    if (nombres and len(nombres) > 50) or (apellidos and len(apellidos) > 50):
                        st.error("El campo 'Nombres' y/o 'Apellidos' no puede exceder 50 caracteres.")
                    elif tipo_documento == "Cédula" and numero_documento and len(numero_documento) != 10:
                        st.error("El número de Cédula debe tener exactamente 10 caracteres.")
                    elif fecha_nacimiento > dt.date.today():
                        st.error("La fecha de nacimiento no puede ser mayor que hoy.")
                    elif correo_electronico and not re.match(email_pattern, correo_electronico):
                        st.error("El correo electrónico no tiene un formato válido.")
                    elif telefono1 and not re.match(phone_pattern, telefono1):
                        st.error("El Teléfono 1 debe tener el formato internacional +593XXXXXXXXX")
                    elif telefono2 and telefono2.strip() and not re.match(phone_pattern, telefono2):
                        st.error("El Teléfono 2 debe tener el formato internacional +593XXXXXXXXX")
                    elif nombres and apellidos and numero_documento and correo_electronico:
                        result = create_client(
                            tipo_cliente=tipo_cliente,
                            nombres=nombres,
                            apellidos=apellidos,
                            razon_social=None,
                            tipo_documento=tipo_documento,
                            numero_documento=numero_documento,
                            fecha_nacimiento=fecha_nacimiento.strftime("%Y-%m-%d"),
                            nacionalidad=nacionalidad,
                            sexo=genero,
                            estado_civil=estado_civil,
                            correo_electronico=correo_electronico,
                            telefono_movil=telefono1,
                            telefono_fijo=telefono2,
                            direccion_domicilio=direccion_domicilio,
                            provincia=provincia,
                            provincia_ecuador=provincia_ecuador,
                            provincia_extranjero=provincia_extranjero,
                            ciudad=ciudad,
                            # codigo_postal eliminado
                            # codigo_postal=codigo_postal,
                            actividad_economica=actividad_economica,
                            subactividad_economica=subactividad_economica,
                            ocupacion_profesion=None,
                            empresa_trabajo=None,
                            tipo_empresa=None,
                            ingresos_mensuales=None,
                            nivel_educacion=None,
                            fumador=None,
                            actividades_riesgo=None,
                            historial_medico=None,
                            historial_siniestros=None,
                            vehiculos_registrados=None,
                            propiedades=None,
                            tipo_contribuyente=None,
                            numero_ruc=None,
                            representante_legal_id=None,
                            observaciones_legales=None,
                            canal_preferido_contacto=None,
                            notas_adicionales=None,
                            fecha_registro=fecha_registro.strftime("%Y-%m-%d"),
                            ultima_actualizacion=ultima_actualizacion.strftime("%Y-%m-%d"),
                            # pagina_web=pagina_web,  # Eliminado para individual
                            # fecha_aniversario=fecha_aniversario.strftime("%Y-%m-%d") if fecha_aniversario else None, # Eliminado para individual
                            contacto_autorizado_id=None
                        )
                        st.success(result)
                    else:
                        st.error("Completa todos los campos obligatorios.")
        else:
            with st.form("form_cliente_empresa"):
                razon_social = st.text_input("Razón Social")
                col1, col2 = st.columns(2)
                with col1:
                    tipo_documento = st.selectbox("Tipo de Documento", ["RUC"])
                with col2:
                    numero_documento = st.text_input("Número de RUC")
                # Validación: RUC exactamente 13 dígitos
                if numero_documento and len(numero_documento) != 13:
                    st.warning("El Número de RUC debe tener exactamente 13 dígitos.")
                col1, col2 = st.columns(2)
                with col1:
                    representante_legal_id = st.text_input("ID Representante Legal")
                if representante_legal_id and (not representante_legal_id.isdigit() or len(representante_legal_id) != 10):
                    st.warning("El ID Representante Legal debe tener exactamente 10 dígitos numéricos.")
                with col2:
                    contacto_autorizado_id = st.text_input("ID Contacto Autorizado")
                if contacto_autorizado_id and (not contacto_autorizado_id.isdigit() or len(contacto_autorizado_id) != 10):
                    st.warning("El ID Contacto Autorizado debe tener exactamente 10 dígitos numéricos.")
                col1, col2 = st.columns(2)
                with col2:
                    correo_electronico = st.text_input("Correo Electrónico Contacto")
                with col1:
                    correo_empresa = st.text_input("Correo Empresa")
                email_pattern = r"^[^@]+@[^@]+\.[^@]+$"
                if correo_electronico and not re.match(email_pattern, correo_electronico):
                    st.error("El correo electrónico de contacto no tiene un formato válido.")
                if correo_empresa and not re.match(email_pattern, correo_empresa):
                    st.error("El correo empresa no tiene un formato válido.")
                # Teléfonos: Teléfono 1 y Teléfono 2
                col1, col2, col3 = st.columns(3)
                with col1:
                    telefono1 = st.text_input("Teléfono 1")
                with col2:
                    telefono2 = st.text_input("Teléfono 2")
                phone_pattern = r"^\+593\d{9}$"
                if telefono1 and not re.match(phone_pattern, telefono1):
                    st.error("El Teléfono 1 debe tener el formato internacional +593XXXXXXXXX")
                if telefono2 and telefono2.strip() and not re.match(phone_pattern, telefono2):
                    st.error("El Teléfono 2 debe tener el formato internacional +593XXXXXXXXX")
                with col3:
                    pagina_web = st.text_input("Página web")
                direccion_domicilio = st.text_area("Dirección de la Empresa")
                col1,col2,col3 = st.columns(3)
                with col1:
                    sector_mercado = st.selectbox(
                        "Sector/Mercado",
                        ["Publico", "Privado", "Mixto", "ONG", "Cooperativo", "Educativo", "Salud"]
                    )
                with col2:
                    tipo_empresa_categoria = st.selectbox(
                        "Tipo Empresa",
                        ["Microempresa", "Pequeña Empresa", "Mediana Empresa", "Gran Empresa"]
                    )
                with col3:
                    tipo_persona_juridica_options = [
                        "SCVS - Sociedad Anónima (S.A.)",
                        "SCVS - Compañía Ltda.",
                        "SCVS - S.A.S. (Sociedad por Acciones Simplificadas)",
                        "SCVS - Sucursal Extranjera",
                        "SCVS - Compañía en Comandita / Colectiva",
                        "SEPS - Cooperativa de Ahorro y Crédito",
                        "SEPS - Asociación",
                        "SEPS - Fundación",
                        "SB - Banco Privado",
                        "SB - Aseguradora",
                        "Otro - Empresa Pública",
                        "Otro - ONG",
                        "Otro - Institución Educativa"
                    ]
                    tipo_persona_juridica = st.selectbox(
                        "Tipo Persona Jurídica",
                        tipo_persona_juridica_options
                    )
                col1, col2 = st.columns(2)
                with col1:
                    # Cambiar a selectbox usando las opciones importadas
                    actividad_economica = st.selectbox("Actividad Económica", actividad_economica_options)
                with col2:
                    subactividad_economica = st.text_input("Subactividad Económica")
                col1, col2 = st.columns(2)
                with col1:
                    fecha_registro = st.date_input("Fecha de Registro")
                with col2:
                    ultima_actualizacion = st.date_input("Última Actualización")
                # fecha_aniversario eliminada para cliente empresa
                submitted = st.form_submit_button("Crear Cliente")
                if submitted:
                    if not (razon_social and numero_documento and correo_electronico):
                        st.error("Completa todos los campos obligatorios.")
                    elif len(numero_documento) != 13:
                        st.error("El Número de RUC debe tener exactamente 13 dígitos.")
                    elif representante_legal_id and (not representante_legal_id.isdigit() or len(representante_legal_id) != 10):
                        st.error("El ID Representante Legal debe tener exactamente 10 dígitos numéricos.")
                    elif contacto_autorizado_id and (not contacto_autorizado_id.isdigit() or len(contacto_autorizado_id) != 10):
                        st.error("El ID Contacto Autorizado debe tener exactamente 10 dígitos numéricos.")
                    elif telefono1 and not re.match(phone_pattern, telefono1):
                        st.error("El Teléfono 1 debe tener el formato internacional +593XXXXXXXXX")
                    elif telefono2 and telefono2.strip() and not re.match(phone_pattern, telefono2):
                        st.error("El Teléfono 2 debe tener el formato internacional +593XXXXXXXXX")
                    else:
                        result = create_client(
                            tipo_cliente=tipo_cliente,
                            nombres=None,
                            apellidos=None,
                            razon_social=razon_social,
                            tipo_documento=tipo_documento,
                            numero_documento=numero_documento,
                            fecha_nacimiento=None,
                            nacionalidad=None,
                            sexo=None,
                            estado_civil=None,
                            correo_electronico=correo_electronico,
                            correo_empresa=correo_empresa,
                            sector_mercado=sector_mercado,
                            tipo_empresa_categoria=tipo_empresa_categoria,
                            tipo_persona_juridica=tipo_persona_juridica,
                            actividad_economica=actividad_economica,
                            subactividad_economica=subactividad_economica,
                            telefono_movil=telefono1,
                            telefono_fijo=telefono2,
                            direccion_domicilio=direccion_domicilio,
                            pagina_web=pagina_web,
                            fecha_aniversario=None,
                            representante_legal_id=representante_legal_id,
                            contacto_autorizado_id=contacto_autorizado_id
                        )
                        st.success(result)
    elif operation == "Leer":
        st.header("Clientes Existentes")
        clients = read_clients()
        if clients:
            import pandas as pd
            df = pd.DataFrame(clients)
            st.dataframe(df)
        else:
            st.info("No hay clientes registrados.")

    elif operation == "Modificar":
        st.header("Modificar Cliente")
        clients = read_clients()
        if not clients:
            st.info("No hay clientes registrados.")
            return

        # Construir opciones para el selectbox
        client_options = []
        for client in clients:
            if client.get("tipo_cliente") == "Empresa":
                label = f"{client.get('razon_social', '')} (Empresa) [ID: {client['id']}]"
            else:
                label = f"{client.get('nombres', '')} {client.get('apellidos', '')} (Individual) [ID: {client['id']}]"
            client_options.append((client["id"], label))

        selected = st.selectbox("Selecciona un cliente para modificar", client_options, format_func=lambda x: x[1] if x else "")
        selected_id = selected[0] if selected else None
        selected_client = next((c for c in clients if c["id"] == selected_id), None)

        if selected_client:
            tipo_cliente = selected_client.get("tipo_cliente", "Individual")
            if tipo_cliente == "Individual":
                with st.form("form_modificar_cliente_individual"):
                    tipo_documento = st.selectbox("Tipo de Documento", ["Cédula", "Pasaporte"], index=["Cédula", "Pasaporte"].index(selected_client.get("tipo_documento", "Cédula")))
                    col1, col2 = st.columns(2)
                    with col1:
                        nombres = st.text_input("Nombres (máx 50 caracteres)", value=selected_client.get("nombres", ""), key="mod_cliente_nombres")
                    with col2:
                        apellidos = st.text_input("Apellidos (máx 50 caracteres)", value=selected_client.get("apellidos", ""), key="mod_cliente_apellidos")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.text(f"Tipo de Documento: {tipo_documento}")
                    with col2:
                        numero_documento = st.text_input("Número de Cédula/Pasaporte", value=selected_client.get("numero_documento", ""))
                    col1, col2 = st.columns(2)
                    with col1:
                        fecha_nacimiento = st.date_input(
                            "Fecha de Nacimiento",
                            value=selected_client.get("fecha_nacimiento", dt.date(2000, 1, 1)),
                            min_value=dt.date(1900, 1, 1),
                            max_value=dt.date.today()
                        )
                    with col2:
                        nacionalidad = st.text_input("Nacionalidad", value=selected_client.get("nacionalidad", ""))
                    col1, col2 = st.columns(2)
                    with col1:
                        genero = st.selectbox("Género", ["Masculino", "Femenino", "Otro"], index=["Masculino", "Femenino", "Otro"].index(selected_client.get("sexo", "Masculino")))
                    with col2:
                        estado_civil = st.selectbox("Estado Civil", ["Soltero", "Casado", "Divorciado", "Viudo"], index=["Soltero", "Casado", "Divorciado", "Viudo"].index(selected_client.get("estado_civil", "Soltero")))
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        correo_electronico = st.text_input("Correo Electrónico Contacto", value=selected_client.get("correo_electronico", ""))
                    with col2:
                        telefono1 = st.text_input("Teléfono 1", value=selected_client.get("telefono_movil", ""))
                    with col3:
                        telefono2 = st.text_input("Teléfono 2", value=selected_client.get("telefono_fijo", ""))
                    direccion_domicilio = st.text_area("Dirección de Domicilio", value=selected_client.get("direccion_domicilio", ""))
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        provincias_ecuador = [
                            "Azuay", "Bolívar", "Cañar", "Carchi", "Chimborazo", "Cotopaxi", "El Oro", "Esmeraldas",
                            "Galápagos", "Guayas", "Imbabura", "Loja", "Los Ríos", "Manabí", "Morona Santiago",
                            "Napo", "Orellana", "Pastaza", "Pichincha", "Santa Elena", "Santo Domingo de los Tsáchilas",
                            "Sucumbíos", "Tungurahua", "Zamora Chinchipe"
                        ]
                        provincia_ecuador = st.selectbox(
                            "Provincia (en caso de Ciudadano o residente ecuatoriano)",
                            provincias_ecuador,
                            index=provincias_ecuador.index(selected_client.get("provincia_ecuador", provincias_ecuador[0])) if selected_client.get("provincia_ecuador", "") in provincias_ecuador else 0
                        )
                    with col2:
                        provincia_extranjero = st.text_input(
                            "Provincia (en caso de extranjero con Pasaporte)",
                            value=selected_client.get("provincia_extranjera", "")
                        )
                    with col3:
                        ciudad = st.text_input("Ciudad", value=selected_client.get("ciudad", ""))
                    col1, col2 = st.columns(2)
                    with col1:
                        # Cambiar a selectbox usando las opciones importadas
                        actividad_actual = selected_client.get("actividad_economica", actividad_economica_options[0])
                        if actividad_actual in actividad_economica_options:
                            actividad_index = actividad_economica_options.index(actividad_actual)
                        else:
                            actividad_index = 0
                        actividad_economica = st.selectbox("Actividad Económica", actividad_economica_options, index=actividad_index)
                    with col2:
                        subactividad_economica = st.text_input("Subactividad Económica", value=selected_client.get("subactividad_economica", ""))
                    fecha_registro = st.date_input("Fecha de Registro", value=_parse_date(selected_client.get("fecha_registro")))
                    ultima_actualizacion = st.date_input("Última Actualización", value=_parse_date(selected_client.get("ultima_actualizacion")))
                    # Solución robusta para fecha_aniversario
                    fecha_aniversario = st.date_input(
                        "Fecha de Aniversario (opcional)",
                        value=_parse_date(selected_client.get("fecha_aniversario"))
                    )
                    submitted = st.form_submit_button("Actualizar Cliente")
                    if submitted:
                        provincia = ""
                        if tipo_documento == "Cédula":
                            provincia = provincia_ecuador
                        elif tipo_documento == "Pasaporte":
                            provincia = provincia_extranjero if provincia_extranjero.strip() else "Extranjero"
                        result = update_client(
                            selected_client.get("correo_electronico"),
                            tipo_cliente=tipo_cliente,
                            nombres=nombres,
                            apellidos=apellidos,
                            razon_social=None,
                            tipo_documento=tipo_documento,
                            numero_documento=numero_documento,
                            fecha_nacimiento=fecha_nacimiento.strftime("%Y-%m-%d"),
                            nacionalidad=nacionalidad,
                            sexo=genero,
                            estado_civil=estado_civil,
                            correo_electronico=correo_electronico,
                            telefono_movil=telefono1,
                            telefono_fijo=telefono2,
                            direccion_domicilio=direccion_domicilio,
                            provincia=provincia,
                            provincia_ecuador=provincia_ecuador,
                            provincia_extranjero=provincia_extranjero,
                            ciudad=ciudad,
                            # codigo_postal eliminado
                            # codigo_postal=codigo_postal,
                            actividad_economica=actividad_economica,
                            subactividad_economica=subactividad_economica,
                            ocupacion_profesion=None,
                            empresa_trabajo=None,
                            tipo_empresa=None,
                            ingresos_mensuales=None,
                            nivel_educacion=None,
                            fumador=None,
                            actividades_riesgo=None,
                            historial_medico=None,
                            historial_siniestros=None,
                            vehiculos_registrados=None,
                            propiedades=None,
                            tipo_contribuyente=None,
                            numero_ruc=None,
                            representante_legal_id=None,
                            observaciones_legales=None,
                            canal_preferido_contacto=None,
                            notas_adicionales=None,
                            fecha_registro=fecha_registro.strftime("%Y-%m-%d"),
                            ultima_actualizacion=ultima_actualizacion.strftime("%Y-%m-%d"),
                            # pagina_web=pagina_web,  # Eliminado para individual
                            fecha_aniversario=fecha_aniversario.strftime("%Y-%m-%d") if fecha_aniversario else None,
                            contacto_autorizado_id=None
                        )
                        st.success(result)
            else:
                with st.form("form_modificar_cliente_empresa"):
                    razon_social = st.text_input("Razón Social", value=selected_client.get("razon_social", ""))
                    col1, col2 = st.columns(2)
                    with col1:
                        tipo_documento = st.selectbox("Tipo de Documento", ["RUC"], index=0)
                    with col2:
                        numero_documento = st.text_input("Número de RUC", value=selected_client.get("numero_documento", ""))
                    col1, col2 = st.columns(2)
                    with col1:
                        representante_legal_id = st.text_input("ID Representante Legal", value=selected_client.get("representante_legal_id", ""))
                    with col2:
                        contacto_autorizado_id = st.text_input("ID Contacto Autorizado", value=selected_client.get("contacto_autorizado_id", ""))
                    col1, col2 = st.columns(2)
                    with col1:
                        correo_electronico = st.text_input("Correo Electrónico Contacto", value=selected_client.get("correo_electronico", ""))
                    with col2:
                        correo_empresa = st.text_input("Correo Empresa", value=selected_client.get("correo_empresa", ""))
                    col1,col2,col3 = st.columns(3)
                    with col1:
                        sector_mercado = st.selectbox(
                            "Sector/Mercado",
                            ["Publico", "Privado", "Mixto", "ONG", "Cooperativo", "Educativo", "Salud"],
                            index=["Publico", "Privado", "Mixto", "ONG", "Cooperativo", "Educativo", "Salud"].index(selected_client.get("sector_mercado", "Publico")) if selected_client.get("sector_mercado") in ["Publico", "Privado", "Mixto", "ONG", "Cooperativo", "Educativo", "Salud"] else 0
                        )
                    with col2:
                        tipo_empresa_categoria = st.selectbox(
                            "Tipo Empresa",
                            ["Microempresa", "Pequeña Empresa", "Mediana Empresa", "Gran Empresa"],
                            index=["Microempresa", "Pequeña Empresa", "Mediana Empresa", "Gran Empresa"].index(selected_client.get("tipo_empresa_categoria", "Microempresa")) if selected_client.get("tipo_empresa_categoria") in ["Microempresa", "Pequeña Empresa", "Mediana Empresa", "Gran Empresa"] else 0
                        )
                    with col3:
                        tipo_persona_juridica_options = [
                            "SCVS - Sociedad Anónima (S.A.)",
                            "SCVS - Compañía Ltda.",
                            "SCVS - S.A.S. (Sociedad por Acciones Simplificadas)",
                            "SCVS - Sucursal Extranjera",
                            "SCVS - Compañía en Comandita / Colectiva",
                            "SEPS - Cooperativa de Ahorro y Crédito",
                            "SEPS - Asociación",
                            "SEPS - Fundación",
                            "SB - Banco Privado",
                            "SB - Aseguradora",
                            "Otro - Empresa Pública",
                            "Otro - ONG",
                            "Otro - Institución Educativa"
                        ]
                        tipo_persona_juridica = st.selectbox(
                            "Tipo Persona Jurídica",
                            tipo_persona_juridica_options,
                            index=tipo_persona_juridica_options.index(selected_client.get("tipo_persona_juridica", tipo_persona_juridica_options[0])) if selected_client.get("tipo_persona_juridica") in tipo_persona_juridica_options else 0
                        )
                    col1, col2 = st.columns(2)
                    with col1:
                        # Cambiar a selectbox usando las opciones importadas
                        actividad_actual = selected_client.get("actividad_economica", actividad_economica_options[0])
                        if actividad_actual in actividad_economica_options:
                            actividad_index = actividad_economica_options.index(actividad_actual)
                        else:
                            actividad_index = 0
                        actividad_economica = st.selectbox("Actividad Económica", actividad_economica_options, index=actividad_index)
                    with col2:
                        subactividad_economica = st.text_input("Subactividad Económica", value=selected_client.get("subactividad_economica", ""))
                    telefono_fijo = st.text_input("Teléfono Fijo", value=selected_client.get("telefono_fijo", ""))
                    direccion_domicilio = st.text_area("Dirección de la Empresa", value=selected_client.get("direccion_domicilio", ""))
                    pagina_web = st.text_input("Página web", value=selected_client.get("pagina_web", ""))
                    fecha_aniversario = st.date_input("Fecha de Aniversario (opcional)", value=selected_client.get("fecha_aniversario", dt.date.today()))
                    submitted = st.form_submit_button("Actualizar Cliente")
                    if submitted:
                        result = update_client(
                            selected_client.get("correo_electronico"),
                            tipo_cliente=tipo_cliente,
                            nombres=None,
                            apellidos=None,
                            razon_social=razon_social,
                            tipo_documento=tipo_documento,
                            numero_documento=numero_documento,
                            fecha_nacimiento=None,
                            nacionalidad=None,
                            sexo=None,
                            estado_civil=None,
                            correo_electronico=correo_electronico,
                            correo_empresa=correo_empresa,
                            sector_mercado=sector_mercado,
                            tipo_empresa_categoria=tipo_empresa_categoria,
                            tipo_persona_juridica=tipo_persona_juridica,
                            actividad_economica=actividad_economica,
                            subactividad_economica=subactividad_economica,
                            telefono_fijo=telefono_fijo,
                            direccion_domicilio=direccion_domicilio,
                            pagina_web=pagina_web,
                            fecha_aniversario=fecha_aniversario.strftime("%Y-%m-%d") if fecha_aniversario else None,
                            representante_legal_id=representante_legal_id,
                            contacto_autorizado_id=contacto_autorizado_id
                        )
                        st.success(result)
    elif operation == "Borrar":
        st.header("Eliminar Cliente")
        clients = read_clients()
        if not clients:
            st.info("No hay clientes registrados.")
            return

        # Construir opciones para el selectbox
        client_options = []
        for client in clients:
            if client.get("tipo_cliente") == "Empresa":
                label = f"{client.get('razon_social', '')} (Empresa) [ID: {client['id']}]"
            else:
                label = f"{client.get('nombres', '')} {client.get('apellidos', '')} (Individual) [ID: {client['id']}]"
            client_options.append((client["id"], label))

        selected = st.selectbox("Selecciona un cliente para eliminar", client_options, format_func=lambda x: x[1] if x else "")
        selected_id = selected[0] if selected else None

        if st.button("Eliminar Cliente"):
            if selected_id:
                result = delete_client(selected_id)
                st.success(result)
            else:
                st.warning("Debes seleccionar un cliente para eliminar.")

# Añadir esta función utilitaria al principio del archivo (después de imports)
def _parse_date(val):
    import datetime
    if not val:
        return datetime.date.today()
    if isinstance(val, datetime.date):
        return val
    try:
        return datetime.datetime.strptime(val, "%Y-%m-%d").date()
    except Exception:
        try:
            return datetime.datetime.fromisoformat(val).date()
        except Exception:
            return datetime.date.today()