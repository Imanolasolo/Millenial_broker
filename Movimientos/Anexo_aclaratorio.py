import streamlit as st
import sqlite3
from dbconfig import DB_FILE
import datetime


def anexo_aclaratorio():
    """UI para crear un Anexo Aclaratorio.

    Comportamiento:
    - Sidebar: selector de pólizas con estado 'Activa' (solo esas aparecen).
    - En el expander: input para código del movimiento y observaciones.
    - Al pulsar 'Crear anexo aclaratorio' se inserta un movimiento en
      `movimientos_poliza` y se actualiza la columna `observaciones` en `polizas`
      reemplazando el contenido por el texto ingresado.
    """

    # Obtener pólizas activas (se mostrarán dentro del expander)
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

    with st.expander('Anexo Aclaratorio', expanded=True):
        codigo_movimiento = st.text_input('Código de nuevo movimiento', help='Código identificador para el anexo aclaratorio')

        if not polizas_activas:
            st.info('No hay pólizas activas disponibles.')
            st.text_area('Observaciones que se escribirán en la póliza', value='', height=200, help='Este texto reemplazará el campo observaciones de la póliza seleccionada')
            st.button('Crear anexo aclaratorio', disabled=True)
            return

        selected_poliza = st.selectbox('Póliza (solo activas)', polizas_activas, format_func=lambda x: x[1], key='anexo_poliza')

        observaciones = st.text_area('Observaciones que se escribirán en la póliza', height=200, help='Este texto reemplazará el campo observaciones de la póliza seleccionada')

        if st.button('Crear anexo aclaratorio'):
            if not codigo_movimiento:
                st.warning('Debe introducir un código para el movimiento.')
                return
            if observaciones is None or observaciones.strip() == '':
                st.warning('Debe introducir las observaciones a almacenar en la póliza.')
                return

            poliza_id = selected_poliza[0]

            # Obtener cliente_id de la póliza
            cliente_id = None
            try:
                conn2 = sqlite3.connect(DB_FILE)
                cur2 = conn2.cursor()
                cur2.execute('SELECT cliente_id FROM polizas WHERE id = ?', (poliza_id,))
                r = cur2.fetchone()
                if r:
                    cliente_id = r[0]
            except Exception as e:
                st.error(f'Error obteniendo datos de la póliza: {e}')
                return
            finally:
                try:
                    conn2.close()
                except Exception:
                    pass

            fecha_mov = datetime.date.today().strftime('%Y-%m-%d')

            # Insertar movimiento y actualizar observaciones de la póliza
            try:
                conn3 = sqlite3.connect(DB_FILE)
                cur3 = conn3.cursor()

                cur3.execute(
                    '''
                    INSERT INTO movimientos_poliza (codigo_movimiento, poliza_id, cliente_id, fecha_movimiento, tipo_movimiento, estado, observaciones)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        codigo_movimiento,
                        poliza_id,
                        cliente_id,
                        fecha_mov,
                        'Anexo Aclaratorio',
                        'Aplicado',
                        f'Anexo aclaratorio creado por UI el {fecha_mov}: {observaciones}'
                    )
                )

                # Reemplazar (cambiar) la columna observaciones de la póliza
                cur3.execute('UPDATE polizas SET observaciones = ? WHERE id = ?', (observaciones, poliza_id))

                conn3.commit()
                st.success(f"Anexo aclaratorio '{codigo_movimiento}' creado y observaciones de la póliza actualizadas.")
                st.rerun()

            except Exception as e:
                try:
                    conn3.rollback()
                except Exception:
                    pass
                st.error(f'Error al crear anexo/actualizar póliza: {e}')
            finally:
                try:
                    conn3.close()
                except Exception:
                    pass


__all__ = ['anexo_aclaratorio']
