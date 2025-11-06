import streamlit as st
import sqlite3
from dbconfig import DB_FILE
from Movimientos.Activacion_poliza import activacion_poliza
from Movimientos.Aumento_suma_asegurada import aumento_suma_asegurada
from Movimientos.Anexo_aclaratorio import anexo_aclaratorio
from Movimientos.Disminucion_suma_asegurada import disminucion_suma_asegurada
from Movimientos.Aumento_prima import aumento_prima
from Movimientos.Disminucion_prima import disminucion_prima
from Movimientos.Cancelacion_poliza import cancelacion_poliza
from Movimientos.Rehabilitación_poliza import rehabilitacion_poliza

def _fetch_movimientos(limit=200):
	try:
		conn = sqlite3.connect(DB_FILE)
		cur = conn.cursor()
		cur.execute(
			"SELECT id, codigo_movimiento, tipo_movimiento, estado, fecha_movimiento FROM movimientos_poliza ORDER BY fecha_movimiento DESC LIMIT ?",
			(limit,)
		)
		rows = cur.fetchall()
		return rows
	except Exception as e:
		st.error(f"Error al acceder a movimientos en la base de datos: {e}")
		return []
	finally:
		try:
			conn.close()
		except Exception:
			pass


def crud_movimientos():
	# Selector principal: acción sobre movimientos
	accion = st.selectbox(
		'Acción sobre Movimientos',
		['Usar Movimientos (seleccionar tipo)', 'Leer movimientos', 'Editar movimientos', 'Borrar movimientos']
	)

	# --- LEER MOVIMIENTOS ---
	if accion == 'Leer movimientos':
		st.subheader('📄 Leer Movimientos')
		movimientos = _fetch_movimientos(limit=500)
		if not movimientos:
			st.info('No hay movimientos para mostrar.')
			return

		options = [(m[0], f"{m[1]} | {m[2]} | {m[3]} | {m[4]}") for m in movimientos]
		seleccionado = st.selectbox('Selecciona un movimiento para ver detalle', options, format_func=lambda x: x[1])
		if not seleccionado:
			return
		mov_id = seleccionado[0]
		try:
			conn = sqlite3.connect(DB_FILE)
			cur = conn.cursor()
			# Fetch movement full row with column names
			cur.execute('PRAGMA table_info(movimientos_poliza)')
			cols = [c[1] for c in cur.fetchall()]
			cur.execute('SELECT * FROM movimientos_poliza WHERE id = ?', (mov_id,))
			row = cur.fetchone()
			if not row:
				st.error('Movimiento no encontrado')
				return
			mov = dict(zip(cols, row))
			st.markdown('### Movimiento')
			st.json(mov)

			# Fetch linked policy if exists
			poliza_info = None
			if mov.get('poliza_id'):
				try:
					cur.execute('SELECT id, numero_poliza, cliente_id, estado, suma_asegurada, prima_neta, prima FROM polizas WHERE id = ?', (mov.get('poliza_id'),))
					p = cur.fetchone()
					if p:
						poliza_info = {
							'id': p[0], 'numero_poliza': p[1], 'cliente_id': p[2], 'estado': p[3],
							'suma_asegurada': p[4], 'prima_neta': p[5], 'prima': p[6]
						}
				except Exception:
					poliza_info = None
			if poliza_info:
				st.markdown('### Póliza vinculada')
				st.json(poliza_info)
			else:
				st.info('No hay póliza vinculada a este movimiento.')

			# Fetch invoices linked to this movement or its policy
			facturas = []
			try:
				cur.execute('SELECT id, numero_factura, poliza_id, fecha_emision, monto_neto, impuestos, iva, total, estado FROM facturas WHERE movimiento_id = ? OR poliza_id = ?', (mov_id, mov.get('poliza_id')))
				for f in cur.fetchall():
					facturas.append({
						'id': f[0], 'numero_factura': f[1], 'poliza_id': f[2], 'fecha_emision': f[3],
						'monto_neto': f[4], 'impuestos': f[5], 'iva': f[6], 'total': f[7], 'estado': f[8]
					})
			except Exception:
				facturas = []
			if facturas:
				st.markdown('### Facturas vinculadas')
				import pandas as pd
				df_f = pd.DataFrame(facturas)
				st.dataframe(df_f, use_container_width=True)
			else:
				st.info('No se encontraron facturas vinculadas a este movimiento/póliza.')

			# Fetch credit notes linked to this movement or invoices
			notas = []
			try:
				# buscar por movimiento_id o por factura_id relacionada
				if facturas:
					factura_ids = tuple([f['id'] for f in facturas])
					placeholders = ','.join('?' for _ in factura_ids)
					query = f'SELECT id, numero_nota, factura_id, poliza_id, monto_neto, impuestos, iva, total, motivo, estado FROM notas_de_credito WHERE movimiento_id = ? OR factura_id IN ({placeholders})'
					params = (mov_id,) + factura_ids
					cur.execute(query, params)
				else:
					cur.execute('SELECT id, numero_nota, factura_id, poliza_id, monto_neto, impuestos, iva, total, motivo, estado FROM notas_de_credito WHERE movimiento_id = ? OR poliza_id = ?', (mov_id, mov.get('poliza_id')))
				for n in cur.fetchall():
					notas.append({
						'id': n[0], 'numero_nota': n[1], 'factura_id': n[2], 'poliza_id': n[3],
						'monto_neto': n[4], 'impuestos': n[5], 'iva': n[6], 'total': n[7], 'motivo': n[8], 'estado': n[9]
					})
			except Exception:
				notas = []
			if notas:
				st.markdown('### Notas de crédito vinculadas')
				import pandas as pd
				df_n = pd.DataFrame(notas)
				st.dataframe(df_n, use_container_width=True)
			else:
				st.info('No se encontraron notas de crédito vinculadas a este movimiento/póliza.')

		except Exception as e:
			st.error(f'Error leyendo detalles del movimiento: {e}')
		finally:
			try:
				conn.close()
			except Exception:
				pass
		return

	# --- EDITAR MOVIMIENTOS ---
	if accion == 'Editar movimientos':
		st.subheader('✏️ Editar Movimientos')
		movimientos = _fetch_movimientos()
		if not movimientos:
			st.info('No hay movimientos disponibles para editar.')
			return

		options = [(m[0], f"{m[1]} | {m[2]} | {m[3]} | {m[4]}") for m in movimientos]
		seleccionado = st.selectbox('Selecciona un movimiento para editar', options, format_func=lambda x: x[1])

		if seleccionado:
			mov_id = seleccionado[0]
			try:
				conn = sqlite3.connect(DB_FILE)
				cur = conn.cursor()
				cur.execute('SELECT * FROM movimientos_poliza WHERE id = ?', (mov_id,))
				row = cur.fetchone()
				if not row:
					st.error('Movimiento no encontrado en la base de datos.')
					return

				# Mapear columnas por índice usando PRAGMA
				cur.execute('PRAGMA table_info(movimientos_poliza)')
				cols = [c[1] for c in cur.fetchall()]
				mov = dict(zip(cols, row))

				# Campos editables básicos
				codigo = st.text_input('Código movimiento', value=mov.get('codigo_movimiento', ''))
				tipo = st.text_input('Tipo de movimiento', value=mov.get('tipo_movimiento', ''))
				fecha = st.text_input('Fecha movimiento', value=mov.get('fecha_movimiento', ''))
				estado = st.selectbox('Estado', ['Proceso', 'Aprobado', 'Aplicado'], index=['Proceso','Aprobado','Aplicado'].index(mov.get('estado')) if mov.get('estado') in ['Proceso','Aprobado','Aplicado'] else 0)

				# Campos opcionales si existen
				suma_nueva = None
				prima_nueva = None
				direccion_nueva = None
				observaciones = mov.get('observaciones', '')
				if 'suma_asegurada_nueva' in mov:
					suma_nueva = st.text_input('Suma Asegurada Nueva', value=str(mov.get('suma_asegurada_nueva') or ''))
				if 'prima_nueva' in mov:
					prima_nueva = st.text_input('Prima Nueva', value=str(mov.get('prima_nueva') or ''))
				if 'direccion_nueva' in mov:
					direccion_nueva = st.text_area('Dirección Nueva', value=mov.get('direccion_nueva') or '')
				observaciones = st.text_area('Observaciones', value=observaciones)

				if st.button('💾 Guardar cambios'):
					try:
						updates = []
						params = []
						updates.append('codigo_movimiento = ?')
						params.append(codigo)
						updates.append('tipo_movimiento = ?')
						params.append(tipo)
						updates.append('fecha_movimiento = ?')
						params.append(fecha)
						updates.append('estado = ?')
						params.append(estado)
						if suma_nueva is not None:
							updates.append('suma_asegurada_nueva = ?')
							params.append(suma_nueva if suma_nueva != '' else None)
						if prima_nueva is not None:
							updates.append('prima_nueva = ?')
							params.append(prima_nueva if prima_nueva != '' else None)
						if direccion_nueva is not None:
							updates.append('direccion_nueva = ?')
							params.append(direccion_nueva)
						updates.append('observaciones = ?')
						params.append(observaciones)

						params.append(mov_id)
						query = f"UPDATE movimientos_poliza SET {', '.join(updates)} WHERE id = ?"
						cur.execute(query, params)
						conn.commit()
						st.success('Movimiento actualizado correctamente.')
						st.rerun()
					except Exception as e:
						st.error(f'Error al actualizar movimiento: {e}')
					finally:
						try:
							conn.close()
						except Exception:
							pass

			except Exception as e:
				st.error(f'Error leyendo el movimiento: {e}')

		return

	# --- BORRAR MOVIMIENTOS ---
	if accion == 'Borrar movimientos':
		st.subheader('🗑️ Borrar Movimientos')
		movimientos = _fetch_movimientos()
		if not movimientos:
			st.info('No hay movimientos disponibles para borrar.')
			return

		options = [(m[0], f"{m[1]} | {m[2]} | {m[3]} | {m[4]}") for m in movimientos]
		seleccionado = st.selectbox('Selecciona un movimiento para borrar', options, format_func=lambda x: x[1])

		if seleccionado:
			mov_id = seleccionado[0]
			try:
				conn = sqlite3.connect(DB_FILE)
				cur = conn.cursor()
				cur.execute('SELECT codigo_movimiento FROM movimientos_poliza WHERE id = ?', (mov_id,))
				row = cur.fetchone()
				codigo = row[0] if row else ''
			except Exception as e:
				st.error(f'Error accediendo a la base de datos: {e}')
				return
			finally:
				try:
					conn.close()
				except Exception:
					pass

			st.markdown('---')
			confirmar1 = st.checkbox('✅ Confirmo que deseo eliminar este movimiento')
			codigo_confirm = st.text_input('Para confirmar, escriba el código del movimiento')
			if confirmar1 and codigo_confirm:
				if codigo_confirm == codigo:
					if st.button('🗑️ ELIMINAR MOVIMIENTO'):
						try:
							conn2 = sqlite3.connect(DB_FILE)
							cur2 = conn2.cursor()
							cur2.execute('DELETE FROM movimientos_poliza WHERE id = ?', (mov_id,))
							conn2.commit()
							st.success('Movimiento eliminado correctamente.')
							st.rerun()
						except Exception as e:
							st.error(f'Error al eliminar movimiento: {e}')
						finally:
							try:
								conn2.close()
							except Exception:
								pass
				else:
					st.error('El código ingresado no coincide.')

		return

	# --- USAR MOVIMIENTOS: mostrar selector original de tipo de movimiento ---
	option = st.selectbox('Movimientos de poliza:', ['Activación de póliza', 'Anexo Aclaratorio', 'Anexo Aumento Suma Asegurada','Anexo Disminución Suma Asegurada', 'Anexo Aumento Prima', 'Anexo Disminución Prima', 'Cancelación de póliza', 'Rehabilitación de póliza'])
	if option == 'Activación de póliza':
		activacion_poliza()
	if option == 'Anexo Aclaratorio':
		anexo_aclaratorio()
	if option == 'Anexo Aumento Suma Asegurada':
		aumento_suma_asegurada()
	if option == 'Anexo Disminución Suma Asegurada':
		disminucion_suma_asegurada()
	if option == 'Anexo Aumento Prima':		
		aumento_prima()
	if option == 'Anexo Disminución Prima':
		disminucion_prima()
	if option == 'Cancelación de póliza':		
		cancelacion_poliza()
	if option == 'Rehabilitación de póliza':		
		rehabilitacion_poliza()
		

