import streamlit as st
import sqlite3
from dbconfig import DB_FILE, initialize_database

def tipos_movimiento_permitidos():
    return [
        "Endoso de Beneficiario",
        "Anexo de Aumento de Suma Asegurada",
        "Anexo de Disminución de Suma Asegurada",
        "Inclusión de Direcciones",
        "Exclusión de Direcciones",
        "Anexo Aclaratorio",
        "Anexo de Aumento de Prima",
        "Anexo de Disminución de Prima",
        "Cancelación",
        "Anulación",
        "Rehabilitación",
        "Renovación"
    ]

    elif operation == "Aplicar a Póliza":
        st.markdown("### 🔄 Aplicar Movimiento a Póliza Madre")
        st.info("Esta función permite aplicar manualmente los cambios de un movimiento aprobado a la póliza madre.")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Obtener movimientos que pueden ser aplicados
        cursor.execute("""
            SELECT m.id, m.codigo_movimiento, m.tipo_movimiento, m.estado, m.fecha_movimiento,
                   p.numero_poliza, p.estado as poliza_estado,
                   c.nombres, c.apellidos, c.razon_social, c.tipo_cliente
            FROM movimientos_poliza m
            JOIN polizas p ON m.poliza_id = p.id
            JOIN clients c ON m.cliente_id = c.id
            WHERE m.estado IN ('Proceso', 'Aprobado')
            AND p.estado NOT IN ('Cancelada', 'Anulada', 'Vencida')
            ORDER BY m.fecha_movimiento DESC
        """)
        movimientos_aplicables = cursor.fetchall()
        
        if not movimientos_aplicables:
            st.warning("No hay movimientos pendientes que puedan ser aplicados a sus pólizas.")
            conn.close()
            return
        
        # Mostrar movimientos disponibles
        st.markdown(f"**Movimientos disponibles para aplicar:** {len(movimientos_aplicables)}")
        
        # Crear opciones para el selectbox
        opciones_movimientos = []
        for mov in movimientos_aplicables:
            cliente_nombre = mov[9] if mov[10] == "Persona Jurídica" else f"{mov[7]} {mov[8]}"
            opciones_movimientos.append((
                mov[0],  # ID
                f"{mov[1]} | {mov[2]} | {mov[5]} | {cliente_nombre} | {mov[4]} ({mov[3]})"
            ))
        
        selected_movimiento = st.selectbox(
            "Selecciona el movimiento a aplicar:",
            opciones_movimientos,
            format_func=lambda x: x[1]
        )
        
        if selected_movimiento:
            movimiento_id = selected_movimiento[0]
            
            # Obtener detalles completos del movimiento
            cursor.execute("SELECT * FROM movimientos_poliza WHERE id = ?", (movimiento_id,))
            detalle_movimiento = cursor.fetchone()
            
            if detalle_movimiento:
                # Mostrar detalles del movimiento
                with st.expander("📋 Detalles del Movimiento", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Código:** {detalle_movimiento[1]}")
                        st.write(f"**Tipo:** {detalle_movimiento[5]}")
                        st.write(f"**Fecha:** {detalle_movimiento[4]}")
                        st.write(f"**Estado Actual:** {detalle_movimiento[6]}")
                    with col2:
                        st.write(f"**Suma Asegurada Nueva:** {detalle_movimiento[7] or 'N/A'}")
                        st.write(f"**Prima Nueva:** {detalle_movimiento[8] or 'N/A'}")
                        st.write(f"**Dirección Nueva:** {detalle_movimiento[9] or 'N/A'}")
                    
                    if detalle_movimiento[11]:  # observaciones
                        st.write(f"**Observaciones:** {detalle_movimiento[11]}")
                
                # Verificar si puede ser aplicado
                puede_aplicar, mensaje_verificacion = verificar_puede_aplicar_movimiento(movimiento_id)
                
                if puede_aplicar:
                    st.success(f"✅ {mensaje_verificacion}")
                    
                    # Mostrar qué cambios se aplicarán
                    with st.expander("🔍 Cambios que se Aplicarán", expanded=True):
                        tipo_mov = detalle_movimiento[5]
                        
                        cambios_previstos = []
                        
                        if tipo_mov in ["Anexo de Aumento de Prima", "Anexo de Disminución de Prima", "Renovación"]:
                            if detalle_movimiento[8]:  # prima_nueva
                                cambios_previstos.append(f"🔸 **Prima:** Se actualizará a {detalle_movimiento[8]}")
                        
                        if tipo_mov in ["Anexo de Aumento de Suma Asegurada", "Anexo de Disminución de Suma Asegurada", "Renovación"]:
                            if detalle_movimiento[7]:  # suma_asegurada_nueva
                                cambios_previstos.append(f"🔸 **Suma Asegurada:** Se registrará {detalle_movimiento[7]} en observaciones")
                        
                        if tipo_mov in ["Cancelación", "Anulación"]:
                            nuevo_estado = "Cancelada" if tipo_mov == "Cancelación" else "Anulada"
                            cambios_previstos.append(f"🔸 **Estado de Póliza:** Cambiará a '{nuevo_estado}'")
                        
                        if tipo_mov == "Rehabilitación":
                            cambios_previstos.append(f"🔸 **Estado de Póliza:** Cambiará a 'Activa'")
                        
                        if cambios_previstos:
                            for cambio in cambios_previstos:
                                st.write(cambio)
                        else:
                            st.info("ℹ️ Este movimiento registrará su aplicación sin modificar campos específicos de la póliza.")
                    
                    # Confirmación para aplicar
                    st.markdown("---")
                    confirmar_aplicacion = st.checkbox("✅ Confirmo que deseo aplicar este movimiento a la póliza madre")
                    
                    if confirmar_aplicacion:
                        if st.button("🚀 APLICAR MOVIMIENTO A PÓLIZA", type="primary"):
                            # Preparar campos específicos
                            campos_para_aplicar = {}
                            if detalle_movimiento[7]:  # suma_asegurada_nueva
                                campos_para_aplicar["suma_asegurada_nueva"] = detalle_movimiento[7]
                            if detalle_movimiento[8]:  # prima_nueva
                                campos_para_aplicar["prima_nueva"] = detalle_movimiento[8]
                            if detalle_movimiento[9]:  # direccion_nueva
                                campos_para_aplicar["direccion_nueva"] = detalle_movimiento[9]
                            
                            # Aplicar el movimiento
                            exito, mensaje = aplicar_movimiento_a_poliza(
                                movimiento_id,
                                detalle_movimiento[5],  # tipo_movimiento
                                campos_para_aplicar,
                                detalle_movimiento[2]   # poliza_id
                            )
                            
                            if exito:
                                st.success(f"🎉 {mensaje}")
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(f"❌ {mensaje}")
                    else:
                        st.info("👆 Marque la confirmación para proceder con la aplicación.")
                
                else:
                    st.error(f"❌ {mensaje_verificacion}")
        
        conn.close()

    elif operation == "Borrar":ón de Prima",
        "Cancelación",
        "Anulación",
        "Rehabilitación",
        "Renovación"
    ]

