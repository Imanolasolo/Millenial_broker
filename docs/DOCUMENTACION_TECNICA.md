# 📊 Documentación Técnica - BCS Millenial Broker

## 🏗️ Arquitectura del Sistema

### Diagrama de Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                      CLIENTE (NAVEGADOR)                        │
│                    http://localhost:8501                        │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/WebSocket
┌─────────────────────▼───────────────────────────────────────────┐
│                   STREAMLIT SERVER                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Frontend   │  │  Routing    │  │  Session    │             │
│  │  Components │  │  Logic      │  │  Management │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Function Calls
┌─────────────────────▼───────────────────────────────────────────┐
│                   BUSINESS LOGIC                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    CRUD     │  │    Auth     │  │  Validation │             │
│  │  Operations │  │   Service   │  │   Logic     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────┬───────────────────────────────────────────┘
                      │ SQL Queries
┌─────────────────────▼───────────────────────────────────────────┐
│                    SQLITE DATABASE                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Tables    │  │   Indexes   │  │  Triggers   │             │
│  │   & Data    │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### Componentes Principales

#### 1. **Frontend Layer (Streamlit)**
- **Responsabilidades**: Renderizado de UI, manejo de eventos, validación de formularios
- **Tecnologías**: Streamlit, HTML/CSS embebido, JavaScript mínimo
- **Archivos**: `app1.py`, `htmlTemplates.py`, archivos en `/dashboards/`

#### 2. **Business Logic Layer**
- **Responsabilidades**: Lógica de negocio, validaciones, procesamiento de datos
- **Tecnologías**: Python puro, pandas para manipulación de datos
- **Archivos**: Módulos en `/crud/`, funciones de utilidad

#### 3. **Data Access Layer**
- **Responsabilidades**: Conexión a BD, operaciones CRUD, migraciones
- **Tecnologías**: SQLite3, SQL nativo
- **Archivos**: `database_config.py`, `dbconfig.py`

#### 4. **Security Layer**
- **Responsabilidades**: Autenticación, autorización, encriptación
- **Tecnologías**: JWT, bcrypt, Python standard library
- **Implementación**: Transversal en todos los módulos

## 🗄️ Diseño de Base de Datos

### Diagrama de Entidad-Relación

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     USERS       │     │    CLIENTS      │     │  ASEGURADORAS   │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ id (PK)         │     │ id (PK)         │     │ id (PK)         │
│ username        │     │ tipo_cliente    │     │ tipo_contrib.   │
│ password        │     │ tipo_documento  │     │ identificacion  │
│ role            │     │ numero_doc      │     │ razon_social    │
│ correo          │     │ nombres         │     │ nombre_comercial│
│ nombres         │     │ apellidos       │     │ pais            │
│ apellidos       │     │ razon_social    │     │ representante   │
│ telefono        │     │ correo_elect.   │     │ web             │
│ fecha_registro  │     │ telefono1       │     │ correo_elect.   │
│ company_id      │     │ direccion       │     └─────────────────┘
└─────────────────┘     │ actividad_econ. │              │
         │               └─────────────────┘              │
         │                        │                       │
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                        POLIZAS                                  │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                                                         │
│ numero_poliza (UNIQUE)                                          │
│ cliente_id (FK → CLIENTS.id)                                    │
│ usuario_id (FK → USERS.id)                                      │
│ aseguradora_id (FK → ASEGURADORAS.id)                          │
│ sucursal_id (FK → SUCURSALES.id)                               │
│ ramo_id (FK → RAMOS_SEGUROS.id)                                │
│ fecha_emision, fecha_inicio, fecha_fin                         │
│ prima, suma_asegurada, deducible                               │
│ anexos_poliza, observaciones_poliza                            │
│ tipo_renovacion, tipo_movimiento                               │
│ formas_de_pago, tipo_facturacion                               │
│ numero_factura, moneda                                          │
│ contrib_scvs, derechos_emision, iva_15                        │
│ csolidaria_2, financiacion, otros_iva, total                  │
└─────────────────────────────────────────────────────────────────┘
```

### Tablas Principales y Relaciones

#### Tabla: `users`
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,               -- bcrypt hash
    role TEXT NOT NULL,                  -- Admin, Ejecutivo Comercial, etc.
    correo TEXT,
    nombres TEXT,
    apellidos TEXT,
    telefono TEXT,
    fecha_registro TEXT,                 -- ISO date string
    ultima_actualizacion TEXT,
    company_id INTEGER                   -- FK para asociaciones empresariales
);
```

