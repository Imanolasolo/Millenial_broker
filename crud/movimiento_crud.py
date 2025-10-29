import streamlit as st
import sqlite3
from dbconfig import DB_FILE, initialize_database
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import io
from datetime import datetime as dt, date

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
        "Renovación",
        "Aplicar"  # Nuevo movimiento
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
        "Endoso de Beneficiario": ["beneficiario"],
        "Anexo Aclaratorio": [],
        "Cancelación": [],
        "Anulación": [],
        "Rehabilitación": [],
        "Renovación": ["suma_asegurada_nueva", "prima_nueva"],
        "Aplicar": []  # Nuevo movimiento sin campos específicos
    }
    return campos_mapping.get(tipo_movimiento, [])

def obtener_datos_actuales_poliza(poliza_id):
    """Obtiene los datos actuales de la póliza para mostrar como referencia"""
    if not poliza_id:
        return None
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Obtener información básica de la póliza incluyendo suma_asegurada y prima_neta
        cursor.execute("""
            SELECT numero_poliza, prima_neta, cobertura, tipo_poliza, estado, observaciones, suma_asegurada
            FROM polizas 
            WHERE id = ?
        """, (poliza_id,))
        
        poliza_data = cursor.fetchone()
        if not poliza_data:
            return None
        
        # Obtener sumas aseguradas de los ramos asociados
        cursor.execute("""
            SELECT pr.suma_asegurada, rs.nombre, pr.prima
            FROM poliza_ramos pr
            JOIN ramos_seguros rs ON pr.ramo_id = rs.id
            WHERE pr.poliza_id = ?
        """, (poliza_id,))
        
        ramos_data = cursor.fetchall()
        
        # Calcular suma asegurada total
        suma_asegurada_total = 0
        prima_ramos_total = 0
        ramos_info = []
        
        for ramo in ramos_data:
            suma_str = str(ramo[0]).replace(',', '').replace('$', '') if ramo[0] else "0"
            prima_str = str(ramo[2]).replace(',', '').replace('$', '') if ramo[2] else "0"
            
            try:
                suma_valor = float(suma_str)
                prima_valor = float(prima_str)
                suma_asegurada_total += suma_valor
                prima_ramos_total += prima_valor
                
                ramos_info.append({
                    'ramo': ramo[1],
                    'suma_asegurada': suma_valor,
                    'prima': prima_valor
                })
            except ValueError:
                # Si no se puede convertir, usar 0
                ramos_info.append({
                    'ramo': ramo[1],
                    'suma_asegurada': 0,
                    'prima': 0
                })
        
        # Prima neta y suma asegurada de la póliza
        prima_neta_str = str(poliza_data[1]).replace(',', '').replace('$', '') if poliza_data[1] else "0"
        suma_asegurada_principal_str = str(poliza_data[6]).replace(',', '').replace('$', '') if poliza_data[6] else "0"
        
        try:
            prima_neta = float(prima_neta_str)
        except ValueError:
            prima_neta = 0
            
        try:
            suma_asegurada_principal = float(suma_asegurada_principal_str)
        except ValueError:
            suma_asegurada_principal = 0
        
        # Usar la suma asegurada principal si es mayor que la suma de ramos
        suma_asegurada_final = max(suma_asegurada_principal, suma_asegurada_total) if suma_asegurada_principal > 0 else suma_asegurada_total
        
        # Usar la prima neta principal si es mayor que la suma de primas de ramos
        prima_final = max(prima_neta, prima_ramos_total) if prima_neta > 0 else prima_ramos_total
        
        return {
            'numero_poliza': poliza_data[0],
            'prima_neta': prima_neta,
            'prima_final': prima_final,
            'suma_asegurada_principal': suma_asegurada_principal,
            'suma_asegurada_total': suma_asegurada_total,
            'suma_asegurada_final': suma_asegurada_final,
            'prima_ramos_total': prima_ramos_total,
            'cobertura': poliza_data[2],
            'tipo_poliza': poliza_data[3],
            'estado': poliza_data[4],
            'ramos_info': ramos_info,
            'observaciones': poliza_data[5]
        }
        
    except sqlite3.Error as e:
        st.error(f"Error al obtener datos de la póliza: {e}")
        return None
    finally:
        conn.close()

