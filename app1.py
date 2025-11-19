# ============================================================================
# ARCHIVO PRINCIPAL DE LA APLICACIÓN - app1.py
# ============================================================================
# Este es el punto de entrada principal del sistema BCS Millennial Broker
# Gestiona la autenticación de usuarios y redirección a dashboards según roles
# ============================================================================

# Importaciones de librerías estándar de Python
import streamlit as st  # Framework principal para la interfaz web
import sqlite3  # Manejo de base de datos SQLite
import jwt  # JSON Web Tokens para autenticación segura
import datetime  # Manejo de fechas y tiempos
import bcrypt  # Encriptación de contraseñas con hash
import base64  # Codificación de imágenes para mostrar en web
import os  # Operaciones del sistema operativo

# Importación de módulos personalizados del proyecto
from dashboards.admin_dashboard import admin_dashboard  # Dashboard de administrador
from dbconfig import DB_FILE, SECRET_KEY  # Configuración de BD y clave secreta
from user_dashboard import user_dashboard  # Dashboard de usuario estándar
from crud.user_crud import create_user, read_users, update_user, delete_user, get_user_details  # Operaciones CRUD de usuarios
from database_config import initialize_database  # Inicialización de la base de datos

# ============================================================================
# CONFIGURACIÓN INICIAL DE LA PÁGINA
# ============================================================================
# Establece el icono de la página, título del navegador y layout wide (ancho completo)
st.set_page_config(page_icon="logo.png", page_title="Millenial Broker", layout="wide")

# ============================================================================
# FUNCIÓN: get_base64_of_bin_file
# Convierte una imagen binaria a formato base64 para usar como fondo CSS
# ============================================================================
def get_base64_of_bin_file(bin_file):
    """
    Codifica un archivo de imagen en formato base64 para embeber en HTML/CSS
    
    Parámetros:
        bin_file (str): Ruta del archivo de imagen a codificar
    
    Retorna:
        str: Cadena codificada en base64 o None si ocurre un error
    """
    try:
        # Abrir archivo en modo lectura binaria
        with open(bin_file, 'rb') as f:
            data = f.read()
        # Codificar en base64 y convertir bytes a string
        return base64.b64encode(data).decode()
    except Exception as e:
        # Mostrar error en la interfaz si no se puede leer el archivo
        st.error(f"Error al leer el archivo '{bin_file}': {e}")
        return None

# ============================================================================
# CONFIGURACIÓN DE IMAGEN DE FONDO
# ============================================================================
# Codificar la imagen de fondo en base64
img_base64 = get_base64_of_bin_file('assets/5134336.jpg')

# Si la imagen se codificó correctamente, aplicar como fondo de la aplicación
if img_base64:
    # Inyectar CSS personalizado usando Markdown de Streamlit
    # La imagen se aplica al elemento principal .stApp con propiedades:
    # - no-repeat: la imagen no se repite
    # - center center: centrada horizontal y verticalmente
    # - fixed: imagen fija al hacer scroll
    # - cover: imagen cubre toda el área sin distorsión
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url('data:image/jpeg;base64,{img_base64}') no-repeat center center fixed;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ============================================================================
# FUNCIÓN: authenticate
# Autentica al usuario verificando credenciales contra la base de datos
# ============================================================================
def authenticate(username, password):
    """
    Verifica las credenciales del usuario y genera un token JWT si son válidas
    
    Parámetros:
        username (str): Nombre de usuario ingresado
        password (str): Contraseña en texto plano ingresada
    
    Retorna:
        str: Token JWT si la autenticación es exitosa, None en caso contrario
    """
    # Conectar a la base de datos SQLite
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Buscar usuario en la tabla users por nombre de usuario
    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()  # Obtener el primer resultado (o None)
    conn.close()  # Cerrar conexión inmediatamente

    # Verificar si el usuario existe en la base de datos
    if not user:
        st.error("Usuario no encontrado.")
        return None

    # Asegurar que la contraseña almacenada esté en formato bytes para bcrypt
    # La contraseña está en la posición 2 del tuple (user[2])
    stored_password = user[2].encode() if isinstance(user[2], str) else user[2]

    # Verificar la contraseña usando bcrypt (compara hash almacenado con contraseña ingresada)
    if bcrypt.checkpw(password.encode(), stored_password):
        try:
            # Generar token JWT con información del usuario
            token = jwt.encode(
                {
                    "username": user[1],  # Nombre de usuario (posición 1)
                    "role": user[3],  # Rol del usuario (posición 3)
                    "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Expiración en 1 hora
                },
                SECRET_KEY,  # Clave secreta para firmar el token
                algorithm="HS256"  # Algoritmo de encriptación HS256
            )
            # Guardar información del usuario en la sesión de Streamlit
            st.session_state["username"] = user[1]
            st.session_state["token"] = token
            return token
        except Exception as e:
            # Capturar cualquier error en la generación del token
            st.error(f"Error al generar el token: {e}")
            return None

    # Si la contraseña no coincide, mostrar error
    st.error("Contraseña incorrecta.")
    return None