#### Tabla: `clients`
```sql
CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_cliente TEXT CHECK(tipo_cliente IN ('Individual', 'Empresa')),
    tipo_documento TEXT,                 -- Cédula, RUC, Pasaporte
    numero_documento TEXT UNIQUE NOT NULL,
    nombres TEXT,                        -- Para personas naturales
    apellidos TEXT,                      -- Para personas naturales
    razon_social TEXT,                   -- Para empresas
    nombre_comercial TEXT,               -- Para empresas
    actividad_economica TEXT,
    subactividad_economica TEXT,
    telefono1 TEXT,
    telefono2 TEXT,
    correo_electronico TEXT,
    direccion_domicilio TEXT,
    sector_mercado TEXT,                 -- Público, Privado, etc.
    tipo_empresa_categoria TEXT,         -- Micro, Pequeña, Mediana, Grande
    tipo_persona_juridica TEXT,
    pagina_web TEXT,
    fecha_aniversario TEXT,
    numero_ruc TEXT,
    representante_legal_id INTEGER,
    contacto_autorizado_id INTEGER,
    observaciones_legales TEXT,
    canal_preferido_contacto TEXT,
    notas_adicionales TEXT,
    fecha_registro TEXT,
    ultima_actualizacion TEXT
);
```

#### Tabla: `polizas`
```sql
CREATE TABLE polizas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_poliza TEXT UNIQUE NOT NULL,
    cliente_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    aseguradora_id INTEGER NOT NULL,
    sucursal_id INTEGER,
    ramo_id INTEGER,
    
    -- Fechas
    fecha_emision TEXT,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    
    -- Información económica
    prima REAL,
    suma_asegurada REAL,
    deducible REAL,
    
    -- Información adicional
    beneficiario TEXT,
    tomador_id INTEGER,
    tomador_nombre TEXT,               -- Denormalizado para consultas rápidas
    tipo_riesgo TEXT,                  -- Nueva, Renovación
    anexos_poliza TEXT,                -- JSON array de anexos
    observaciones_poliza TEXT,
    
    -- Facturación
    formas_de_pago TEXT,               -- Contado, Cuotas, Crédito
    tipo_de_facturacion TEXT,          -- Anual, Semestral, etc.
    numero_factura TEXT,
    moneda TEXT DEFAULT 'USD',
    clausulas_particulares TEXT,
    
    -- Cálculos fiscales
    contrib_scvs REAL,                 -- Contribución SCVS
    derechos_emision REAL,
    ssoc_camp REAL,                    -- Seguro Social Campesino
    subtotal REAL,
    iva_15 REAL,                       -- IVA 15%
    csolidaria_2 REAL,                 -- Contribución Solidaria 2%
    financiacion REAL,
    otros_iva REAL,
    total REAL,
    
    -- Gestión comercial
    tipo_renovacion TEXT CHECK(tipo_renovacion IN ('MANUAL', 'AUTOMATICO')),
    tipo_movimiento TEXT CHECK(tipo_movimiento IN ('ALTA', 'BAJA', 'MODIFICACION')),
    gestion_cobro INTEGER,             -- FK a users (ejecutivo comercial)
    liberacion_comision TEXT CHECK(liberacion_comision IN ('SI', 'NO')),
    agrupadora INTEGER,                -- FK a companies
    
    -- Constraints
    FOREIGN KEY (cliente_id) REFERENCES clients(id) ON DELETE RESTRICT,
    FOREIGN KEY (usuario_id) REFERENCES users(id) ON DELETE RESTRICT,
    FOREIGN KEY (aseguradora_id) REFERENCES aseguradoras(id) ON DELETE RESTRICT,
    FOREIGN KEY (sucursal_id) REFERENCES sucursales(id) ON DELETE SET NULL,
    FOREIGN KEY (tomador_id) REFERENCES clients(id) ON DELETE SET NULL,
    FOREIGN KEY (gestion_cobro) REFERENCES users(id) ON DELETE SET NULL
);
```