def get_campos_por_tipo_movimiento(tipo_movimiento):
    """Retorna los campos específicos que se deben mostrar según el tipo de movimiento"""
    campos_mapping = {
        "Anexo de Aumento de Suma Asegurada": ["suma_asegurada_nueva"],
        "Anexo de Disminución de Suma Asegurada": ["suma_asegurada_nueva"],
        "Anexo de Aumento de Prima": ["prima_nueva"],
        "Anexo de Disminución de Prima": ["prima_nueva"],
        "Inclusión de Direcciones": ["direccion_nueva"],
        "Exclusión de Direcciones": ["direccion_nueva"],
        "Endoso de Beneficiario": [],  # No requiere campos adicionales específicos
        "Anexo Aclaratorio": [],
        "Cancelación": [],
        "Anulación": [],
        "Rehabilitación": [],
        "Renovación": ["suma_asegurada_nueva", "prima_nueva"]  # Puede incluir ambos
    }
    return campos_mapping.get(tipo_movimiento, [])

def render_campos_especificos(tipo_movimiento, valores_actuales=None):
    """Renderiza los campos específicos según el tipo de movimiento seleccionado"""
    campos = get_campos_por_tipo_movimiento(tipo_movimiento)
    valores = {}
    
    if not campos:
        st.info(f"El movimiento '{tipo_movimiento}' no requiere campos adicionales específicos.")
        return valores
    
    with st.expander(f"📋 Campos específicos para: {tipo_movimiento}", expanded=True):
        for campo in campos:
            if campo == "suma_asegurada_nueva":
                valor_actual = valores_actuales.get(campo, 0.0) if valores_actuales else 0.0
                valores[campo] = st.number_input(
                    "Nueva Suma Asegurada", 
                    min_value=0.0, 
                    value=float(valor_actual) if valor_actual else 0.0,
                    step=1000.0,
                    format="%.2f",
                    help="Ingrese la nueva suma asegurada para este movimiento"
                )
            elif campo == "prima_nueva":
                valor_actual = valores_actuales.get(campo, 0.0) if valores_actuales else 0.0
                valores[campo] = st.number_input(
                    "Nueva Prima", 
                    min_value=0.0, 
                    value=float(valor_actual) if valor_actual else 0.0,
                    step=100.0,
                    format="%.2f",
                    help="Ingrese la nueva prima para este movimiento"
                )
            elif campo == "direccion_nueva":
                valor_actual = valores_actuales.get(campo, "") if valores_actuales else ""
                valores[campo] = st.text_area(
                    "Nueva Dirección", 
                    value=str(valor_actual) if valor_actual else "",
                    height=100,
                    help="Ingrese la nueva dirección o las direcciones a incluir/excluir"
                )
    
    return valores

