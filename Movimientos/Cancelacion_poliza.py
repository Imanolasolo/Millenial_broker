import streamlit as st
import sqlite3
from dbconfig import DB_FILE
import datetime


def cancelacion_poliza():
    """Formulario para crear un movimiento de Cancelación de póliza.

    - Pide el `Código de nuevo movimiento` (requerido).
    - Permite seleccionar una póliza (lista de pólizas existentes) y guarda un registro en `movimientos_poliza`.
    - Actualiza el estado de la póliza a 'Cancelada' en la misma transacción.
    """

    with st.expander('Cancelación de Póliza', expanded=True):
        st.write('Cree un movimiento de cancelación y marque la póliza como Cancelada.')

        codigo_movimiento = st.text_input('Código de nuevo movimiento', help='Ingrese el código identificador para el movimiento de cancelación')

        # Cargar pólizas
        polizas = []
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("SELECT id, numero_poliza, estado FROM polizas ORDER BY id DESC")
            rows = cur.fetchall()
            for r in rows:
                pid = r[0]
                numero = r[1] if len(r) > 1 else str(r[0])
                estado = r[2] if len(r) > 2 else None
                label = f"{numero} ({estado})" if estado else f"{numero}"
                polizas.append((pid, label))
        except Exception as e:
            st.error(f'Error leyendo pólizas: {e}')
        finally:
            try:
                conn.close()
            except Exception:
                pass

        if not polizas:
            st.info('No hay pólizas registradas en la base de datos.')
            return

        selected = st.selectbox('Seleccionar póliza a cancelar:', polizas, format_func=lambda x: x[1])

        if st.button('Registrar Cancelación'):
            if not codigo_movimiento:
                st.warning('Introduzca el código del nuevo movimiento antes de guardar la cancelación.')
                return

            poliza_id = selected[0]

            # Obtener cliente_id (si existe)
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

            # Insertar movimiento y actualizar póliza en la misma transacción
            try:
                conn3 = sqlite3.connect(DB_FILE)
                cur3 = conn3.cursor()

                fecha_mov = datetime.date.today().strftime('%Y-%m-%d')

                cur3.execute(
                    '''
                    INSERT INTO movimientos_poliza (codigo_movimiento, poliza_id, cliente_id, fecha_movimiento, tipo_movimiento, estado)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''',
                    (
                        codigo_movimiento,
                        poliza_id,
                        cliente_id,
                        fecha_mov,
                        'Cancelación',
                        'Aplicado',
                    )
                )

                # Actualizar estado de la póliza a 'Cancelada'
                cur3.execute("UPDATE polizas SET estado = ? WHERE id = ?", ('Cancelada', poliza_id))

                conn3.commit()
                st.success(f"Cancelación registrada (codigo={codigo_movimiento}) y póliza id={poliza_id} marcada como 'Cancelada'.")
                st.rerun()
            except Exception as e:
                try:
                    conn3.rollback()
                except Exception:
                    pass
                st.error(f'Error registrando la cancelación: {e}')
            finally:
                try:
                    conn3.close()
                except Exception:
                    pass
