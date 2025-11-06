import streamlit as st
import sqlite3
from dbconfig import DB_FILE
import datetime


def aumento_suma_asegurada():
    """Expander para crear un movimiento de Anexo de Aumento de Suma Asegurada.

    Muestra un expander con un selector que lista solo las pólizas con estado 'Activa'.
    Permite introducir código de movimiento y nueva suma asegurada.
    Al crear, inserta un registro en `movimientos_poliza` con tipo
    'Anexo de Aumento de Suma Asegurada' y deja el movimiento en estado 'Proceso'.
    """

    # Obtener pólizas activas
    polizas_activas = []
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT id, numero_poliza FROM polizas WHERE estado = 'Activa' ORDER BY id DESC")
        rows = cur.fetchall()
        for r in rows:
            polizas_activas.append((r[0], r[1]))
    except Exception as e:
        st.error(f"Error al leer pólizas activas: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass

    with st.expander("Aumento de Suma Asegurada", expanded=True):
        # Código del nuevo movimiento (input antes del selector, como en otros movimientos)
        codigo_movimiento = st.text_input("Código de nuevo movimiento", help="Ingrese el código identificador para el movimiento")

        # Mostrar únicamente el selector de póliza (solo activas) por ahora
        if not polizas_activas:
            st.info('No hay pólizas ACTIVAS disponibles para este movimiento.')
            return

        selected = st.selectbox('Seleccione la póliza a la que aplicar el anexo (solo activas):', polizas_activas, format_func=lambda x: x[1])

        # Mostrar suma asegurada y prima actuales de la póliza seleccionada
        suma_actual = None
        prima_actual = None
        try:
            conn4 = sqlite3.connect(DB_FILE)
            cur4 = conn4.cursor()
            # Detectar columnas disponibles para evitar errores si el esquema varía
            cur4.execute("PRAGMA table_info(polizas)")
            pol_cols = [c[1] for c in cur4.fetchall()]

            select_cols = []
            if 'suma_asegurada' in pol_cols:
                select_cols.append('suma_asegurada')
            # preferir prima_neta si existe, sino prima
            if 'prima_neta' in pol_cols:
                select_cols.append('prima_neta')
            elif 'prima' in pol_cols:
                select_cols.append('prima')

            if not select_cols:
                # nada que mostrar
                suma_display = 'N/A'
                prima_display = 'N/A'
            else:
                q = f"SELECT {', '.join(select_cols)} FROM polizas WHERE id = ?"
                cur4.execute(q, (selected[0],))
                rr = cur4.fetchone()
                if rr:
                    # asignar según lo que se obtuvo
                    idx = 0
                    if 'suma_asegurada' in select_cols:
                        suma_actual = rr[idx]
                        idx += 1
                    if 'prima_neta' in select_cols:
                        prima_actual = rr[idx]
                        idx += 1
                    elif 'prima' in select_cols:
                        prima_actual = rr[idx]
                        idx += 1

                suma_display = f"{float(suma_actual):,.2f}" if suma_actual not in (None, '') else 'N/A'
                # prima_actual puede ser int o texto; intentar formatear
                try:
                    prima_display = f"{float(prima_actual):,.2f}" if prima_actual not in (None, '') else 'N/A'
                except Exception:
                    prima_display = str(prima_actual) if prima_actual not in (None, '') else 'N/A'
        except Exception as e:
            st.error(f"Error al leer suma/prima de la póliza: {e}")
            suma_display = 'N/A'
            prima_display = 'N/A'
        finally:
            try:
                conn4.close()
            except Exception:
                pass

        st.write(f"**Suma Asegurada actual:** {suma_display}")
        st.write(f"**Prima actual:** {prima_display}")

        # Input para nueva suma asegurada (por defecto el valor actual si existe)
        default_nueva = 0.0
        try:
            if suma_actual not in (None, ''):
                default_nueva = float(suma_actual)
        except Exception:
            default_nueva = 0.0

        nueva_suma = st.number_input('Nueva suma asegurada', min_value=0.0, value=default_nueva, step=100.0, format='%.2f')

    # Observaciones temporalmente omitidas — se añadirán en una operación posterior

        # Calcular y mostrar porcentaje de cambio respecto a la suma actual
        can_proceed = False
        if suma_actual in (None, '') or suma_actual == 0:
            # Si no hay suma actual o es 0, mostramos aviso y permitimos si la nueva > 0
            if nueva_suma > 0:
                st.info('No existe una suma asegurada previa (o es 0). La nueva suma será registrada.')
                can_proceed = True
            else:
                st.warning('La nueva suma debe ser mayor que 0 para proceder.')
        else:
            try:
                actual_val = float(suma_actual)
                if nueva_suma > actual_val:
                    pct = (nueva_suma - actual_val) / actual_val * 100.0
                    st.success(f'Incremento: {pct:.2f}% respecto a la suma actual')
                    can_proceed = True
                elif nueva_suma == actual_val:
                    st.info('La nueva suma es igual a la suma actual; no hay cambio.')
                    can_proceed = False
                else:
                    pct = (actual_val - nueva_suma) / actual_val * 100.0
                    st.error(f'La nueva suma es menor que la actual (disminución de {pct:.2f}%). No está permitido.')
                    can_proceed = False
            except Exception:
                st.warning('No se pudo calcular el porcentaje de cambio.')
                can_proceed = False

        # Botón para crear el anexo — solo activo si la nueva suma es mayor que la actual
        if can_proceed:
            # Mostrar input para nueva prima y validación ANTES de pulsar crear (para que aparezca en la UI)
            default_prima = 0.0
            try:
                if prima_actual not in (None, ''):
                    default_prima = float(prima_actual)
            except Exception:
                default_prima = 0.0

            nueva_prima = st.number_input('Nueva prima', min_value=0.0, value=default_prima, step=1.0, format='%.2f')

            # Validación y porcentaje para la prima
            prima_can_proceed = False
            # --- CÁLCULO DE IMPUESTOS Y CARGOS SOBRE LA PRIMA ---
            # Asumimos contribuciones porcentuales: 0.5% Contribución SCVS y 0.5% Seguro Campesino
            try:
                contrib_scvs_pct = 0.5
                seguro_campesino_pct = 0.5
                contrib_scvs_amount = float(nueva_prima) * contrib_scvs_pct / 100.0
                seguro_campesino_amount = float(nueva_prima) * seguro_campesino_pct / 100.0
            except Exception:
                contrib_scvs_pct = 0.5
                seguro_campesino_pct = 0.5
                contrib_scvs_amount = 0.0
                seguro_campesino_amount = 0.0

            derecho_emision = st.number_input('Derecho de emisión', min_value=0.0, value=0.0, step=0.01, format='%.2f', help='Ingrese el monto del derecho de emisión')
            otros_cargos = st.number_input('Otros cargos', min_value=0.0, value=0.0, step=0.01, format='%.2f', help='Ingrese otros cargos aplicables')

            subtotal = float(nueva_prima) + contrib_scvs_amount + seguro_campesino_amount + float(derecho_emision) + float(otros_cargos)

            st.write(f"Contribución SCVS ({contrib_scvs_pct}%): {contrib_scvs_amount:,.2f}")
            st.write(f"Seguro Campesino ({seguro_campesino_pct}%): {seguro_campesino_amount:,.2f}")
            st.write(f"Derecho de emisión: {float(derecho_emision):,.2f}")
            st.write(f"Otros cargos: {float(otros_cargos):,.2f}")
            st.write(f"**Subtotal (prima + cargos): {subtotal:,.2f}**")
            # Aplicar IVA al subtotal
            try:
                iva_pct = 15.0
                iva_amount = subtotal * iva_pct / 100.0
                total_prima = subtotal + iva_amount
            except Exception:
                iva_pct = 15.0
                iva_amount = 0.0
                total_prima = subtotal

            st.write(f"IVA ({iva_pct}%): {iva_amount:,.2f}")
            st.write(f"**Total prima (subtotal + IVA): {total_prima:,.2f}**")
            # --- CAMPOS PARA LA FACTURA (opcional) ---
            st.markdown('### Datos de factura (opcional)')
            generar_factura = st.checkbox('Generar factura ligada a este movimiento', value=False, help='Si está activado, al crear el anexo se creará un registro en la tabla "facturas" usando los importes calculados.')
            numero_factura = st.text_input('Número de factura', value=f"F-{datetime.date.today().strftime('%Y%m%d')}-", help='Código o número de la factura')
            fecha_emision = st.date_input('Fecha de emisión de la factura', value=datetime.date.today())
            if prima_actual in (None, '') or float(prima_actual) == 0:
                if nueva_prima > 0:
                    st.info('No existe una prima previa (o es 0). La nueva prima será registrada.')
                    prima_can_proceed = True
                else:
                    st.warning('La nueva prima debe ser mayor que 0 para proceder.')
            else:
                try:
                    prior_prima = float(prima_actual)
                    if nueva_prima > prior_prima:
                        pctp = (nueva_prima - prior_prima) / prior_prima * 100.0
                        st.success(f'Incremento de prima: {pctp:.2f}% respecto a la prima actual')
                        prima_can_proceed = True
                    elif nueva_prima == prior_prima:
                        st.info('La nueva prima es igual a la prima actual; no hay cambio.')
                        prima_can_proceed = False
                    else:
                        pctp = (prior_prima - nueva_prima) / prior_prima * 100.0
                        st.error(f'La nueva prima es menor que la actual (disminución de {pctp:.2f}%). No está permitido.')
                        prima_can_proceed = False
                except Exception:
                    st.warning('No se pudo calcular el porcentaje de cambio de la prima.')
                    prima_can_proceed = False

            # Obtener cliente_id (necesario para el INSERT) — hacemos esto antes del botón
            poliza_id = selected[0]
            cliente_id = None
            try:
                conn2 = sqlite3.connect(DB_FILE)
                cur2 = conn2.cursor()
                cur2.execute('SELECT cliente_id FROM polizas WHERE id = ?', (poliza_id,))
                r = cur2.fetchone()
                if r:
                    cliente_id = r[0]
            except Exception as e:
                st.error(f'Error obteniendo cliente de la póliza: {e}')
                return
            finally:
                try:
                    conn2.close()
                except Exception:
                    pass

            if not prima_can_proceed:
                st.button('Crear Anexo de Aumento de Suma Asegurada', disabled=True)
            else:
                if st.button('Crear Anexo de Aumento de Suma Asegurada'):
                    # Validaciones mínimas
                    if not codigo_movimiento:
                        st.warning('Introduzca un código para el movimiento antes de crear el anexo.')
                        return
                    # Si se solicita factura, requerir número de factura válido
                    if generar_factura and (not numero_factura or not str(numero_factura).strip()):
                        st.warning('Si desea generar factura, introduzca un número de factura válido.')
                        return
                    else:
                        fecha_mov = datetime.date.today().strftime('%Y-%m-%d')
                        try:
                            conn3 = sqlite3.connect(DB_FILE)
                            cur3 = conn3.cursor()
                            # Insertar movimiento
                            cur3.execute(
                                '''
                                INSERT INTO movimientos_poliza (codigo_movimiento, poliza_id, cliente_id, fecha_movimiento, tipo_movimiento, estado, suma_asegurada_nueva, prima_nueva)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                ''',
                                (
                                    codigo_movimiento,
                                    poliza_id,
                                    cliente_id,
                                    fecha_mov,
                                    'Anexo de Aumento de Suma Asegurada',
                                    'Aplicado',
                                    nueva_suma,
                                    nueva_prima,
                                )
                            )

                            movimiento_id = cur3.lastrowid

                            # Si se solicita factura, insertarla vinculada al movimiento (usando columnas presentes en la tabla facturas)
                            if generar_factura:
                                try:
                                    monto_neto = float(nueva_prima)
                                    impuestos = contrib_scvs_amount + seguro_campesino_amount + float(derecho_emision) + float(otros_cargos)
                                    iva_val = float(iva_amount)
                                    total = float(total_prima)
                                    fecha_emision_str = fecha_emision.strftime('%Y-%m-%d')

                                    cur3.execute(
                                        '''
                                        INSERT INTO facturas
                                        (numero_factura, poliza_id, movimiento_id, cliente_id, fecha_emision, monto_neto, impuestos, iva, total, estado, fecha_registro)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        ''',
                                        (
                                            numero_factura,
                                            poliza_id,
                                            movimiento_id,
                                            cliente_id,
                                            fecha_emision_str,
                                            monto_neto,
                                            impuestos,
                                            iva_val,
                                            total,
                                            'Emitida',
                                            datetime.date.today().strftime('%Y-%m-%d')
                                        )
                                    )
                                except Exception as ef:
                                    st.warning(f'No se pudo insertar la factura automáticamente: {ef}')

                            # Actualizar la póliza con los nuevos valores (misma transacción)
                            try:
                                cur3.execute("PRAGMA table_info(polizas)")
                                pol_cols_all = [c[1] for c in cur3.fetchall()]
                                update_parts = []
                                update_vals = []
                                if 'suma_asegurada' in pol_cols_all:
                                    update_parts.append('suma_asegurada = ?')
                                    update_vals.append(nueva_suma)
                                # preferir prima_neta si existe
                                prima_col = None
                                if 'prima_neta' in pol_cols_all:
                                    prima_col = 'prima_neta'
                                elif 'prima' in pol_cols_all:
                                    prima_col = 'prima'
                                if prima_col:
                                    update_parts.append(f"{prima_col} = ?")
                                    update_vals.append(nueva_prima)

                                if update_parts:
                                    update_vals.append(poliza_id)
                                    q_up = f"UPDATE polizas SET {', '.join(update_parts)} WHERE id = ?"
                                    cur3.execute(q_up, tuple(update_vals))
                            except Exception:
                                # si falla la actualización de póliza, continuamos y haremos rollback abajo
                                raise

                            conn3.commit()
                            st.success(f"Anexo creado (codigo={codigo_movimiento}) y registrado en movimientos_poliza; póliza actualizada.")
                            st.rerun()
                        except Exception as e:
                            try:
                                conn3.rollback()
                            except Exception:
                                pass
                            st.error(f'Error al crear anexo o actualizar póliza: {e}')
                        finally:
                            try:
                                conn3.close()
                            except Exception:
                                pass
        else:
            st.button('Crear Anexo de Aumento de Suma Asegurada', disabled=True)