#### Tabla: `aseguradoras`
```sql
CREATE TABLE aseguradoras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_contribuyente TEXT CHECK(tipo_contribuyente IN ('Persona Natural', 'Persona Jurídica')),
    tipo_identificacion TEXT CHECK(tipo_identificacion IN ('Cédula', 'RUC', 'Pasaporte')),
    identificacion TEXT UNIQUE NOT NULL,
    razon_social TEXT NOT NULL,
    nombre_comercial TEXT,
    pais TEXT DEFAULT 'Ecuador',
    representante_legal TEXT,
    aniversario TEXT,                  -- Fecha de aniversario
    web TEXT,                          -- Sitio web
    correo_electronico TEXT
);
```

#### Tabla: `sucursales`
```sql
CREATE TABLE sucursales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aseguradora_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    ciudad TEXT,
    direccion TEXT,
    telefono TEXT,
    email TEXT,
    FOREIGN KEY (aseguradora_id) REFERENCES aseguradoras(id) ON DELETE CASCADE
);
```

### Índices para Optimización

```sql
-- Índices para mejorar performance de consultas frecuentes
CREATE INDEX idx_polizas_cliente_id ON polizas(cliente_id);
CREATE INDEX idx_polizas_usuario_id ON polizas(usuario_id);
CREATE INDEX idx_polizas_aseguradora_id ON polizas(aseguradora_id);
CREATE INDEX idx_polizas_numero ON polizas(numero_poliza);
CREATE INDEX idx_polizas_fecha_emision ON polizas(fecha_emision);
CREATE INDEX idx_clients_documento ON clients(numero_documento);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
```

## 🔐 Arquitectura de Seguridad

### Flujo de Autenticación

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Usuario   │    │   Frontend  │    │   Backend   │    │  Database   │
│   (Login)   │    │ (Streamlit) │    │   (Auth)    │    │  (SQLite)   │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │                  │
1. Credenciales           │                  │                  │
       ├─────────────────►│                  │                  │
       │                  │                  │                  │
       │              2. Validar            │                  │
       │                  ├─────────────────►│                  │
       │                  │                  │                  │
       │                  │              3. Query              │
       │                  │                  ├─────────────────►│
       │                  │                  │                  │
       │                  │              4. User Data          │
       │                  │                  │◄─────────────────┤
       │                  │                  │                  │
       │                  │           5. bcrypt.checkpw        │
       │                  │                  ├──────────┐       │
       │                  │                  │          │       │
       │                  │                  │◄─────────┘       │
       │                  │                  │                  │
       │              6. Generate JWT        │                  │
       │                  │◄─────────────────┤                  │
       │                  │                  │                  │
   7. JWT Token           │                  │                  │
       │◄─────────────────┤                  │                  │
       │                  │                  │                  │
   8. Store in Session    │                  │                  │
       ├─────────────────►│                  │                  │
```

### Componentes de Seguridad

#### 1. **Gestión de Contraseñas**
```python
import bcrypt

def hash_password(password: str) -> str:
    """Genera hash seguro de contraseña usando bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verifica contraseña contra hash almacenado"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
```

#### 2. **Gestión de JWT**
```python
import jwt
from datetime import datetime, timedelta

def generate_token(username: str, role: str, secret_key: str) -> str:
    """Genera token JWT con expiración"""
    payload = {
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(hours=24),  # Expira en 24 horas
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_token(token: str, secret_key: str) -> dict:
    """Verifica y decodifica token JWT"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expirado")
    except jwt.InvalidTokenError:
        raise Exception("Token inválido")