def aplicar_movimiento_a_poliza(movimiento_id, tipo_movimiento, campos_especificos, poliza_id):
    """Aplica los cambios del movimiento a la póliza madre según el tipo de movimiento"""
    if not campos_especificos:
        return True, "Movimiento aplicado (sin cambios específicos en la póliza)"
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Obtener información actual de la póliza
        cursor.execute("SELECT * FROM polizas WHERE id = ?", (poliza_id,))
        poliza_actual = cursor.fetchone()
        
        if not poliza_actual:
            return False, "No se encontró la póliza asociada"
        
        # Construir la consulta de actualización según el tipo de movimiento
        updates = []
        params = []
        cambios_aplicados = []
        
        if tipo_movimiento in ["Anexo de Aumento de Suma Asegurada", "Anexo de Disminución de Suma Asegurada", "Renovación"]:
            if "suma_asegurada_nueva" in campos_especificos and campos_especificos["suma_asegurada_nueva"]:
                # Nota: En este caso, asumiré que necesitamos agregar una columna suma_asegurada a la tabla polizas
                # o utilizar un campo existente para almacenar esta información
                # Por ahora, actualizaremos las observaciones con esta información
                nueva_suma = campos_especificos["suma_asegurada_nueva"]
                cambios_aplicados.append(f"Suma Asegurada: {nueva_suma}")
        
        if tipo_movimiento in ["Anexo de Aumento de Prima", "Anexo de Disminución de Prima", "Renovación"]:
            if "prima_nueva" in campos_especificos and campos_especificos["prima_nueva"]:
                updates.append("prima = ?")
                params.append(str(campos_especificos["prima_nueva"]))
                cambios_aplicados.append(f"Prima actualizada: {campos_especificos['prima_nueva']}")
        
        if tipo_movimiento in ["Cancelación", "Anulación"]:
            updates.append("estado = ?")
            params.append("Cancelada" if tipo_movimiento == "Cancelación" else "Anulada")
            cambios_aplicados.append(f"Estado cambiado a: {'Cancelada' if tipo_movimiento == 'Cancelación' else 'Anulada'}")
        
        if tipo_movimiento == "Rehabilitación":
            updates.append("estado = ?")
            params.append("Activa")
            cambios_aplicados.append("Estado cambiado a: Activa")
        
        # Agregar información de cambios a las observaciones
        if cambios_aplicados:
            cursor.execute("SELECT observaciones FROM polizas WHERE id = ?", (poliza_id,))
            observaciones_actuales = cursor.fetchone()[0] or ""
            
            nuevas_observaciones = observaciones_actuales
            if observaciones_actuales:
                nuevas_observaciones += "\n\n"
            
            import datetime
            fecha_aplicacion = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            nuevas_observaciones += f"[{fecha_aplicacion}] Movimiento aplicado - {tipo_movimiento}:\n"
            nuevas_observaciones += "\n".join([f"- {cambio}" for cambio in cambios_aplicados])
            
            updates.append("observaciones = ?")
            params.append(nuevas_observaciones)
        
        # Ejecutar la actualización si hay cambios
        if updates:
            params.append(poliza_id)
            query = f"UPDATE polizas SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()
        
        # Actualizar el estado del movimiento a "Aplicado"
        cursor.execute("""
            UPDATE movimientos_poliza 
            SET estado = 'Aplicado', 
                observaciones = COALESCE(observaciones, '') || '\n[APLICADO] Cambios aplicados a la póliza el ' || datetime('now', 'localtime')
            WHERE id = ?
        """, (movimiento_id,))
        conn.commit()
        
        mensaje_exito = f"Movimiento aplicado exitosamente. Cambios realizados: {', '.join(cambios_aplicados) if cambios_aplicados else 'Registro del movimiento'}"
        return True, mensaje_exito
        
    except sqlite3.Error as e:
        conn.rollback()
        return False, f"Error al aplicar el movimiento: {str(e)}"
    finally:
        conn.close()

