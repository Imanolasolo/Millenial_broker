import streamlit as st
from typing import Dict, Any, List
from crud.movimiento_crud import crud_movimientos

def movimientos_dashboard():
	"""Dashboard básico de gestión de movimientos."""
	st.title("Gestión de Movimientos - Básico")

	# CREAR
	st.header("Crear nuevo movimiento")
	with st.form("create_form", clear_on_submit=True):
		descripcion = st.text_input("Descripción")
		cantidad = st.number_input("Cantidad", value=0.0, format="%.2f")
		tipo = st.selectbox("Tipo", options=["ingreso", "gasto"])
		submit = st.form_submit_button("Crear")
		if submit:
			data: Dict[str, Any] = {
				"descripcion": descripcion,
				"cantidad": float(cantidad),
				"tipo": tipo,
			}
			created = crud_movimientos.create(data)
			st.success(f"Movimiento creado con id {created['id']}")

	# LISTAR
	st.header("Movimientos existentes")
	movs: List[Dict[str, Any]] = crud_movimientos.list_all()
	if not movs:
		st.info("No hay movimientos aún.")
	else:
		# mostrar tabla
		st.table(movs)

		# SELECCIÓN para editar/eliminar
		ids = [m["id"] for m in movs]
		selected_id = st.selectbox("Seleccionar movimiento por id", options=ids)
		if selected_id is not None:
			selected = crud_movimientos.get_by_id(selected_id)
			if selected:
				st.subheader(f"Detalles del movimiento {selected_id}")
				st.write(selected)

				# EDITAR
				with st.form("edit_form"):
					descripcion_e = st.text_input("Descripción", value=selected.get("descripcion", ""))
					cantidad_e = st.number_input("Cantidad", value=float(selected.get("cantidad", 0.0)), format="%.2f")
					tipo_e = st.selectbox("Tipo", options=["ingreso", "gasto"], index=0 if selected.get("tipo")=="ingreso" else 1)
					guardar = st.form_submit_button("Actualizar")
					if guardar:
						updated = crud_movimientos.update(selected_id, {
							"descripcion": descripcion_e,
							"cantidad": float(cantidad_e),
							"tipo": tipo_e,
						})
						if updated:
							st.success("Movimiento actualizado.")
						else:
							st.error("No se pudo actualizar el movimiento.")

				# ELIMINAR
				if st.button("Eliminar movimiento"):
					if crud_movimientos.delete(selected_id):
						st.success("Movimiento eliminado.")
					else:
						st.error("No se pudo eliminar el movimiento.")

if __name__ == "__main__":
	movimientos_dashboard()