```

#### 3. **Control de Acceso Basado en Roles**
```python
def require_role(required_roles: list):
    """Decorator para verificar roles requeridos"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if 'token' not in st.session_state:
                st.error("Acceso no autorizado")
                return
            
            try:
                payload = verify_token(st.session_state['token'], SECRET_KEY)
                user_role = payload.get('role')
                
                if user_role not in required_roles:
                    st.error(f"Acceso denegado. Rol requerido: {required_roles}")
                    return
                
                return func(*args, **kwargs)
            except Exception as e:
                st.error(f"Error de autenticación: {e}")
                return
        return wrapper
    return decorator

# Uso del decorator
@require_role(['Admin'])
def admin_only_function():
    # Código que solo pueden ejecutar administradores
    pass
```

## 🛠️ Patrones de Diseño Utilizados

### 1. **CRUD Pattern**
Cada entidad tiene su módulo CRUD con operaciones estándar:

```python
# Estructura estándar de módulos CRUD
class EntityCRUD:
    def create(self, data: dict) -> str:
        """Crear nueva entidad"""
        pass
    
    def read(self, filters: dict = None) -> list:
        """Leer entidades con filtros opcionales"""
        pass
    
    def update(self, entity_id: int, data: dict) -> str:
        """Actualizar entidad existente"""
        pass
    
    def delete(self, entity_id: int) -> str:
        """Eliminar entidad"""
        pass
```

### 2. **Session State Pattern**
Uso de `st.session_state` para mantener estado entre requests:

```python
def initialize_session_state():
    """Inicializar variables de sesión"""
    if 'token' not in st.session_state:
        st.session_state['token'] = None
    
    if 'poliza_form_step' not in st.session_state:
        st.session_state['poliza_form_step'] = 1
    
    if 'poliza_form_data' not in st.session_state:
        st.session_state['poliza_form_data'] = {}
```

### 3. **Factory Pattern** (para Dashboards)
Creación de dashboards específicos según el rol:

```python
def create_dashboard(role: str):
    """Factory para crear dashboard según rol"""
    dashboards = {
        'Admin': admin_dashboard,
        'Ejecutivo Comercial': ejecutivo_comercial_dashboard,
        'Back Office - Operacion': back_office_dashboard,
    }
    
    dashboard_func = dashboards.get(role, user_dashboard)
    return dashboard_func()
```

### 4. **Template Method Pattern**
Estructura común para formularios CRUD:

```python
def crud_template(entity_name: str, operations: dict):
    """Template para interfaces CRUD"""
    st.subheader(f"Gestión de {entity_name}")
    
    operation = st.selectbox("Selecciona una operación", 
                           list(operations.keys()))
    
    if operation in operations:
        operations[operation]()
```

## 📦 Estructura de Módulos

### Organización del Código

```
app1.py                          # Punto de entrada principal
├── Authentication              # Funciones de autenticación
├── Session Management          # Gestión de sesiones
└── Routing Logic              # Redirección a dashboards

database_config.py               # Configuración e inicialización de BD
├── Table Creation             # DDL para todas las tablas
├── Default Data               # Datos iniciales
└── Migration Logic            # Lógica de migración

dbconfig.py                      # Configuración de conexión
├── Database Path              # Ubicación de la BD
├── Secret Keys                # Claves de seguridad
└── Environment Config         # Configuración por ambiente

crud/                           # Módulos de lógica de negocio
├── user_crud.py               # CRUD de usuarios
├── client_crud.py             # CRUD de clientes
├── poliza_crud.py             # CRUD de pólizas (más complejo)
├── aseguradora_crud.py        # CRUD de aseguradoras
├── agencias_crud.py           # CRUD de agencias
└── role_crud.py               # CRUD de roles

dashboards/                     # Interfaces por rol
├── admin_dashboard.py         # Dashboard completo de administrador
├── user_dashboard.py          # Dashboard básico de usuario
├── Ejecutivo_Comercial_dashboard.py  # Dashboard de ventas
└── Back_Office_Operacion_dashboard.py # Dashboard operativo

assets/                         # Recursos estáticos
├── logo.png                   # Logo del sistema
├── images/                    # Imágenes de interfaz
└── styles/                    # Estilos CSS personalizados
```

### Dependencias entre Módulos

```
app1.py
├── database_config.py
├── dbconfig.py
├── dashboards/
│   ├── admin_dashboard.py
│   │   └── crud/ (todos los módulos)
│   ├── user_dashboard.py
│   └── otros_dashboards.py
│       └── crud/ (módulos específicos)
└── htmlTemplates.py

crud/
├── Dependencias comunes:
│   ├── sqlite3
│   ├── streamlit
│   ├── pandas
│   └── dbconfig.py
└── Interdependencias:
    ├── client_crud.py ← poliza_crud.py
    ├── user_crud.py ← poliza_crud.py
    └── aseguradora_crud.py ← poliza_crud.py
```

## 🔄 Flujos de Datos Principales

### Flujo de Creación de Póliza

```
1. INICIO → Dashboard → Módulo Pólizas → Crear
                ↓
2. FORMULARIO 1: Información General
   ├── Selección Aseguradora → get_aseguradora_options()
   ├── Selección Sucursal → get_sucursales_by_aseguradora_id()
   ├── Selección Cliente → get_client_options()
   └── Validaciones → Siguiente
                ↓
3. FORMULARIO 2: Datos de Facturación
   ├── Selección Ramo → get_ramos_options()
   ├── Cálculos Automáticos (IVA, total)
   └── Validaciones → Guardar facturación
                ↓
4. FORMULARIO 3: Información Adicional
   ├── Selección Ejecutivo → get_ejecutivo_comercial_options()
   ├── Configuración final
   └── Validaciones → Crear Póliza
                ↓
5. PERSISTENCIA
   ├── Inserción en tabla polizas
   ├── Validación de constraints
   └── Confirmación → SUCCESS/ERROR
```

### Flujo de Autenticación

```
1. LOGIN PAGE
   ├── Cargar usuarios disponibles
   ├── Validar credenciales
   └── Generar JWT token
                ↓
2. DASHBOARD ROUTING
   ├── Verificar token válido
   ├── Extraer rol del token
   └── Redireccionar a dashboard apropiado
                ↓
3. DASHBOARD SPECIFIC
   ├── Cargar módulos según rol
   ├── Verificar permisos por operación
   └── Renderizar interfaz personalizada
```

## 🚀 APIs y Servicios

### API de Datos (Funciones de Consulta)

```python
# Servicios de consulta comunes
def get_client_options() -> List[Tuple[int, str]]:
    """Retorna lista de clientes para dropdowns"""
    
def get_aseguradora_options() -> List[Tuple[int, str]]:
    """Retorna lista de aseguradoras para dropdowns"""
    
def get_user_options() -> List[Tuple[int, str]]:
    """Retorna lista de usuarios para dropdowns"""
    
def get_poliza_details(poliza_id: int) -> Dict:
    """Retorna detalles completos de una póliza"""
```

### Servicios de Validación

```python
def validate_document_number(doc_type: str, doc_number: str) -> bool:
    """Valida formato de documentos de identidad"""
    
def validate_email_format(email: str) -> bool:
    """Valida formato de email"""
    
def validate_phone_format(phone: str) -> bool:
    """Valida formato de teléfono (+593XXXXXXXXX)"""
    
def validate_poliza_number(numero: str) -> bool:
    """Valida que número de póliza tenga mínimo 10 caracteres"""
```

### Servicios de Cálculo

```python
def calculate_policy_totals(prima: float, contrib_scvs: float, 
                          derechos_emision: float) -> Dict:
    """Calcula totales de póliza con impuestos"""
    
def calculate_coverage_days(fecha_inicio: date, fecha_fin: date) -> int:
    """Calcula días de cobertura"""
    
def calculate_iva(subtotal: float, rate: float = 0.15) -> float:
    """Calcula IVA según tasa especificada"""
```

## 📈 Optimizaciones y Performance

### Optimizaciones de Base de Datos

1. **Índices Estratégicos**:
   - Campos de búsqueda frecuente
   - Foreign keys para JOINs
   - Campos únicos para validación

2. **Consultas Optimizadas**:
   ```sql
   -- Consulta optimizada para dashboard
   SELECT p.numero_poliza, c.razon_social, a.razon_social as aseguradora
   FROM polizas p
   JOIN clients c ON p.cliente_id = c.id
   JOIN aseguradoras a ON p.aseguradora_id = a.id
   WHERE p.fecha_emision >= date('now', '-30 days')
   ORDER BY p.fecha_emision DESC;
   ```

3. **Evitar N+1 Queries**:
   ```python
   # Malo: Una query por cada póliza
   for poliza in polizas:
       cliente = get_client_by_id(poliza.cliente_id)
   
   # Bueno: Una query para todos los clientes
   client_ids = [p.cliente_id for p in polizas]
   clientes = get_clients_by_ids(client_ids)
   ```

### Optimizaciones de Frontend

1. **Caching de Streamlit**:
   ```python
   @st.cache_data
   def load_static_data():
       """Cache datos que no cambian frecuentemente"""
       return get_aseguradoras(), get_ramos(), get_countries()
   ```

2. **Session State Eficiente**:
   ```python
   # Evitar recálculos innecesarios
   if 'expensive_calculation' not in st.session_state:
       st.session_state['expensive_calculation'] = heavy_computation()
   ```

3. **Lazy Loading**:
   ```python
   # Cargar datos solo cuando se necesiten
   if operation == "Leer":
       data = load_polizas_data()  # Solo al seleccionar "Leer"
   ```

## 🧪 Testing y Calidad

### Estrategia de Testing

```python
# tests/test_auth.py
import unittest
from unittest.mock import patch, MagicMock
import bcrypt
import jwt

class TestAuthentication(unittest.TestCase):
    
    def test_password_hashing(self):
        """Test de hash y verificación de contraseñas"""
        password = "test123"
        hashed = hash_password(password)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrong", hashed))
    
    def test_jwt_generation(self):
        """Test de generación y verificación de JWT"""
        token = generate_token("testuser", "Admin", "secret")
        payload = verify_token(token, "secret")
        self.assertEqual(payload['username'], "testuser")
        self.assertEqual(payload['role'], "Admin")

# tests/test_crud.py
class TestPolizaCRUD(unittest.TestCase):
    
    def setUp(self):
        """Configurar BD de prueba"""
        self.test_db = ":memory:"
        initialize_test_database(self.test_db)
    
    def test_create_poliza(self):
        """Test de creación de póliza"""
        poliza_data = {
            'numero_poliza': 'TEST123456789',
            'cliente_id': 1,
            'aseguradora_id': 1,
            'prima': 1000.0
        }
        result = create_poliza(poliza_data)
        self.assertIn("exitosamente", result)
```

### Métricas de Calidad

1. **Code Coverage**: Objetivo >80%
2. **Complexity**: Función max 10 líneas, clase max 200 líneas
3. **Documentation**: Docstrings en todas las funciones públicas
4. **Type Hints**: Para funciones críticas

```python
def create_poliza(data: Dict[str, Any]) -> str:
    """
    Crea una nueva póliza en el sistema.
    
    Args:
        data: Diccionario con datos de la póliza
        
    Returns:
        str: Mensaje de confirmación o error
        
    Raises:
        ValidationError: Si los datos no son válidos
        DatabaseError: Si hay problemas de BD
    """
```

## 📚 Documentación para Desarrolladores

### Convenciones de Código

1. **Naming Conventions**:
   - Variables: `snake_case`
   - Funciones: `snake_case`
   - Clases: `PascalCase`
   - Constantes: `UPPER_CASE`

2. **File Organization**:
   - Un módulo por entidad
   - Máximo 500 líneas por archivo
   - Imports ordenados (stdlib, third-party, local)

3. **Error Handling**:
   ```python
   try:
       result = risky_operation()
       return f"Éxito: {result}"
   except SpecificError as e:
       logging.error(f"Error específico: {e}")
       return f"Error: {str(e)}"
   except Exception as e:
       logging.error(f"Error inesperado: {e}")
       return "Error interno del sistema"
   ```

### Guía de Contribución

1. **Branch Strategy**:
   - `main`: Código de producción
   - `develop`: Integración de features
   - `feature/`: Nuevas funcionalidades
   - `hotfix/`: Correcciones críticas

2. **Commit Messages**:
   ```
   feat: agregar validación de RUC en clientes
   fix: corregir cálculo de IVA en pólizas
   docs: actualizar documentación de API
   refactor: simplificar lógica de autenticación
   ```

3. **Pull Request Process**:
   - Tests pasando
   - Code review aprobado
   - Documentación actualizada
   - Sin conflictos con main

---

**Desarrollado por CodeCodix AI Lab**  
*Especialistas en Arquitectura de Software Empresarial*