def verificar_puede_aplicar_movimiento(movimiento_id):
    """Verifica si un movimiento puede ser aplicado a la póliza"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT m.estado, m.tipo_movimiento, p.estado as poliza_estado
            FROM movimientos_poliza m
            JOIN polizas p ON m.poliza_id = p.id
            WHERE m.id = ?
        """, (movimiento_id,))
        
        resultado = cursor.fetchone()
        if not resultado:
            return False, "Movimiento no encontrado"
        
        mov_estado, tipo_mov, poliza_estado = resultado
        
        if mov_estado == "Aplicado":
            return False, "El movimiento ya fue aplicado"
        
        if poliza_estado in ["Cancelada", "Anulada", "Vencida"]:
            return False, f"La póliza está en estado '{poliza_estado}' y no puede ser modificada"
        
        return True, "El movimiento puede ser aplicado"
        
    except sqlite3.Error as e:
        return False, f"Error al verificar el movimiento: {str(e)}"
    finally:
        conn.close()

def get_poliza_options():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, numero_poliza FROM polizas")
    polizas = cursor.fetchall()
    conn.close()
    return [(p[0], p[1]) for p in polizas]

def get_client_options():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombres, apellidos, razon_social, tipo_cliente FROM clients")
    clients = cursor.fetchall()
    conn.close()
    options = []
    for c in clients:
        if c[4] == "Persona Jurídica":
            label = f"{c[3]} (PJ) [ID: {c[0]}]"
        else:
            label = f"{c[1]} {c[2]} (PN) [ID: {c[0]}]"
        options.append((c[0], label))
    return options

