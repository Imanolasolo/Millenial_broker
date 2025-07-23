# 🔧 Guía de Instalación y Configuración - BCS Millenial Broker

## 📋 Requisitos del Sistema

### Requisitos Mínimos de Hardware:
- **CPU**: 2 núcleos, 2.0 GHz
- **RAM**: 4 GB mínimo (8 GB recomendado)
- **Almacenamiento**: 5 GB de espacio libre
- **Red**: Conexión a internet (para dependencias y actualizaciones)

### Requisitos de Software:
- **Sistema Operativo**: Windows 10+, macOS 10.14+, o Linux Ubuntu 18.04+
- **Python**: Versión 3.8 o superior
- **Navegador Web**: Chrome, Firefox, Safari, o Edge (versiones recientes)

### Herramientas de Desarrollo (opcionales):
- **IDE**: VS Code, PyCharm, o similar
- **Git**: Para control de versiones
- **Terminal/CMD**: Para ejecución de comandos

## 🚀 Proceso de Instalación

### Paso 1: Preparar el Entorno

#### Verificar Python
```bash
# Verificar versión de Python
python --version
# o
python3 --version

# Debería mostrar Python 3.8.x o superior
```

#### Verificar pip
```bash
# Verificar pip (gestor de paquetes)
pip --version
# o
pip3 --version
```