# ============================================================================
# FUNCIÓN: login_page
# Renderiza la página de inicio de sesión con información del sistema
# ============================================================================
def login_page():
    """
    Muestra la interfaz de login con selector de usuarios, campos de entrada
    e información sobre el sistema BCS Millennial Broker
    """
    # ============================================================================
    # ENCABEZADO DE LA PÁGINA CON LOGO Y TÍTULO
    # ============================================================================
    # Crear dos columnas: una pequeña para el logo (1) y una grande para el título (4)
    col1, col2= st.columns([1, 4])
    with col1:
        # Mostrar logo de la aplicación
        st.image("assets/logo.png", width=100)
    with col2:
        # Título principal con colores personalizados (naranja y azul)
        st.title("Bienvenidos al :orange[BCS] de :blue[MILLENNIAL BROKER] ")
    
    # ============================================================================
    # CONTENIDO PRINCIPAL CON 3 COLUMNAS
    # ============================================================================
    # Crear tres columnas de igual tamaño para organizar el contenido
    col1,col2,col3 = st.columns([2, 2, 2])
    # ============================================================================
    # COLUMNA 1: Información del sistema
    # ============================================================================
    with col1:
        # Imagen decorativa
        st.image('assets/image1.png', width=200, )
        # Expander con información sobre qué es el sistema
        with st.expander("¿Qué es el :orange[BCS] :blue[Millennial Broker]?"):
            st.markdown("""
            El **BCS Millennial Broker** es una plataforma integral para la gestión de *clientes*, *pólizas*, *aseguradoras*, *agencias* y *usuarios* del sector asegurador. Permite administrar y consultar información relevante de manera centralizada y segura.
            """)
    
    # ============================================================================
    # COLUMNA 2: Formulario de inicio de sesión
    # ============================================================================
    with col2:
        # Imagen decorativa
        st.image('assets/imagen2.jpg', width=200)
        # Expander con el formulario de login
        with st.expander("Iniciar Sesión como :orange[usuario]"):
            # Obtener lista de usuarios disponibles desde la base de datos
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users")  # Consultar todos los nombres de usuario
            user_list = [row[0] for row in cursor.fetchall()]  # Convertir resultados a lista
            conn.close()
            
            # Mostrar selectbox con usuarios o campo de texto si no hay usuarios
            username = st.selectbox(":blue[Usuario]", user_list) if user_list else st.text_input("Usuario")
            # Campo de contraseña (oculto por type="password")
            password = st.text_input(":blue[Contraseña]", type="password")
            
            # Botón de inicio de sesión
            if st.button("Login"):
                # Intentar autenticar con las credenciales ingresadas
                token = authenticate(username, password)
                if token:
                    # Si la autenticación es exitosa, mostrar mensaje y recargar
                    st.success("Autenticación exitosa!")
                    st.rerun()  # Recargar la página para mostrar el dashboard correspondiente
    # ============================================================================
    # COLUMNA 3: Instrucciones de uso
    # ============================================================================
    with col3:
        # Imagen decorativa
        st.image('assets/image3.jpg', width=200)
        # Expander con instrucciones de uso del sistema
        with st.expander("Instrucciones de uso del :blue[BCS] :orange[Millennial Broker]"):
            st.markdown("""
            - Selecciona tu usuario y contraseña para acceder a tu dashboard personalizado.
            - Navega por los módulos desde la barra lateral izquierda.
            - Cada módulo cuenta con opciones para crear, leer, modificar y borrar registros.
            - Utiliza los formularios y tablas para gestionar la información.
            - Para cerrar sesión, utiliza el botón "Logout" en la barra lateral.
            """)
    
    # ============================================================================
    # FOOTER CON INFORMACIÓN DE CONTACTO Y CRÉDITOS
    # ============================================================================
    st.markdown("""
        <hr style="margin-top:2em;margin-bottom:0.5em;">
        <div style="text-align:center; font-size: 0.95em;">
            Creado por <b>CodeCodix AI Lab @2025</b>
        </div>
        <div style="text-align:center; margin-top:0.5em;">
            <a href="https://wa.me/5930993513082?text=Consulta%20t%C3%A9cnica%20BCS%20Millennial%20Broker" target="_blank">
                <button style="background-color:#25D366; color:white; border:none; padding:8px 18px; border-radius:5px; font-size:1em; cursor:pointer;">
                    Contacto con servicio técnico
                </button>
            </a>
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# FUNCIÓN: main
# Función principal que gestiona el flujo de la aplicación
# ============================================================================
def main():
    """
    Controla el flujo principal de la aplicación:
    1. Inicializa la base de datos
    2. Verifica si existe una sesión activa (token JWT)
    3. Decodifica el token para obtener información del usuario
    4. Redirige al dashboard correspondiente según el rol del usuario
    5. Si no hay sesión, muestra la página de login
    """
    # Inicializar la base de datos (crear tablas si no existen)
    initialize_database()
    
    # Verificar si existe un token de sesión en st.session_state
    if "token" in st.session_state:
        try:
            # Decodificar el token JWT para obtener la información del usuario
            payload = jwt.decode(st.session_state["token"], SECRET_KEY, algorithms=["HS256"])
            username = payload["username"]  # Extraer nombre de usuario
            role = payload["role"]  # Extraer rol del usuario
            
            # Normalizar el rol para comparación robusta (sin espacios, guiones, guiones bajos)
            # Esto permite que "Ejecutivo Comercial", "ejecutivo_comercial" y "ejecutivo-comercial" sean equivalentes
            normalized_role = role.lower().replace(" ", "").replace("_", "").replace("-", "")
            
            # ============================================================================
            # REDIRECCIÓN SEGÚN EL ROL DEL USUARIO
            # ============================================================================ correspondiente según el rol
            if normalized_role == "admin":
                # Usuario administrador: acceso completo a todos los módulos
                admin_dashboard()
            elif normalized_role in ["ejecutivocomercial", "seller"]:
                # Ejecutivo comercial o vendedor: dashboard de ventas
                from dashboards.Ejecutivo_Comercial_dashboard import welcome_message, manage_modules
                welcome_message()  # Mostrar mensaje de bienvenida personalizado
                manage_modules()  # Gestionar módulos disponibles para este rol
            elif normalized_role in ["backofficeoperacion"]:
                # Personal de back office: dashboard de operaciones
                from dashboards.Back_Office_Operacion_dashboard import welcome_message, manage_modules
                welcome_message()  # Mostrar mensaje de bienvenida personalizado
                manage_modules()  # Gestionar módulos disponibles para este rol
            else:
                # Usuario estándar: dashboard básico
                user_dashboard()
                
        except jwt.ExpiredSignatureError:
            # El token JWT ha expirado (después de 1 hora)
            st.error("Sesión expirada, por favor inicie sesión nuevamente")
            del st.session_state["token"]  # Eliminar token expirado de la sesión
            st.rerun()  # Recargar la página para mostrar el login
    else:
        # Si no hay token en la sesión, mostrar la página de login
        login_page()

# ============================================================================
# PUNTO DE ENTRADA DE LA APLICACIÓN
# ============================================================================
if __name__ == "__main__":
    # Inicializar la base de datos al arrancar la aplicación
    initialize_database()
    # Ejecutar la función principal
    main()
