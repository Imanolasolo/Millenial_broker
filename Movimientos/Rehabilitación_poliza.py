import streamlit as st
import sqlite3
from dbconfig import DB_FILE
import datetime


def rehabilitacion_poliza():
	"""Expander para rehabilitar (reactivar) pólizas canceladas.

	- Pide Código de nuevo movimiento.
	- Muestra un selector con pólizas cuyo estado es 'Cancelada'.
	- Al pulsar 'Reactivar póliza' inserta un movimiento en `movimientos_poliza` y cambia el estado a 'Activa'.
	"""

	with st.expander('Rehabilitación de Póliza', expanded=True):
		st.write('Reactive una póliza marcada como Cancelada. Se registrará un movimiento.')

		codigo_movimiento = st.text_input('Código de nuevo movimiento', help='Ingrese el código identificador para el movimiento de rehabilitación')

		# Cargar pólizas con estado Cancelada
		polizas_canceladas = []
		try:
			conn = sqlite3.connect(DB_FILE)
			cur = conn.cursor()
			cur.execute("SELECT id, numero_poliza FROM polizas WHERE estado = 'Cancelada' ORDER BY id DESC")
			rows = cur.fetchall()
			for r in rows:
				polizas_canceladas.append((r[0], r[1]))
		except Exception as e:
			st.error(f"Error al leer pólizas canceladas: {e}")
		finally:
			try:
				conn.close()
			except Exception:
				pass

		if not polizas_canceladas:
			st.info('No hay pólizas con estado "Cancelada".')
			return

		selected = st.selectbox('Seleccionar póliza (CANCELADA):', polizas_canceladas, format_func=lambda x: x[1])

		if st.button('Reactivar póliza'):
			if not codigo_movimiento:
				st.warning('Introduzca el código del nuevo movimiento antes de reactivar la póliza.')
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

			# Insertar movimiento y actualizar estado en la misma transacción
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
						'Rehabilitación',
						'Aplicado',
					)
				)

				cur3.execute("UPDATE polizas SET estado = ? WHERE id = ?", ('Activa', poliza_id))

				conn3.commit()
				st.success(f'Póliza id={poliza_id} reactivada a estado Activa (movimiento={codigo_movimiento}).')
				st.rerun()
			except Exception as e:
				try:
					conn3.rollback()
				except Exception:
					pass
				st.error(f'Error al reactivar la póliza: {e}')
			finally:
				try:
					conn3.close()
				except Exception:
					pass