#### Instalar Python (si es necesario)
- **Windows**: Descargar desde [python.org](https://www.python.org/downloads/)
- **macOS**: Usar Homebrew `brew install python3` o descargar desde python.org
- **Linux**: `sudo apt update && sudo apt install python3 python3-pip`

### Paso 2: Obtener el Código Fuente

#### Opción A: Clonar Repositorio (recomendado)
```bash
# Clonar el repositorio
git clone [URL_DEL_REPOSITORIO]
cd Millenial_broker

# Verificar contenido
ls -la
```

#### Opción B: Descargar ZIP
1. Descargar el archivo ZIP del proyecto
2. Extraer en la ubicación deseada
3. Navegar a la carpeta extraída

### Paso 3: Configurar Entorno Virtual

#### Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv millenial_broker_env

# Activar entorno virtual
# Windows:
millenial_broker_env\Scripts\activate

# macOS/Linux:
source millenial_broker_env/bin/activate

# Verificar activación (debería mostrar el prompt con el nombre del entorno)
```

#### Ventajas del Entorno Virtual:
- Aislamiento de dependencias
- Evita conflictos con otros proyectos
- Facilita el mantenimiento
- Permite diferentes versiones de librerías

### Paso 4: Instalar Dependencias

#### Instalar desde requirements.txt
```bash
# Instalar todas las dependencias
pip install -r requirements.txt

# Verificar instalación
pip list
```

#### Dependencias Principales:
```
streamlit==1.28.0         # Framework web principal
PyJWT==2.8.0             # Manejo de tokens JWT
bcrypt==4.0.1            # Encriptación de contraseñas
pandas==2.1.1            # Manipulación de datos
PyMuPDF==1.23.5          # Procesamiento de PDFs
langchain==0.0.292       # Framework para IA
langchain-community==0.0.20  # Extensiones LangChain
openai==0.28.1           # API de OpenAI
tiktoken==0.5.1          # Tokenización
faiss-cpu==1.7.4         # Búsqueda vectorial
```

#### Resolver Problemas de Instalación:
```bash
# Si hay errores de permisos (Linux/macOS):
pip install --user -r requirements.txt

# Si hay errores de compilación:
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Instalar dependencias una por una en caso de errores:
pip install streamlit
pip install PyJWT
pip install bcrypt
# ... continuar con cada dependencia
```

## ⚙️ Configuración Inicial

### Configuración de la Base de Datos

El sistema usa SQLite y se configura automáticamente:

#### Archivo: `dbconfig.py`
```python
import os

# Configuración de la base de datos
DB_FILE = "database.db"
SECRET_KEY = "tu_clave_secreta_super_segura_aqui"  # CAMBIAR EN PRODUCCIÓN

# Configuración de la aplicación
DEBUG_MODE = True  # Cambiar a False en producción
```

#### Configuración de Seguridad (IMPORTANTE):
```python
# Para ambiente de producción, usa una clave segura:
import secrets
SECRET_KEY = secrets.token_urlsafe(32)
```

### Configuración de Streamlit

#### Archivo: `.streamlit/config.toml` (crear si no existe)
```toml
[server]
port = 8501
headless = false
enableCORS = false
enableWebsocketCompression = false

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#FF6B35"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Configuración de Variables de Entorno

#### Crear archivo `.env` (opcional)
```bash
# Variables de entorno para producción
DATABASE_URL=sqlite:///database.db
SECRET_KEY=tu_clave_super_secreta
DEBUG=False
STREAMLIT_SERVER_PORT=8501
```

## 🏃‍♂️ Primera Ejecución

### Iniciar la Aplicación
```bash
# Asegurar que el entorno virtual está activado
# Navegar al directorio del proyecto
cd Millenial_broker

# Ejecutar la aplicación
streamlit run app1.py
```

### Verificar Funcionamiento

1. **La aplicación debería mostrar**:
   ```
   You can now view your Streamlit app in your browser.
   Local URL: http://localhost:8501
   Network URL: http://192.168.x.x:8501
   ```

2. **Abrir en navegador**: `http://localhost:8501`

3. **Verificar elementos**:
   - Logo y diseño de la aplicación
   - Pantalla de login
   - Dropdown de usuarios (puede estar vacío inicialmente)

### Inicialización de la Base de Datos

Al ejecutar por primera vez:
1. **Se crean automáticamente**:
   - Archivo `database.db`
   - Tablas necesarias
   - Estructura de la base de datos

2. **Verificar creación**:
   ```bash
   # Verificar que existe el archivo de BD
   ls -la database.db
   ```

## 👤 Configuración de Usuario Inicial

### Crear Usuario Administrador

Como la aplicación inicia sin usuarios, necesitas crear uno manualmente:

#### Opción A: Usar la Consola Python
```python
# Ejecutar en el directorio del proyecto
python3

import sqlite3
import bcrypt
from dbconfig import DB_FILE

# Conectar a la base de datos
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Crear usuario administrador
username = "admin"
password = "admin123"  # CAMBIAR INMEDIATAMENTE
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

cursor.execute("""
    INSERT INTO users (username, password, role, nombres, apellidos, correo)
    VALUES (?, ?, ?, ?, ?, ?)
""", (username, hashed.decode('utf-8'), "Admin", "Administrador", "Sistema", "admin@empresa.com"))

conn.commit()
conn.close()
print("Usuario administrador creado exitosamente")
```

#### Opción B: Modificar el Código Temporalmente

En `app1.py`, agregar temporalmente:
```python
def create_initial_admin():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Verificar si ya existe un admin
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='Admin'")
    if cursor.fetchone()[0] == 0:
        # Crear admin inicial
        hashed = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
        cursor.execute("""
            INSERT INTO users (username, password, role, nombres, apellidos)
            VALUES (?, ?, ?, ?, ?)
        """, ("admin", hashed.decode('utf-8'), "Admin", "Admin", "Inicial"))
        conn.commit()
    
    conn.close()

# Llamar en main() antes de mostrar la interfaz
create_initial_admin()
```

### Primer Login

1. **Usar credenciales temporales**:
   - Usuario: `admin`
   - Contraseña: `admin123`

2. **Cambiar contraseña inmediatamente**:
   - Ir a módulo de Usuarios
   - Modificar usuario admin
   - Establecer contraseña segura

3. **Crear usuarios adicionales**:
   - Usar el módulo de gestión de usuarios
   - Asignar roles apropiados

## 🔧 Configuración Avanzada

### Configuración para Producción

#### 1. Configuración de Seguridad
```python
# dbconfig.py - Versión de producción
import os
from dotenv import load_dotenv

load_dotenv()

DB_FILE = os.getenv("DATABASE_URL", "database.db")
SECRET_KEY = os.getenv("SECRET_KEY")  # Obligatorio desde variable de entorno
DEBUG_MODE = False

if not SECRET_KEY:
    raise ValueError("SECRET_KEY debe estar definido en variables de entorno")
```

#### 2. Configuración de Base de Datos
```bash
# Para PostgreSQL en producción (requiere psycopg2)
pip install psycopg2-binary

# Variable de entorno:
DATABASE_URL=postgresql://user:password@localhost/millenial_broker
```

#### 3. Configuración de Servidor
```bash
# Para deployment con nginx/apache
streamlit run app1.py --server.port 8501 --server.address 0.0.0.0
```

### Configuración de Respaldos

#### Script de Respaldo Automático
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups"
DB_FILE="database.db"

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_DIR/database_backup_$DATE.db

# Mantener solo los últimos 30 respaldos
ls -t $BACKUP_DIR/database_backup_*.db | tail -n +31 | xargs rm -f

echo "Respaldo creado: database_backup_$DATE.db"
```

### Monitoreo y Logs

#### Configuración de Logging
```python
# logging_config.py
import logging
import os

def setup_logging():
    log_level = logging.DEBUG if os.getenv("DEBUG") == "True" else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('millenial_broker.log'),
            logging.StreamHandler()
        ]
    )