def render_campos_especificos(tipo_movimiento, valores_actuales=None, poliza_id=None):
    """Renderiza los campos específicos según el tipo de movimiento seleccionado"""
    campos = get_campos_por_tipo_movimiento(tipo_movimiento)
    valores = {}
    
    if not campos:
        st.info(f"El movimiento '{tipo_movimiento}' no requiere campos adicionales específicos.")
        return valores
    
    # Obtener datos actuales de la póliza para referencia
    poliza_datos = obtener_datos_actuales_poliza(poliza_id) if poliza_id else None
    
    with st.expander(f"📋 Campos específicos para: {tipo_movimiento}", expanded=True):
        
        # Mostrar información de referencia si está disponible
        if poliza_datos and campos:
            with st.container():
                st.markdown("#### 📊 **Información Actual de la Póliza (Referencia)**")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    if "suma_asegurada_nueva" in campos:
                        st.metric(
                            label="Suma Asegurada Actual",
                            value=f"${poliza_datos['suma_asegurada_final']:,.2f}",
                            help="Suma total asegurada actual de todos los ramos"
                        )
                        
                        # Mostrar desglose por ramos si hay múltiples
                        if len(poliza_datos['ramos_info']) > 1:
                            with st.expander("🔍 Desglose por Ramos", expanded=False):
                                for ramo_info in poliza_datos['ramos_info']:
                                    st.write(f"**{ramo_info['ramo']}:** ${ramo_info['suma_asegurada']:,.2f}")
                
                with col2:
                    if "prima_nueva" in campos:
                        # Mostrar prima principal si existe, sino la suma de ramos
                        prima_mostrar = poliza_datos['prima_final']
                        st.metric(
                            label="Prima Actual",
                            value=f"${prima_mostrar:,.2f}",
                            help="Prima actual de la póliza"
                        )
                        
                        # Mostrar desglose de primas por ramos si hay múltiples
                        if len(poliza_datos['ramos_info']) > 1 and poliza_datos['prima_ramos_total'] > 0:
                            with st.expander("🔍 Desglose Prima por Ramos", expanded=False):
                                for ramo_info in poliza_datos['ramos_info']:
                                    if ramo_info['prima'] > 0:
                                        st.write(f"**{ramo_info['ramo']}:** ${ramo_info['prima']:,.2f}")
                
                with col3:
                    st.metric(
                        label="Estado de la Póliza",
                        value=poliza_datos['estado'],
                        help="Estado actual de la póliza"
                    )
                    st.write(f"**Póliza:** {poliza_datos['numero_poliza']}")
                    st.write(f"**Tipo:** {poliza_datos['tipo_poliza']}")
                
                st.markdown("---")
        
        # Renderizar campos específicos
        for campo in campos:
            if campo == "beneficiario":
                beneficiario_actual = None
                if poliza_id:
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    try:
                        cursor.execute("SELECT beneficiario FROM polizas WHERE id = ?", (poliza_id,))
                        row = cursor.fetchone()
                        if row:
                            beneficiario_actual = row[0]
                    except Exception:
                        beneficiario_actual = None
                    finally:
                        conn.close()
                valores[campo] = st.text_input("Beneficiario de la póliza", value=beneficiario_actual or "")
            elif campo == "suma_asegurada_nueva":
                valor_actual = valores_actuales.get(campo, 0.0) if valores_actuales else 0.0
                help_text = "Ingrese la nueva suma asegurada para este movimiento"
                if poliza_datos:
                    help_text += f"\n💡 Suma actual: ${poliza_datos['suma_asegurada_final']:,.2f}"
                valores[campo] = st.number_input(
                    "Nueva Suma Asegurada", 
                    min_value=0.0, 
                    value=float(valor_actual) if valor_actual else 0.0,
                    step=1000.0,
                    format="%.2f",
                    help=help_text
                )
                if poliza_datos and valores[campo] > 0:
                    diferencia = valores[campo] - poliza_datos['suma_asegurada_final']
                    if diferencia != 0:
                        col_comp1, col_comp2 = st.columns(2)
                        with col_comp1:
                            if diferencia > 0:
                                st.success(f"📈 Aumento: ${diferencia:,.2f}")
                            else:
                                st.warning(f"📉 Disminución: ${abs(diferencia):,.2f}")
                        with col_comp2:
                            porcentaje = (diferencia / poliza_datos['suma_asegurada_final'] * 100) if poliza_datos['suma_asegurada_final'] > 0 else 0
                            st.info(f"📊 Cambio: {porcentaje:+.1f}%")
            elif campo == "prima_nueva":
                valor_actual = valores_actuales.get(campo, 0.0) if valores_actuales else 0.0
                prima_referencia = 0
                if poliza_datos:
                    prima_referencia = poliza_datos['prima_final']
                help_text = "Ingrese la nueva prima para este movimiento"
                if poliza_datos and prima_referencia > 0:
                    help_text += f"\n💡 Prima actual: ${prima_referencia:,.2f}"
                valores[campo] = st.number_input(
                    "Nueva Prima", 
                    min_value=0.0, 
                    value=float(valor_actual) if valor_actual else 0.0,
                    step=100.0,
                    format="%.2f",
                    help=help_text
                )
                if poliza_datos and prima_referencia > 0 and valores[campo] > 0:
                    diferencia = valores[campo] - prima_referencia
                    if diferencia != 0:
                        col_comp1, col_comp2 = st.columns(2)
                        with col_comp1:
                            if diferencia > 0:
                                st.success(f"📈 Aumento: ${diferencia:,.2f}")
                            else:
                                st.warning(f"📉 Disminución: ${abs(diferencia):,.2f}")
                        with col_comp2:
                            porcentaje = (diferencia / prima_referencia * 100) if prima_referencia > 0 else 0
                            st.info(f"📊 Cambio: {porcentaje:+.1f}%")
            elif campo == "direccion_nueva":
                valor_actual = valores_actuales.get(campo, "") if valores_actuales else ""
                if poliza_datos and poliza_datos['cobertura']:
                    st.markdown("**🏠 Cobertura Actual:**")
                    st.text_area(
                        "Cobertura/Direcciones Actuales (Solo Referencia)",
                        value=poliza_datos['cobertura'],
                        height=60,
                        disabled=True,
                        help="Esta es la cobertura actual de la póliza para su referencia"
                    )
                valores[campo] = st.text_area(
                    "Nueva Dirección/Cobertura", 
                    value=str(valor_actual) if valor_actual else "",
                    height=100,
                    help="Ingrese la nueva dirección o las direcciones a incluir/excluir"
                )
            else:
                valores[campo] = st.text_input(campo.replace("_", " ").capitalize(), value=valores_actuales.get(campo, "") if valores_actuales else "")
    return valores

