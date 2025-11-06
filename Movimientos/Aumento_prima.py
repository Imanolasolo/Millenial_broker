import streamlit as st
import sqlite3
from dbconfig import DB_FILE
import datetime


def aumento_prima():
    """Panel flow to increase the policy premium.

    - Shows a policy selector in the main panel (only ACTIVE policies).
    - Shows a number input for the new premium (default = current premium).
    - Validates that the new premium is greater than the current one (or >0 if none).
    - On button press, updates the appropriate `prima` column in `polizas` (prefers `prima_neta` if present, else `prima`).
    """

    # Load active policies
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

    st.header('Aumento de Prima')

    # Código del nuevo movimiento (input antes del selector)
    codigo_movimiento = st.text_input('Código de nuevo movimiento', help='Ingrese el código identificador para el movimiento')

    if not polizas_activas:
        st.info('No hay pólizas ACTIVAS disponibles.')
        return

    selected = st.selectbox('Seleccionar póliza (ACTIVA):', polizas_activas, format_func=lambda x: x[1])

    # Read current premium for the selected policy
    prima_actual = None
    try:
        conn2 = sqlite3.connect(DB_FILE)
        cur2 = conn2.cursor()
        cur2.execute("PRAGMA table_info(polizas)")
        cols = [c[1] for c in cur2.fetchall()]
        sel_col = None
        if 'prima_neta' in cols:
            sel_col = 'prima_neta'
        elif 'prima' in cols:
            sel_col = 'prima'

        if sel_col:
            cur2.execute(f"SELECT {sel_col} FROM polizas WHERE id = ?", (selected[0],))
            r = cur2.fetchone()
            if r:
                prima_actual = r[0]
    except Exception as e:
        st.error(f"Error leyendo prima actual: {e}")
    finally:
        try:
            conn2.close()
        except Exception:
            pass

    # Display current premium in the main area
    try:
        prima_display = f"{float(prima_actual):,.2f}" if prima_actual not in (None, '') else 'N/A'
    except Exception:
        prima_display = str(prima_actual) if prima_actual not in (None, '') else 'N/A'

    st.write(f"**Prima actual:** {prima_display}")

    # Input for new premium in sidebar
    default_prima = 0.0
    try:
        if prima_actual not in (None, ''):
            default_prima = float(prima_actual)
    except Exception:
        default_prima = 0.0

    nueva_prima = st.number_input('Nueva prima', min_value=0.0, value=default_prima, step=1.0, format='%.2f')

    # --- CÁLCULO DE TASAS, SUBTOTAL, IVA Y TOTAL A CAMBIAR ---
    # Contribuciones porcentuales: 0.5% Contribución SCVS y 0.5% Seguro Campesino
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

    # IVA y total
    try:
        iva_pct = 15.0
        iva_amount = subtotal * iva_pct / 100.0
        total_prima = subtotal + iva_amount
    except Exception:
        iva_pct = 15.0
        iva_amount = 0.0
        total_prima = subtotal

    st.write(f"IVA ({iva_pct}%): {iva_amount:,.2f}")
    st.write(f"**Total prima a aplicar (subtotal + IVA): {total_prima:,.2f}**")

    # --- CAMPOS PARA LA FACTURA (inputs antes del botón) ---
    st.markdown('### Datos de factura (opcional)')
    generar_factura = st.checkbox('Generar factura ligada a este movimiento', value=False, help='Si está activado, al aplicar el movimiento se creará un registro en la tabla "facturas" usando los importes calculados.')
    numero_factura = st.text_input('Número de factura', value=f"F-{datetime.date.today().strftime('%Y%m%d')}-", help='Código o número de la factura')
    fecha_emision = st.date_input('Fecha de emisión de la factura', value=datetime.date.today())
    # Nota: la tabla `facturas` creada en dbconfig no contiene campos moneda/forma_pago por defecto;
    # si los necesitas, podemos añadir esas columnas en la inicialización de la BD.

    # Validation: new premium must be greater than current (or >0 if current missing)
    can_apply = False
    if prima_actual in (None, '') or float(prima_actual) == 0:
        if nueva_prima > 0:
            st.info('No existe una prima previa (o es 0). La nueva prima será registrada.')
            can_apply = True
        else:
            st.warning('La nueva prima debe ser mayor que 0 para proceder.')
    else:
        try:
            prior = float(prima_actual)
            if nueva_prima > prior:
                pct = (nueva_prima - prior) / prior * 100.0
                st.success(f'Incremento de prima: {pct:.2f}%')
                can_apply = True
            elif nueva_prima == prior:
                st.info('La nueva prima es igual a la prima actual; no hay cambio.')
                can_apply = False
            else:
                pct = (prior - nueva_prima) / prior * 100.0
                st.error(f'La nueva prima es menor que la actual (disminución de {pct:.2f}%). No está permitido.')
                can_apply = False
        except Exception:
            st.warning('No se pudo calcular la diferencia de prima.')
            can_apply = False

    # Apply button in the sidebar
    if not can_apply:
        st.button('Aplicar Aumento de Prima', disabled=True)
        return

    if st.button('Aplicar Aumento de Prima'):
        # perform update on polizas (detecting prima_neta/prima column)
        # require codigo_movimiento
        if not codigo_movimiento:
            st.warning('Introduzca un código para el movimiento antes de aplicar el aumento de prima.')
            return
        # Si se solicita factura, requerir número de factura válido
        if generar_factura and (not numero_factura or not str(numero_factura).strip()):
            st.warning('Si desea generar factura, introduzca un número de factura válido.')
            return
        try:
            conn3 = sqlite3.connect(DB_FILE)
            cur3 = conn3.cursor()

            # Obtener cliente_id para el INSERT en movimientos_poliza
            cliente_id = None
            try:
                cur3.execute('SELECT cliente_id FROM polizas WHERE id = ?', (selected[0],))
                rcli = cur3.fetchone()
                if rcli:
                    cliente_id = rcli[0]
            except Exception:
                cliente_id = None

            fecha_mov = datetime.date.today().strftime('%Y-%m-%d')

            # Insertar movimiento en movimientos_poliza (estado 'Aplicado' porque se aplica inmediatamente)
            cur3.execute(
                '''
                INSERT INTO movimientos_poliza (codigo_movimiento, poliza_id, cliente_id, fecha_movimiento, tipo_movimiento, estado, prima_nueva)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''',
                (
                    codigo_movimiento,
                    selected[0],
                    cliente_id,
                    fecha_mov,
                    'Aumento de Prima',
                    'Aplicado',
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
                            selected[0],
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
                    # si falla la inserción de factura, advertimos pero continuamos (rollback ocurrirá si hay error crítico más abajo)
                    st.warning(f'No se pudo insertar la factura automáticamente: {ef}')

            # Detectar columna de prima y actualizar la póliza con total_prima
            cur3.execute("PRAGMA table_info(polizas)")
            cols_all = [c[1] for c in cur3.fetchall()]
            prima_col = None
            if 'prima_neta' in cols_all:
                prima_col = 'prima_neta'
            elif 'prima' in cols_all:
                prima_col = 'prima'

            if not prima_col:
                st.error('La tabla polizas no contiene columna de prima para actualizar.')
                conn3.rollback()
                return

            cur3.execute(f"UPDATE polizas SET {prima_col} = ? WHERE id = ?", (total_prima, selected[0]))
            conn3.commit()
            st.success(f'Prima actualizada a {total_prima:,.2f} (incluye cargos e IVA) en {prima_col} para la póliza {selected[1]} (id={selected[0]}).')
        except Exception as e:
            try:
                conn3.rollback()
            except Exception:
                pass
            st.error(f'Error actualizando prima: {e}')
        finally:
            try:
                conn3.close()
            except Exception:
                pass