def crud_movimientos():
    st.subheader("Gestión de Movimientos de Pólizas")
    col1, col2, col3 = st.columns(3)
    with col1:
        operation = st.selectbox("Selecciona una operación", ["Crear", "Leer", "Modificar", "Aplicar a Póliza", "Borrar"])

    # Reiniciar el proceso y los datos cada vez que se cambia de operación
    if "last_movimiento_operation" not in st.session_state or st.session_state["last_movimiento_operation"] != operation:
        st.session_state["movimiento_form_data"] = {}
        st.session_state["last_movimiento_operation"] = operation

    # Obtener columnas de la tabla movimientos_poliza
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(movimientos_poliza)")
    columns_info = cursor.fetchall()
    movimiento_fields = [col[1] for col in columns_info if col[1] != "id"]
    conn.close()

    if operation == "Crear":
        st.markdown("### 📝 Crear Nuevo Movimiento")
        
        # Campos básicos fuera del formulario para poder detectar cambios en tiempo real
        col1, col2 = st.columns(2)
        with col1:
            codigo_movimiento = st.text_input("Código único de movimiento")
            fecha_movimiento = st.date_input("Fecha de movimiento")
            tipo_movimiento = st.selectbox("Tipo de movimiento", tipos_movimiento_permitidos())
        
        with col2:
            poliza_options = get_poliza_options()
            poliza_id = st.selectbox("Póliza asociada", poliza_options, format_func=lambda x: x[1] if x else "", key="poliza_movimiento") if poliza_options else None
            client_options = get_client_options()
            cliente_id = st.selectbox("Cliente asociado", client_options, format_func=lambda x: x[1] if x else "", key="cliente_movimiento") if client_options else None
            estado = st.selectbox("Estado", ["Proceso", "Aprobado", "Aplicado"])
        
        # Renderizar campos específicos según el tipo de movimiento
        campos_especificos = render_campos_especificos(tipo_movimiento)
        
        # Campos adicionales
        with st.expander("📎 Información Adicional", expanded=False):
            pdf_path = st.text_input("Ruta/archivo PDF adjunto")
            observaciones = st.text_area("Observaciones del ejecutivo", height=100)
        
        # Opción para aplicar automáticamente
        with st.expander("⚙️ Opciones de Aplicación", expanded=True):
            aplicar_automaticamente = st.checkbox(
                "🔄 Aplicar cambios automáticamente a la póliza madre",
                value=False,
                help="Si está marcado, los cambios se aplicarán inmediatamente a la póliza cuando el estado sea 'Aprobado' o 'Aplicado'"
            )
            
            if aplicar_automaticamente:
                st.info("ℹ️ Los cambios se aplicarán automáticamente a la póliza madre según el tipo de movimiento seleccionado.")
                
                # Mostrar qué cambios se aplicarán
                if tipo_movimiento in ["Anexo de Aumento de Prima", "Anexo de Disminución de Prima", "Renovación"]:
                    st.write("🔸 **Se actualizará:** Prima de la póliza")
                if tipo_movimiento in ["Anexo de Aumento de Suma Asegurada", "Anexo de Disminución de Suma Asegurada", "Renovación"]:
                    st.write("🔸 **Se registrará:** Nueva suma asegurada en observaciones")
                if tipo_movimiento in ["Cancelación", "Anulación"]:
                    st.write("🔸 **Se actualizará:** Estado de la póliza")
                if tipo_movimiento == "Rehabilitación":
                    st.write("🔸 **Se actualizará:** Estado de la póliza a 'Activa'")
        
        # Botón de crear
        if st.button("✅ Crear Movimiento", type="primary"):
            if not codigo_movimiento:
                st.error("El código de movimiento es obligatorio.")
            elif not poliza_id:
                st.error("Debe seleccionar una póliza.")
            elif not cliente_id:
                st.error("Debe seleccionar un cliente.")
            else:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO movimientos_poliza 
                    (codigo_movimiento, fecha_movimiento, tipo_movimiento, poliza_id, cliente_id, 
                     pdf_documento, observaciones, estado, suma_asegurada_nueva, prima_nueva, direccion_nueva)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    codigo_movimiento,
                    fecha_movimiento.strftime("%Y-%m-%d"),
                    tipo_movimiento,
                    poliza_id[0] if poliza_id else None,
                    cliente_id[0] if cliente_id else None,
                    pdf_path,
                    observaciones,
                    estado,
                    campos_especificos.get("suma_asegurada_nueva"),
                    campos_especificos.get("prima_nueva"),
                    campos_especificos.get("direccion_nueva")
                ))
                
                # Obtener el ID del movimiento recién creado
                movimiento_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                # Aplicar automáticamente si está marcado y el estado lo permite
                if aplicar_automaticamente and estado in ["Aprobado", "Aplicado"]:
                    exito, mensaje = aplicar_movimiento_a_poliza(
                        movimiento_id, 
                        tipo_movimiento, 
                        campos_especificos, 
                        poliza_id[0] if poliza_id else None
                    )
                    
                    if exito:
                        st.success(f"✅ Movimiento creado y aplicado exitosamente.")
                        st.info(f"📋 {mensaje}")
                    else:
                        st.success("✅ Movimiento creado exitosamente.")
                        st.warning(f"⚠️ No se pudo aplicar automáticamente: {mensaje}")
                else:
                    st.success("✅ Movimiento creado exitosamente.")
                    if aplicar_automaticamente:
                        st.info("ℹ️ El movimiento se aplicará automáticamente cuando su estado cambie a 'Aprobado' o 'Aplicado'.")
                
                st.rerun()

    elif operation == "Leer":
        st.markdown("### 📊 Consultar Movimientos")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            filtro_tipo = st.selectbox("Filtrar por tipo", ["Todos"] + tipos_movimiento_permitidos())
        with col2:
            filtro_estado = st.selectbox("Filtrar por estado", ["Todos", "Proceso", "Aprobado", "Aplicado"])
        with col3:
            mostrar_campos_especificos = st.checkbox("Mostrar campos específicos", value=False)
        
        # Construir consulta con filtros
        query = """
            SELECT m.*, p.numero_poliza, c.nombres, c.apellidos, c.razon_social, c.tipo_cliente
            FROM movimientos_poliza m
            LEFT JOIN polizas p ON m.poliza_id = p.id
            LEFT JOIN clients c ON m.cliente_id = c.id
            WHERE 1=1
        """
        params = []
        
        if filtro_tipo != "Todos":
            query += " AND m.tipo_movimiento = ?"
            params.append(filtro_tipo)
        
        if filtro_estado != "Todos":
            query += " AND m.estado = ?"
            params.append(filtro_estado)
        
        query += " ORDER BY m.fecha_movimiento DESC"
        
        cursor.execute(query, params)
        movimientos = cursor.fetchall()
        conn.close()
        
        if movimientos:
            st.markdown(f"**Total de movimientos encontrados:** {len(movimientos)}")
            
            # Crear DataFrame con información enriquecida
            import pandas as pd
            
            columns = ['ID', 'Código', 'Póliza ID', 'Cliente ID', 'Fecha', 'Tipo', 'Estado', 
                      'Suma Asegurada Nueva', 'Prima Nueva', 'Dirección Nueva', 'PDF', 
                      'Observaciones', 'Usuario ID', 'Fecha Registro', 'Número Póliza', 
                      'Nombres', 'Apellidos', 'Razón Social', 'Tipo Cliente']
            
            df_data = []
            for mov in movimientos:
                # Crear nombre del cliente
                if mov[18] == "Persona Jurídica":  # tipo_cliente
                    cliente_nombre = mov[17] if mov[17] else "Sin nombre"  # razon_social
                else:
                    cliente_nombre = f"{mov[15]} {mov[16]}" if mov[15] and mov[16] else "Sin nombre"  # nombres apellidos
                
                row = list(mov[:14]) + [mov[14], cliente_nombre, mov[18]]  # Simplificar columnas
                df_data.append(row)
            
            # Columnas simplificadas para mejor visualización
            df_columns = ['ID', 'Código', 'Póliza ID', 'Cliente ID', 'Fecha', 'Tipo', 'Estado', 
                         'Suma Asegurada Nueva', 'Prima Nueva', 'Dirección Nueva', 'PDF', 
                         'Observaciones', 'Usuario ID', 'Fecha Registro', 'Número Póliza', 
                         'Cliente', 'Tipo Cliente']
            
            df = pd.DataFrame(df_data, columns=df_columns)
            
            # Configurar qué columnas mostrar
            if mostrar_campos_especificos:
                columnas_mostrar = ['Código', 'Número Póliza', 'Cliente', 'Fecha', 'Tipo', 'Estado', 
                                  'Suma Asegurada Nueva', 'Prima Nueva', 'Dirección Nueva']
            else:
                columnas_mostrar = ['Código', 'Número Póliza', 'Cliente', 'Fecha', 'Tipo', 'Estado']
            
            # Filtrar solo las columnas que existen
            columnas_disponibles = [col for col in columnas_mostrar if col in df.columns]
            df_mostrar = df[columnas_disponibles]
            
            st.dataframe(df_mostrar, use_container_width=True, hide_index=True)
            
            # Resumen por tipo de movimiento
            with st.expander("📈 Resumen por Tipo de Movimiento", expanded=False):
                resumen = df['Tipo'].value_counts()
                col1, col2 = st.columns(2)
                with col1:
                    st.bar_chart(resumen)
                with col2:
                    for tipo, cantidad in resumen.items():
                        st.write(f"**{tipo}:** {cantidad}")
            
            # Resumen por estado
            with st.expander("📊 Resumen por Estado", expanded=False):
                resumen_estado = df['Estado'].value_counts()
                st.bar_chart(resumen_estado)
                
        else:
            st.info("No hay movimientos registrados que coincidan con los filtros seleccionados.")

    elif operation == "Modificar":
        st.markdown("### ✏️ Modificar Movimiento")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, codigo_movimiento, tipo_movimiento FROM movimientos_poliza")
        movimientos = cursor.fetchall()
        if not movimientos:
            st.info("No hay movimientos registrados.")
            conn.close()
            return
        
        selected_movimiento = st.selectbox(
            "Selecciona un movimiento", 
            movimientos, 
            format_func=lambda x: f"{x[1]} - {x[2]} (ID: {x[0]})"
        )
        
        if selected_movimiento:
            cursor.execute("SELECT * FROM movimientos_poliza WHERE id=?", (selected_movimiento[0],))
            movimiento_actual = cursor.fetchone()
            conn.close()
            
            if not movimiento_actual:
                st.error("No se encontró el movimiento seleccionado.")
                return
            
            movimiento_dict = dict(zip([col[1] for col in columns_info], movimiento_actual))
            
            # Mostrar información actual
            with st.expander("ℹ️ Información Actual del Movimiento", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Código:** {movimiento_dict.get('codigo_movimiento', 'N/A')}")
                    st.write(f"**Tipo:** {movimiento_dict.get('tipo_movimiento', 'N/A')}")
                with col2:
                    st.write(f"**Fecha:** {movimiento_dict.get('fecha_movimiento', 'N/A')}")
                    st.write(f"**Estado:** {movimiento_dict.get('estado', 'N/A')}")
                with col3:
                    st.write(f"**Prima Nueva:** {movimiento_dict.get('prima_nueva', 'N/A')}")
                    st.write(f"**Suma Asegurada Nueva:** {movimiento_dict.get('suma_asegurada_nueva', 'N/A')}")
            
            # Campos básicos
            col1, col2 = st.columns(2)
            with col1:
                codigo_movimiento = st.text_input("Código único de movimiento", value=movimiento_dict.get("codigo_movimiento", ""))
                import datetime
                fecha_val = movimiento_dict.get("fecha_movimiento")
                try:
                    fecha_val = datetime.datetime.strptime(fecha_val, "%Y-%m-%d").date() if fecha_val else None
                except Exception:
                    fecha_val = None
                fecha_movimiento = st.date_input("Fecha de movimiento", value=fecha_val)
                
                tipos = tipos_movimiento_permitidos()
                tipo_actual = movimiento_dict.get("tipo_movimiento", tipos[0])
                tipo_index = tipos.index(tipo_actual) if tipo_actual in tipos else 0
                tipo_movimiento = st.selectbox("Tipo de movimiento", tipos, index=tipo_index)
            
            with col2:
                poliza_options = get_poliza_options()
                poliza_index = 0
                if movimiento_dict.get("poliza_id") and poliza_options:
                    try:
                        poliza_index = [p[0] for p in poliza_options].index(movimiento_dict.get("poliza_id"))
                    except ValueError:
                        poliza_index = 0
                poliza_id = st.selectbox("Póliza asociada", poliza_options, index=poliza_index, format_func=lambda x: x[1] if x else "")
                
                client_options = get_client_options()
                client_index = 0
                if movimiento_dict.get("cliente_id") and client_options:
                    try:
                        client_index = [c[0] for c in client_options].index(movimiento_dict.get("cliente_id"))
                    except ValueError:
                        client_index = 0
                cliente_id = st.selectbox("Cliente asociado", client_options, index=client_index, format_func=lambda x: x[1] if x else "")
                
                estados = ["Proceso", "Aprobado", "Aplicado"]
                estado_actual = movimiento_dict.get("estado", "Proceso")
                estado_index = estados.index(estado_actual) if estado_actual in estados else 0
                estado = st.selectbox("Estado", estados, index=estado_index)
            
            # Renderizar campos específicos según el tipo de movimiento
            campos_especificos = render_campos_especificos(tipo_movimiento, movimiento_dict)
            
            # Campos adicionales
            with st.expander("📎 Información Adicional", expanded=False):
                pdf_path = st.text_input("Ruta/archivo PDF adjunto", value=movimiento_dict.get("pdf_documento", ""))
                observaciones = st.text_area("Observaciones del ejecutivo", value=movimiento_dict.get("observaciones", ""), height=100)
            
            # Botón de actualizar
            if st.button("💾 Actualizar Movimiento", type="primary"):
                if not codigo_movimiento:
                    st.error("El código de movimiento es obligatorio.")
                elif not poliza_id:
                    st.error("Debe seleccionar una póliza.")
                elif not cliente_id:
                    st.error("Debe seleccionar un cliente.")
                else:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE movimientos_poliza SET
                            codigo_movimiento = ?,
                            fecha_movimiento = ?,
                            tipo_movimiento = ?,
                            poliza_id = ?,
                            cliente_id = ?,
                            pdf_documento = ?,
                            observaciones = ?,
                            estado = ?,
                            suma_asegurada_nueva = ?,
                            prima_nueva = ?,
                            direccion_nueva = ?
                        WHERE id = ?
                    """, (
                        codigo_movimiento,
                        fecha_movimiento.strftime("%Y-%m-%d"),
                        tipo_movimiento,
                        poliza_id[0] if poliza_id else None,
                        cliente_id[0] if cliente_id else None,
                        pdf_path,
                        observaciones,
                        estado,
                        campos_especificos.get("suma_asegurada_nueva"),
                        campos_especificos.get("prima_nueva"),
                        campos_especificos.get("direccion_nueva"),
                        selected_movimiento[0]
                    ))
                    conn.commit()
                    conn.close()
                    st.success("💾 Movimiento actualizado exitosamente.")
                    st.rerun()

    elif operation == "Borrar":
        st.markdown("### 🗑️ Eliminar Movimiento")
        st.warning("⚠️ **ADVERTENCIA:** Esta acción eliminará permanentemente el movimiento seleccionado y no se puede deshacer.")
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.id, m.codigo_movimiento, m.tipo_movimiento, m.fecha_movimiento, m.estado,
                   p.numero_poliza, c.nombres, c.apellidos, c.razon_social, c.tipo_cliente
            FROM movimientos_poliza m
            LEFT JOIN polizas p ON m.poliza_id = p.id
            LEFT JOIN clients c ON m.cliente_id = c.id
            ORDER BY m.fecha_movimiento DESC
        """)
        movimientos = cursor.fetchall()
        
        if not movimientos:
            st.info("No hay movimientos registrados para eliminar.")
            conn.close()
            return
        
        # Formato mejorado para mostrar los movimientos
        movimientos_options = []
        for mov in movimientos:
            cliente_nombre = mov[8] if mov[9] == "Persona Jurídica" else f"{mov[6]} {mov[7]}"
            movimientos_options.append((
                mov[0],  # ID
                f"{mov[1]} - {mov[2]} | {mov[5]} | {cliente_nombre} | {mov[3]} ({mov[4]})"
            ))
        
        selected_movimiento = st.selectbox(
            "Selecciona el movimiento a eliminar", 
            movimientos_options, 
            format_func=lambda x: x[1]
        )
        
        if selected_movimiento:
            # Obtener detalles completos del movimiento seleccionado
            cursor.execute("SELECT * FROM movimientos_poliza WHERE id = ?", (selected_movimiento[0],))
            detalle_movimiento = cursor.fetchone()
            
            if detalle_movimiento:
                with st.expander("📋 Detalles del Movimiento a Eliminar", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**ID:** {detalle_movimiento[0]}")
                        st.write(f"**Código:** {detalle_movimiento[1]}")
                        st.write(f"**Tipo:** {detalle_movimiento[5]}")
                        st.write(f"**Fecha:** {detalle_movimiento[4]}")
                        st.write(f"**Estado:** {detalle_movimiento[6]}")
                    with col2:
                        st.write(f"**Suma Asegurada Nueva:** {detalle_movimiento[7] or 'N/A'}")
                        st.write(f"**Prima Nueva:** {detalle_movimiento[8] or 'N/A'}")
                        st.write(f"**Dirección Nueva:** {detalle_movimiento[9] or 'N/A'}")
                        st.write(f"**PDF:** {detalle_movimiento[10] or 'Sin archivo'}")
                    
                    if detalle_movimiento[11]:  # observaciones
                        st.write(f"**Observaciones:** {detalle_movimiento[11]}")
            
            st.markdown("---")
            
            # Confirmaciones múltiples para mayor seguridad
            col1, col2 = st.columns(2)
            with col1:
                confirmar1 = st.checkbox("✅ Confirmo que he revisado los detalles del movimiento")
            with col2:
                confirmar2 = st.checkbox("✅ Confirmo que deseo eliminar este movimiento permanentemente")
            
            if confirmar1 and confirmar2:
                codigo_confirmacion = st.text_input(
                    f"Para confirmar, escriba el código del movimiento: **{detalle_movimiento[1]}**",
                    placeholder="Escriba el código aquí..."
                )
                
                if codigo_confirmacion == detalle_movimiento[1]:
                    if st.button("🗑️ ELIMINAR MOVIMIENTO DEFINITIVAMENTE", type="primary"):
                        try:
                            cursor.execute("DELETE FROM movimientos_poliza WHERE id = ?", (selected_movimiento[0],))
                            conn.commit()
                            st.success("✅ Movimiento eliminado exitosamente.")
                            st.balloons()
                            st.rerun()
                        except sqlite3.Error as e:
                            st.error(f"❌ Error al eliminar el movimiento: {str(e)}")
                elif codigo_confirmacion:
                    st.error("❌ El código ingresado no coincide. Verifique e intente nuevamente.")
            else:
                st.info("👆 Complete ambas confirmaciones para proceder con la eliminación.")
        
        conn.close()