def generar_pdf_movimiento(codigo_movimiento, fecha_movimiento, tipo_movimiento, poliza_info, cliente_info, campos_especificos, observaciones, estado):
    """Genera un PDF con la información del movimiento"""
    buffer = io.BytesIO()
    
    # Configurar el documento
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Obtener estilos
    styles = getSampleStyleSheet()
    
    # Crear estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    # Contenido del PDF
    story = []
    
    # Título principal
    story.append(Paragraph("MILLENIAL BROKER", title_style))
    story.append(Paragraph("Documento de Movimiento de Póliza", subtitle_style))
    story.append(Spacer(1, 20))
    
    # Información básica del movimiento
    story.append(Paragraph("INFORMACIÓN DEL MOVIMIENTO", subtitle_style))
    
    movimiento_data = [
        ['Código de Movimiento:', codigo_movimiento],
        ['Fecha del Movimiento:', fecha_movimiento.strftime("%d/%m/%Y") if isinstance(fecha_movimiento, date) else str(fecha_movimiento)],
        ['Tipo de Movimiento:', tipo_movimiento],
        ['Estado:', estado],
        ['Fecha de Generación:', dt.now().strftime("%d/%m/%Y %H:%M:%S")]
    ]
    
    movimiento_table = Table(movimiento_data, colWidths=[2.5*inch, 3.5*inch])
    movimiento_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(movimiento_table)
    story.append(Spacer(1, 20))
    
    # Información de la póliza
    if poliza_info:
        story.append(Paragraph("INFORMACIÓN DE LA PÓLIZA", subtitle_style))
        
        # Formatear prima y suma asegurada correctamente
        prima_formateada = f"${poliza_info.get('prima', 0):,.2f}" if isinstance(poliza_info.get('prima'), (int, float)) else f"${poliza_info.get('prima', 'N/A')}"
        suma_formateada = f"${poliza_info.get('suma_asegurada', 0):,.2f}" if isinstance(poliza_info.get('suma_asegurada'), (int, float)) else f"${poliza_info.get('suma_asegurada', 'N/A')}"
        
        poliza_data = [
            ['Número de Póliza:', poliza_info.get('numero_poliza', 'N/A')],
            ['Tipo de Póliza:', poliza_info.get('tipo_poliza', 'N/A')],
            ['Prima Actual:', prima_formateada],
            ['Suma Asegurada Actual:', suma_formateada],
            ['Estado de la Póliza:', poliza_info.get('estado', 'N/A')],
            ['Fecha de Inicio:', poliza_info.get('fecha_inicio', 'N/A')],
            ['Fecha de Fin:', poliza_info.get('fecha_fin', 'N/A')]
        ]
        
        poliza_table = Table(poliza_data, colWidths=[2.5*inch, 3.5*inch])
        poliza_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(poliza_table)
        story.append(Spacer(1, 20))
    
    # Información del cliente
    if cliente_info:
        story.append(Paragraph("INFORMACIÓN DEL CLIENTE", subtitle_style))
        
        if cliente_info.get('tipo_cliente') == 'Persona Jurídica':
            cliente_data = [
                ['Razón Social:', cliente_info.get('razon_social', 'N/A')],
                ['Tipo de Cliente:', cliente_info.get('tipo_cliente', 'N/A')],
                ['Documento:', f"{cliente_info.get('tipo_documento', '')} - {cliente_info.get('numero_documento', '')}"],
                ['Correo Electrónico:', cliente_info.get('correo_electronico', 'N/A')],
                ['Teléfono:', cliente_info.get('telefono_movil', 'N/A')]
            ]
        else:
            cliente_data = [
                ['Nombres:', f"{cliente_info.get('nombres', '')} {cliente_info.get('apellidos', '')}"],
                ['Tipo de Cliente:', cliente_info.get('tipo_cliente', 'N/A')],
                ['Documento:', f"{cliente_info.get('tipo_documento', '')} - {cliente_info.get('numero_documento', '')}"],
                ['Correo Electrónico:', cliente_info.get('correo_electronico', 'N/A')],
                ['Teléfono:', cliente_info.get('telefono_movil', 'N/A')]
            ]
        
        cliente_table = Table(cliente_data, colWidths=[2.5*inch, 3.5*inch])
        cliente_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgreen),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(cliente_table)
        story.append(Spacer(1, 20))
    
    # Campos específicos del movimiento
    if campos_especificos:
        story.append(Paragraph("DETALLES ESPECÍFICOS DEL MOVIMIENTO", subtitle_style))
        
        detalles_data = []
        for campo, valor in campos_especificos.items():
            if valor:
                campo_nombre = {
                    'suma_asegurada_nueva': 'Nueva Suma Asegurada',
                    'prima_nueva': 'Nueva Prima',
                    'direccion_nueva': 'Nueva Dirección'
                }.get(campo, campo)
                
                if campo == 'direccion_nueva':
                    # Para direcciones largas, usar párrafo
                    detalles_data.append([campo_nombre + ':', str(valor)])
                else:
                    valor_formateado = f"${valor:,.2f}" if isinstance(valor, (int, float)) else str(valor)
                    detalles_data.append([campo_nombre + ':', valor_formateado])
        
        if detalles_data:
            detalles_table = Table(detalles_data, colWidths=[2.5*inch, 3.5*inch])
            detalles_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightyellow),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ]))
            
            story.append(detalles_table)
            story.append(Spacer(1, 20))
    
    # Observaciones
    if observaciones:
        story.append(Paragraph("OBSERVACIONES", subtitle_style))
        story.append(Paragraph(observaciones, normal_style))
        story.append(Spacer(1, 20))
    
    # Pie de página
    story.append(Spacer(1, 30))
    story.append(Paragraph("___________________________", normal_style))
    story.append(Paragraph("Firma del Ejecutivo", normal_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Documento generado automáticamente el {dt.now().strftime('%d/%m/%Y a las %H:%M:%S')}", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey)))
    
    # Construir el PDF
    doc.build(story)
    
    # Obtener el contenido del buffer
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def obtener_info_completa_para_pdf(poliza_id, cliente_id):
    """Obtiene la información completa de póliza y cliente para el PDF"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    poliza_info = None
    cliente_info = None
    
    try:
        # Obtener información de la póliza usando la función que ya maneja los valores correctos
        if poliza_id:
            cursor.execute("SELECT * FROM polizas WHERE id = ?", (poliza_id,))
            poliza_row = cursor.fetchone()
            if poliza_row:
                cursor.execute("PRAGMA table_info(polizas)")
                poliza_columns = [col[1] for col in cursor.fetchall()]
                poliza_info = dict(zip(poliza_columns, poliza_row))
                
                # Obtener los datos actuales correctos para suma asegurada y prima
                datos_actuales = obtener_datos_actuales_poliza(poliza_id)
                if datos_actuales:
                    # Sobrescribir con los valores correctos
                    poliza_info['prima'] = datos_actuales['prima_final']
                    poliza_info['suma_asegurada'] = datos_actuales['suma_asegurada_final']
        
        # Obtener información del cliente
        if cliente_id:
            cursor.execute("SELECT * FROM clients WHERE id = ?", (cliente_id,))
            cliente_row = cursor.fetchone()
            if cliente_row:
                cursor.execute("PRAGMA table_info(clients)")
                cliente_columns = [col[1] for col in cursor.fetchall()]
                cliente_info = dict(zip(cliente_columns, cliente_row))
    
    except sqlite3.Error as e:
        st.error(f"Error al obtener información: {e}")
    finally:
        conn.close()
    
    return poliza_info, cliente_info

def aplicar_movimiento_a_poliza(movimiento_id, tipo_movimiento, campos_especificos, poliza_id, confirm_anulacion=False):
    """Aplica los cambios del movimiento a la póliza madre según el tipo de movimiento"""
    
    # Siempre aplicar al menos el tipo_movimiento y anexos, incluso sin campos específicos
    # if not campos_especificos and tipo_movimiento not in ["Cancelación", "Anulación", "Rehabilitación"]:
    #     return True, "Movimiento aplicado (sin cambios específicos en la póliza)"
    
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
        
        # Actualizar el tipo_movimiento en la póliza (para reflejar el último movimiento aplicado)
        updates.append("tipo_movimiento = ?")
        params.append(tipo_movimiento)
        cambios_aplicados.append(f"Tipo de movimiento actualizado: {tipo_movimiento}")
        st.write(f"✅ Tipo de movimiento será actualizado a: {tipo_movimiento}")

        # Si es Endoso de Beneficiario, actualizar el beneficiario
        if tipo_movimiento == "Endoso de Beneficiario" and "beneficiario" in campos_especificos:
            updates.append("beneficiario = ?")
            params.append(campos_especificos["beneficiario"])
            cambios_aplicados.append(f"Beneficiario actualizado: {campos_especificos['beneficiario']}")
            st.success(f"El beneficiario de la póliza ha sido actualizado a: {campos_especificos['beneficiario']}")

        # Manejar cambios de prima
        if tipo_movimiento in ["Anexo de Aumento de Prima", "Anexo de Disminución de Prima", "Renovación"]:
            if "prima_nueva" in campos_especificos and campos_especificos["prima_nueva"] is not None and campos_especificos["prima_nueva"] > 0:
                prima_valor = float(campos_especificos["prima_nueva"])
                updates.append("prima_neta = ?")
                params.append(prima_valor)
                cambios_aplicados.append(f"Prima neta actualizada: {prima_valor}")
                st.write(f"✅ Prima neta será actualizada a: {prima_valor}")
            else:
                st.write(f"❌ No se cumplieron las condiciones para actualizar prima")

        
        # Manejar cambios de estado (Cancelación / Anulación)
        if tipo_movimiento in ["Cancelación", "Anulación"]:
            nuevo_estado = "Cancelada" if tipo_movimiento == "Cancelación" else "Anulada"

            # Para 'Anulación' requerimos confirmación explícita (confirm_anulacion=True) antes de cambiar el estado
            if tipo_movimiento == "Anulación" and not confirm_anulacion:
                st.info("ℹ️ La anulación requiere confirmación explícita antes de cambiar el estado de la póliza.")
            else:
                # Siempre actualizar la columna canonical `estado`
                updates.append("estado = ?")
                params.append(nuevo_estado)
                cambios_aplicados.append(f"Estado cambiado a: {nuevo_estado}")

                # Intentar también mantener/sincronizar la columna legacy `estado_poliza`
                try:
                    cursor.execute("PRAGMA table_info(polizas)")
                    pol_cols = [r[1] for r in cursor.fetchall()]
                except Exception:
                    pol_cols = []

                if 'estado_poliza' in pol_cols:
                    updates.append("estado_poliza = ?")
                    params.append(nuevo_estado)
                else:
                    # Si no existe la columna legacy, intentar crearla y escribirla para compatibilidad
                    try:
                        cursor.execute("ALTER TABLE polizas ADD COLUMN estado_poliza TEXT")
                        # También actualizar la nueva columna con el mismo valor
                        updates.append("estado_poliza = ?")
                        params.append(nuevo_estado)
                    except sqlite3.Error:
                        # Si falla la alteración (por permisos o locking), simplemente continuar
                        pass
        
        if tipo_movimiento == "Rehabilitación":
            updates.append("estado = ?")
            params.append("Activa")
            cambios_aplicados.append("Estado cambiado a: Activa")

        # Manejar movimiento tipo 'Aplicar': activar póliza solo si está en 'Borrador'
        if tipo_movimiento == "Aplicar":
            try:
                cursor.execute("SELECT estado FROM polizas WHERE id = ?", (poliza_id,))
                fila_estado = cursor.fetchone()
                estado_actual_poliza = fila_estado[0] if fila_estado else None
            except Exception:
                estado_actual_poliza = None

            if estado_actual_poliza == "Borrador":
                updates.append("estado = ?")
                params.append("Activa")
                cambios_aplicados.append("Estado cambiado a: Activa (Aplicar)")
                st.success("✅ La póliza estaba en 'Borrador' y será activada.")
            else:
                st.info(f"ℹ️ La póliza está en estado '{estado_actual_poliza}' y no se activará (solo se activa si está en 'Borrador').")
        
        # Actualizar suma asegurada en la póliza y registrar en observaciones
        if tipo_movimiento in ["Anexo de Aumento de Suma Asegurada", "Anexo de Disminución de Suma Asegurada", "Renovación"]:
            if "suma_asegurada_nueva" in campos_especificos and campos_especificos["suma_asegurada_nueva"] is not None and campos_especificos["suma_asegurada_nueva"] > 0:
                suma_valor = float(campos_especificos["suma_asegurada_nueva"])
                updates.append("suma_asegurada = ?")
                params.append(suma_valor)
                cambios_aplicados.append(f"Suma asegurada actualizada: {suma_valor}")

        
        # Obtener código único del movimiento para actualizar anexos de la póliza
        cursor.execute("SELECT codigo_movimiento FROM movimientos_poliza WHERE id = ?", (movimiento_id,))
        resultado_codigo = cursor.fetchone()
        codigo_movimiento = resultado_codigo[0] if resultado_codigo else f"MOV-{movimiento_id}"
        st.write(f"� Código único del movimiento: **{codigo_movimiento}**")
        
        # Obtener anexos actuales de la póliza
        cursor.execute("SELECT anexos FROM polizas WHERE id = ?", (poliza_id,))
        resultado_anexos = cursor.fetchone()
        anexos_actuales = resultado_anexos[0] if resultado_anexos else ""
        st.write(f"� Anexos actuales de la póliza: **{anexos_actuales if anexos_actuales else '(Sin anexos)'}**")
        
        # Actualizar lista de anexos con el código único del movimiento
        if anexos_actuales in ["(Sin anexos)", "", None] or not anexos_actuales.strip():
            nuevos_anexos = codigo_movimiento
            st.success(f"🆕 **Primer anexo**: Estableciendo '{codigo_movimiento}' como anexo inicial")
        else:
            # Convertir la cadena de anexos en lista para verificar duplicados
            lista_anexos = [anexo.strip() for anexo in anexos_actuales.split(",")]
            
            if codigo_movimiento not in lista_anexos:
                nuevos_anexos = f"{anexos_actuales}, {codigo_movimiento}"
                st.success(f"➕ **Agregando anexo**: '{codigo_movimiento}' → Anexos: {nuevos_anexos}")
            else:
                nuevos_anexos = anexos_actuales  # Ya existe, no duplicar
                st.info(f"ℹ️ **Anexo existente**: '{codigo_movimiento}' ya está registrado en la póliza")
        
        updates.append("anexos = ?")
        params.append(nuevos_anexos)
        cambios_aplicados.append(f"Anexo registrado: {codigo_movimiento}")
        st.write(f"💾 **Campo anexos final**: `{nuevos_anexos}`")
        
        # Agregar información de cambios a las observaciones
        cursor.execute("SELECT observaciones FROM polizas WHERE id = ?", (poliza_id,))
        observaciones_actuales = cursor.fetchone()[0] or ""
        
        nuevas_observaciones = observaciones_actuales
        if observaciones_actuales:
            nuevas_observaciones += "\n\n"
        
        fecha_aplicacion = dt.now().strftime("%Y-%m-%d %H:%M:%S")
        nuevas_observaciones += f"[{fecha_aplicacion}] Movimiento aplicado - {tipo_movimiento}:\n"
        nuevas_observaciones += "\n".join([f"- {cambio}" for cambio in cambios_aplicados])
        
        updates.append("observaciones = ?")
        params.append(nuevas_observaciones)
        
        # Ejecutar la actualización si hay cambios

        
        if updates:
            params.append(poliza_id)
            query = f"UPDATE polizas SET {', '.join(updates)} WHERE id = ?"
            st.write(f"🚀 Ejecutando query: {query}")
            st.write(f"🚀 Con parámetros: {params}")
            cursor.execute(query, params)
            conn.commit()
            st.write(f"✅ Query ejecutada exitosamente")
        else:
            st.write(f"❌ No hay updates para aplicar - lista updates vacía")
        
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
        
        # Permitir aplicar movimientos de tipo 'Anulación' incluso si la póliza ya está en estados 'Cancelada'/'Anulada'/'Vencida'
        if tipo_mov != "Anulación" and poliza_estado in ["Cancelada", "Anulada", "Vencida"]:
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
            # Estado del movimiento oculto en la creación (por defecto 'Proceso')
            estado = "Proceso"
        
        # Renderizar campos específicos según el tipo de movimiento
        campos_especificos = render_campos_especificos(tipo_movimiento, None, poliza_id[0] if poliza_id else None)
        
        # Campos adicionales
        with st.expander("📎 Información Adicional", expanded=False):
            observaciones = st.text_area("Observaciones del ejecutivo", height=100)
            
            # Generación de PDF
            st.markdown("#### 📄 Documento PDF del Movimiento")
            
            if st.button("🎯 Vista Previa del PDF", help="Genera una vista previa del documento antes de crear el movimiento"):
                if codigo_movimiento and poliza_id and cliente_id and tipo_movimiento:
                    # Obtener información completa
                    poliza_info, cliente_info = obtener_info_completa_para_pdf(poliza_id[0], cliente_id[0])
                    
                    # Generar PDF
                    pdf_data = generar_pdf_movimiento(
                        codigo_movimiento=codigo_movimiento,
                        fecha_movimiento=fecha_movimiento,
                        tipo_movimiento=tipo_movimiento,
                        poliza_info=poliza_info,
                        cliente_info=cliente_info,
                        campos_especificos=campos_especificos,
                        observaciones=observaciones,
                        estado=estado
                    )
                    
                    # Mostrar botón de descarga
                    st.download_button(
                        label="📥 Descargar PDF de Vista Previa",
                        data=pdf_data,
                        file_name=f"Movimiento_{codigo_movimiento}_Vista_Previa.pdf",
                        mime="application/pdf",
                        help="Descarga el documento PDF del movimiento"
                    )
                    
                    st.success("✅ Vista previa del PDF generada exitosamente. Use el botón de arriba para descargar.")
                else:
                    st.warning("⚠️ Complete los campos básicos (código, póliza, cliente, tipo) para generar la vista previa.")
            
            st.info("💡 **Consejo:** Puede generar una vista previa del PDF antes de crear el movimiento para verificar que toda la información esté correcta.")
        
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
                # Generar nombre del archivo PDF
                pdf_filename = f"Movimiento_{codigo_movimiento}_{dt.now().strftime('%Y%m%d_%H%M%S')}.pdf"

                # Verificar unicidad del codigo_movimiento antes de intentar insertar
                try:
                    cursor.execute("SELECT COUNT(*) FROM movimientos_poliza WHERE codigo_movimiento = ?", (codigo_movimiento,))
                    if cursor.fetchone()[0] > 0:
                        conn.close()
                        st.error(f"Ya existe un movimiento con el código '{codigo_movimiento}'. Use un código único.")
                    else:
                        try:
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
                                pdf_filename,  # Guardamos el nombre del archivo PDF generado
                                observaciones,
                                estado,
                                campos_especificos.get("suma_asegurada_nueva"),
                                campos_especificos.get("prima_nueva"),
                                campos_especificos.get("direccion_nueva")
                            ))

                            # Obtener el ID del movimiento recién creado
                            movimiento_id = cursor.lastrowid
                            conn.commit()

                            # Generar PDF del movimiento creado
                            poliza_info, cliente_info = obtener_info_completa_para_pdf(poliza_id[0], cliente_id[0])
                            pdf_data = generar_pdf_movimiento(
                                codigo_movimiento=codigo_movimiento,
                                fecha_movimiento=fecha_movimiento,
                                tipo_movimiento=tipo_movimiento,
                                poliza_info=poliza_info,
                                cliente_info=cliente_info,
                                campos_especificos=campos_especificos,
                                observaciones=observaciones,
                                estado=estado
                            )

                            # Aplicar automáticamente si el estado es "Aplicado" o si está marcado y el estado lo permite.
                            # Además, si el tipo de movimiento es 'Aplicar' se considerará para aplicación inmediata
                            # (esto permite que seleccionar 'Aplicar' en la creación ejecute el cambio en la póliza).
                            if (
                                estado == "Aplicado"
                                or (aplicar_automaticamente and estado in ["Aprobado", "Aplicado"])
                                or (tipo_movimiento == "Aplicar" and poliza_id)
                                or (tipo_movimiento == "Endoso de Beneficiario" and poliza_id)
                                or (tipo_movimiento in ["Anexo de Aumento de Suma Asegurada", "Anexo de Disminución de Suma Asegurada", "Renovación"] and poliza_id)
                            ):
                                # Si es una Anulación y se aplica inmediatamente, pedir confirmación en la función
                                if tipo_movimiento == "Anulación":
                                    exito, mensaje = aplicar_movimiento_a_poliza(
                                        movimiento_id,
                                        tipo_movimiento,
                                        campos_especificos,
                                        poliza_id[0] if poliza_id else None,
                                        confirm_anulacion=True
                                    )
                                else:
                                    exito, mensaje = aplicar_movimiento_a_poliza(
                                        movimiento_id,
                                        tipo_movimiento,
                                        campos_especificos,
                                        poliza_id[0] if poliza_id else None
                                    )

                                if exito:
                                    st.success(f"✅ Movimiento creado y aplicado exitosamente a la póliza.")
                                    st.info(f"📋 {mensaje}")
                                else:
                                    st.success("✅ Movimiento creado exitosamente.")
                                    st.warning(f"⚠️ No se pudo aplicar automáticamente: {mensaje}")
                            else:
                                st.success("✅ Movimiento creado exitosamente.")
                                if aplicar_automaticamente:
                                    st.info("ℹ️ El movimiento se aplicará automáticamente cuando su estado cambie a 'Aprobado' o 'Aplicado'.")
                                elif estado == "Proceso":
                                    st.info("ℹ️ El movimiento está en proceso. Cambie el estado a 'Aplicado' para aplicar los cambios a la póliza.")

                            # Mostrar botón de descarga del PDF
                            st.markdown("---")
                            st.markdown("### 📄 Documento del Movimiento")
                            st.download_button(
                                label="📥 Descargar PDF del Movimiento",
                                data=pdf_data,
                                file_name=pdf_filename,
                                mime="application/pdf",
                                help="Descarga el documento oficial del movimiento en formato PDF"
                            )
                            st.info("📋 El documento PDF contiene toda la información del movimiento para sus archivos.")

                            # Esperar 3 segundos antes del rerun para dar tiempo a la descarga
                            import time
                            time.sleep(3)
                            st.rerun()
                        except sqlite3.IntegrityError as ie:
                            conn.rollback()
                            st.error(f"Error al crear movimiento: código duplicado o restricción de integridad. ({ie})")
                        except Exception as e:
                            conn.rollback()
                            st.error(f"Error al crear movimiento: {e}")
                        finally:
                            conn.close()
                except Exception:
                    conn.close()
                    st.error("Error verificando la unicidad del código de movimiento.")

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
            
            # Opción para descargar PDF de movimientos existentes
            with st.expander("📄 Generar PDF de Movimiento Existente", expanded=False):
                st.markdown("Seleccione un movimiento para generar y descargar su documento PDF:")
                
                # Crear opciones para el selectbox
                opciones_movimientos = []
                for i, mov in enumerate(movimientos):
                    opciones_movimientos.append((
                        mov[0],  # ID del movimiento
                        f"{mov[1]} - {mov[5]} | {mov[14]} | {mov[15]} ({mov[6]})"  # Código - Tipo | Póliza | Cliente (Estado)
                    ))
                
                if opciones_movimientos:
                    movimiento_seleccionado = st.selectbox(
                        "Movimiento:",
                        opciones_movimientos,
                        format_func=lambda x: x[1],
                        key="pdf_download_select"
                    )
                    
                    if st.button("🎯 Generar y Descargar PDF", key="generate_existing_pdf"):
                        # Buscar el movimiento seleccionado en la lista
                        mov_data = None
                        for mov in movimientos:
                            if mov[0] == movimiento_seleccionado[0]:
                                mov_data = mov
                                break
                        
                        if mov_data:
                            # Obtener información completa
                            poliza_info, cliente_info = obtener_info_completa_para_pdf(mov_data[2], mov_data[3])
                            
                            # Preparar campos específicos
                            campos_especificos = {}
                            if mov_data[7]:  # suma_asegurada_nueva
                                campos_especificos["suma_asegurada_nueva"] = mov_data[7]
                            if mov_data[8]:  # prima_nueva
                                campos_especificos["prima_nueva"] = mov_data[8]
                            if mov_data[9]:  # direccion_nueva
                                campos_especificos["direccion_nueva"] = mov_data[9]
                            
                            # Generar PDF
                            try:
                                # Convertir fecha string a objeto date
                                fecha_mov = dt.strptime(mov_data[4], "%Y-%m-%d").date()
                            except:
                                fecha_mov = mov_data[4]
                            
                            pdf_data = generar_pdf_movimiento(
                                codigo_movimiento=mov_data[1],
                                fecha_movimiento=fecha_mov,
                                tipo_movimiento=mov_data[5],
                                poliza_info=poliza_info,
                                cliente_info=cliente_info,
                                campos_especificos=campos_especificos,
                                observaciones=mov_data[11] or "",
                                estado=mov_data[6]
                            )
                            
                            # Mostrar botón de descarga
                            st.download_button(
                                label="📥 Descargar PDF del Movimiento",
                                data=pdf_data,
                                file_name=f"Movimiento_{mov_data[1]}_Regenerado.pdf",
                                mime="application/pdf",
                                help="Descarga el documento PDF del movimiento seleccionado",
                                key="download_regenerated_pdf"
                            )
                            
                            st.success("✅ PDF generado exitosamente. Use el botón de arriba para descargar.")
                        else:
                            st.error("❌ No se pudo encontrar el movimiento seleccionado.")
                else:
                    st.info("ℹ️ No hay movimientos disponibles para generar PDF.")
            
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
            -- Permitir movimientos de tipo 'Anulación' incluso si la póliza ya está en estados como Cancelada/Anulada/Vencida
            AND (
                p.estado NOT IN ('Cancelada', 'Anulada', 'Vencida')
                OR m.tipo_movimiento = 'Anulación'
            )
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
                            tipo_mov = detalle_movimiento[5]

                            # Si es una Anulación, mostrar el estado actual y pedir confirmación explícita
                            if tipo_mov == "Anulación":
                                try:
                                    cursor.execute("SELECT estado FROM polizas WHERE id = ?", (detalle_movimiento[2],))
                                    fila = cursor.fetchone()
                                    estado_actual_poliza = fila[0] if fila else "(desconocido)"
                                except Exception:
                                    estado_actual_poliza = "(desconocido)"

                                st.warning(f"La póliza seleccionada está actualmente en estado: '{estado_actual_poliza}'. ¿Desea cambiarla a 'Anulada'?")

                                col_yes, col_no = st.columns(2)
                                with col_yes:
                                    if st.button("Sí, ANULAR póliza", key=f"confirm_anular_{movimiento_id}"):
                                        exito, mensaje = aplicar_movimiento_a_poliza(
                                            movimiento_id,
                                            tipo_mov,
                                            campos_para_aplicar,
                                            detalle_movimiento[2],
                                            confirm_anulacion=True
                                        )
                                        if exito:
                                            st.success(f"🎉 {mensaje}")
                                            st.balloons()
                                            st.rerun()
                                        else:
                                            st.error(f"❌ {mensaje}")
                                with col_no:
                                    if st.button("No, cancelar anulación", key=f"cancel_anular_{movimiento_id}"):
                                        st.info("Anulación cancelada por el usuario.")
                            else:
                                exito, mensaje = aplicar_movimiento_a_poliza(
                                    movimiento_id,
                                    tipo_mov,
                                    campos_para_aplicar,
                                    detalle_movimiento[2]
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
                fecha_val = movimiento_dict.get("fecha_movimiento")
                try:
                    fecha_val = dt.strptime(fecha_val, "%Y-%m-%d").date() if fecha_val else None
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
                
                # Ocultar edición directa del estado en la modificación; usar flujos 'Aplicar a Póliza' para aplicar movimientos
                estado = movimiento_dict.get("estado", "Proceso")
            
            # Renderizar campos específicos según el tipo de movimiento
            campos_especificos = render_campos_especificos(tipo_movimiento, movimiento_dict, poliza_id[0] if poliza_id else None)
            
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
                    # Verificar si el estado requiere aplicación a la póliza
                    estado_anterior = movimiento_dict.get("estado", "")
                    aplicar_cambios = False
                    
                    if estado in ["Aprobado", "Aplicado"]:
                        if estado_anterior not in ["Aprobado", "Aplicado"]:
                            aplicar_cambios = True
                            st.info(f"🔄 **Cambio de estado detectado**: '{estado_anterior}' → '{estado}'. Se aplicarán los cambios a la póliza.")
                        else:
                            # También aplicar si ya está en estado aplicable pero se está re-aplicando
                            aplicar_cambios = True
                            st.info(f"🔄 **Estado '{estado}' confirmado**. Se aplicarán/verificarán los cambios en la póliza.")
                    
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

                    # Si el movimiento es un Endoso de Beneficiario o un Anexo/ Renovación de suma/prima, aplicar inmediatamente
                    if tipo_movimiento in ("Endoso de Beneficiario", "Anexo de Aumento de Suma Asegurada", "Anexo de Disminución de Suma Asegurada", "Renovación"):
                        st.info(f"🔄 Aplicando {tipo_movimiento} a la póliza...")
                        try:
                            exito, mensaje_aplicar = aplicar_movimiento_a_poliza(
                                selected_movimiento[0],
                                tipo_movimiento,
                                campos_especificos,
                                poliza_id[0] if poliza_id else None
                            )
                            if exito:
                                st.success(f"✅ {tipo_movimiento} aplicado correctamente: {mensaje_aplicar}")
                            else:
                                st.warning(f"⚠️ No se pudo aplicar automáticamente: {mensaje_aplicar}")
                        except Exception as e:
                            st.error(f"❌ Error al aplicar automáticamente: {e}")
                    
                    # Aplicar cambios a la póliza si el estado cambió a Aprobado/Aplicado
                    if aplicar_cambios:
                        st.info("� Aplicando cambios del movimiento a la póliza madre...")
                        

                        st.write(f"   - selected_movimiento[0]: {selected_movimiento[0]}")
                        st.write(f"   - tipo_movimiento: {tipo_movimiento}")
                        # Si el movimiento es una Anulación y el estado cambió a Aplicado/Aprobado,
                        # asumimos que la actualización vino del usuario y permitimos la anulación inmediata.
                        if tipo_movimiento == "Anulación":
                            exito, mensaje = aplicar_movimiento_a_poliza(
                                selected_movimiento[0],
                                tipo_movimiento,
                                campos_especificos,
                                poliza_id[0] if poliza_id else None,
                                confirm_anulacion=True
                            )
                        else:
                            exito, mensaje = aplicar_movimiento_a_poliza(
                                selected_movimiento[0],
                                tipo_movimiento,
                                campos_especificos,
                                poliza_id[0] if poliza_id else None
                            )
                        
                        if exito:
                            st.success("💾 Movimiento actualizado exitosamente.")
                            st.success(f"✅ **Anexos y cambios aplicados a la póliza:** {mensaje}")
                        else:
                            st.success("💾 Movimiento actualizado exitosamente.")
                            st.warning(f"⚠️ No se pudieron aplicar los cambios automáticamente: {mensaje}")
                    else:
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