```

## 🛠️ Solución de Problemas de Instalación

### Problemas Comunes

#### 1. Error: "Python no reconocido"
```bash
# Windows: Agregar Python al PATH
# Reinstalar Python marcando "Add to PATH"

# Linux/macOS: Usar python3
python3 -m venv millenial_broker_env
```

#### 2. Error de Permisos
```bash
# Linux/macOS:
sudo chmod +x install.sh
pip install --user -r requirements.txt

# Windows: Ejecutar como administrador
```

#### 3. Error de Compilación de bcrypt
```bash
# Windows:
pip install --only-binary=all bcrypt

# Linux:
sudo apt-get install build-essential libffi-dev python3-dev
pip install bcrypt
```

#### 4. Error de Streamlit
```bash
# Limpiar caché de pip
pip cache purge
pip install --upgrade streamlit

# Verificar conflictos
pip check
```

#### 5. Error de Base de Datos
```bash
# Verificar permisos de escritura
ls -la database.db

# Recrear base de datos
rm database.db
# Reiniciar aplicación
```

### Verificación Post-Instalación

#### Lista de Verificación:
- [ ] Python 3.8+ instalado y funcionando
- [ ] Entorno virtual creado y activado
- [ ] Todas las dependencias instaladas sin errores
- [ ] Base de datos creada automáticamente
- [ ] Aplicación inicia sin errores
- [ ] Interfaz accesible en navegador
- [ ] Usuario administrador creado
- [ ] Login funciona correctamente
- [ ] Módulos principales accesibles

#### Script de Verificación:
```python
# verify_installation.py
import sys
import importlib

def check_python_version():
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requerido")
        return False
    print(f"✅ Python {sys.version.split()[0]} detectado")
    return True

def check_dependencies():
    required = ["streamlit", "jwt", "bcrypt", "pandas", "sqlite3"]
    for module in required:
        try:
            importlib.import_module(module)
            print(f"✅ {module} instalado")
        except ImportError:
            print(f"❌ {module} faltante")
            return False
    return True

if __name__ == "__main__":
    print("🔍 Verificando instalación...")
    if check_python_version() and check_dependencies():
        print("🎉 Instalación verificada exitosamente")
    else:
        print("⚠️ Problemas detectados en la instalación")
```

## 📞 Soporte de Instalación

### Contacto Técnico:
- **WhatsApp**: +593 99 351 3082
- **Email**: soporte@codecodix.com
- **Consulta rápida**: [WhatsApp directo](https://wa.me/5930993513082?text=Ayuda%20instalación%20BCS%20Millennial%20Broker)

### Información para Soporte:
Cuando solicites ayuda, incluye:
1. Sistema operativo y versión
2. Versión de Python instalada
3. Mensaje de error completo
4. Pasos realizados antes del error
5. Capturas de pantalla si es útil

---

**Desarrollado por CodeCodix AI Lab**  
*Especialistas en Desarrollo de Software Empresarial*
