import streamlit as st
import sqlite3
import streamlit as st
import sqlite3
from dbconfig import DB_FILE
import datetime


def activacion_poliza():
    with st.expander("Activación de Póliza", expanded=True):
        # Código del nuevo movimiento
        codigo_movimiento = st.text_input("Código de nuevo movimiento", help="Ingrese el código identificador para el movimiento de activación")

        # Cargar pólizas desde la base de datos
        polizas = []
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("SELECT id, numero_poliza, estado FROM polizas ORDER BY id DESC")
            rows = cur.fetchall()
            for r in rows:
                pid, numero, estado = r[0], r[1], r[2] if len(r) > 2 else None
                label = f"{numero} ({estado})" if estado else f"{numero}"
                polizas.append((pid, label))
        except Exception as e:
            st.error(f"Error al leer la base de datos: {e}")
        finally:
            try:
                conn.close()
            except Exception:
                pass

        if not polizas:
            st.info("No hay pólizas registradas en la base de datos.")
            st.button('Activar Póliza', disabled=True)
            return

        selected = st.selectbox('Seleccione la póliza a activar:', polizas, format_func=lambda x: x[1])

        if st.button('Activar Póliza'):
            if not selected:
                st.warning("Seleccione primero una póliza.")
                return

            if not codigo_movimiento:
                st.warning("Debe ingresar un código para el nuevo movimiento antes de activar la póliza.")
                return

            poliza_id = selected[0]

            # comprobar estado actual desde la base de datos para garantizar consistencia
            estado_actual = None
            cliente_id = None
            try:
                conn2 = sqlite3.connect(DB_FILE)
                cur2 = conn2.cursor()
                cur2.execute("SELECT estado, cliente_id FROM polizas WHERE id = ?", (poliza_id,))
                row = cur2.fetchone()
                if row:
                    estado_actual = row[0]
                    cliente_id = row[1]
            except Exception as e:
                st.error(f"Error comprobando estado de la póliza: {e}")
                return
            finally:
                try:
                    conn2.close()
                except Exception:
                    pass

            if estado_actual == 'Activa':
                st.info(f"La póliza ya está en estado 'Activa'. (id={poliza_id})")
                return

            # Insertar movimiento y actualizar el estado de la póliza dentro de una transacción
            try:
                conn3 = sqlite3.connect(DB_FILE)
                cur3 = conn3.cursor()

                fecha_mov = datetime.date.today().strftime("%Y-%m-%d")

                # Insertar nuevo movimiento con estado 'Aplicado' porque se está activando inmediatamente
                cur3.execute(
                    """
                    INSERT INTO movimientos_poliza (codigo_movimiento, poliza_id, cliente_id, fecha_movimiento, tipo_movimiento, estado, observaciones)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        codigo_movimiento,
                        poliza_id,
                        cliente_id,
                        fecha_mov,
                        'Activación de póliza',
                        'Aplicado',
                        f'Generado por UI Activación de Póliza el {fecha_mov}'
                    )
                )

                # Actualizar estado de la póliza a 'Activa'
                cur3.execute("UPDATE polizas SET estado = ? WHERE id = ?", ('Activa', poliza_id))

                conn3.commit()
                st.success(f"Movimiento '{codigo_movimiento}' creado y póliza (id={poliza_id}) activada.")
                st.rerun()

            except Exception as e:
                try:
                    conn3.rollback()
                except Exception:
                    pass
                st.error(f"Error al crear movimiento/actualizar póliza: {e}")
            finally:
                try:
                    conn3.close()
                except Exception:
                    pass