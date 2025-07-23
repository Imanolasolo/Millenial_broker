# 📖 Manual de Usuario - BCS Millenial Broker

## 🎯 Introducción

Este manual está diseñado para guiar a los usuarios en el uso efectivo del sistema BCS Millenial Broker. El sistema está diseñado para ser intuitivo, pero este manual te ayudará a aprovechar al máximo todas sus funcionalidades.

## 🚀 Primeros Pasos

### Acceso al Sistema

1. **Abrir la aplicación** en tu navegador web
2. **Pantalla de Login**: Verás una interfaz de bienvenida con:
   - Logo de Millenial Broker
   - Selector de usuario (dropdown)
   - Campo de contraseña
   - Información sobre el sistema

3. **Iniciar Sesión**:
   - Selecciona tu usuario del dropdown
   - Ingresa tu contraseña
   - Haz clic en "Login"

### Navegación General

Una vez autenticado, accederás a tu dashboard personalizado según tu rol. La navegación se realiza principalmente através de:

- **Barra lateral izquierda**: Módulos disponibles según tu rol
- **Área principal**: Contenido del módulo seleccionado
- **Botón Logout**: Cerrar sesión (siempre visible en la barra lateral)

## 👥 Roles y Accesos

### 🔴 Administrador
**Acceso completo a todos los módulos:**

1. **Usuarios**: Gestión completa de usuarios del sistema
2. **Clientes**: Administración de clientes (personas y empresas)
3. **Aseguradoras**: Gestión de compañías aseguradoras
4. **Agencias**: Administración de agencias
5. **Roles**: Gestión de roles y permisos
6. **Pólizas**: Gestión completa de pólizas
7. **Reportes**: Acceso a todos los reportes

### 🟡 Ejecutivo Comercial
**Enfoque en ventas y relación con clientes:**

1. **Gestión de Clientes**: Crear y gestionar prospectos
2. **Pólizas**: Crear y seguir pólizas de sus clientes
3. **Reportes de Ventas**: Métricas de su desempeño

### 🟢 Back Office - Operación
**Enfoque operativo y procesamiento:**

1. **Gestión de Pólizas**: Procesamiento operativo
2. **Automatizaciones**: Herramientas para optimizar procesos
3. **Control de Operaciones**: Supervisión de procesos

## 📝 Guías por Módulo

### 👥 Gestión de Usuarios

#### Crear Usuario
1. Navega a **Usuarios** en la barra lateral
2. Selecciona **"Crear"** en el selector de operaciones
3. Completa el formulario:
   - **Username**: Único en el sistema
   - **Password**: Mínimo 8 caracteres
   - **Rol**: Selecciona según las responsabilidades
   - **Datos personales**: Nombres, apellidos, correo, teléfono
4. Haz clic en **"Crear Usuario"**

#### Consultar Usuarios
1. Selecciona **"Leer"** en el selector de operaciones
2. Visualiza la tabla con todos los usuarios
3. Usa los filtros disponibles para buscar usuarios específicos

#### Modificar Usuario
1. Selecciona **"Modificar"** en el selector de operaciones
2. Elige el usuario a modificar del dropdown
3. Actualiza los campos necesarios
4. Haz clic en **"Actualizar Usuario"**

#### Eliminar Usuario
1. Selecciona **"Borrar"** en el selector de operaciones
2. Elige el usuario a eliminar
3. Confirma la acción (esta acción es irreversible)

### 🏢 Gestión de Clientes

#### Tipos de Cliente

**Persona Natural (Individual):**
- Datos personales básicos
- Información de contacto
- Datos adicionales (profesión, ingresos, etc.)
- Historial médico y siniestros

**Persona Jurídica (Empresa):**
- Razón social y nombre comercial
- RUC y representante legal
- Actividad económica detallada
- Información corporativa

#### Crear Cliente

1. Navega a **Clientes** → **"Crear"**
2. **Selecciona el tipo de cliente**:
   - Individual: Para personas naturales
   - Empresa: Para personas jurídicas

3. **Para Personas Naturales**:
   - Tipo de documento (Cédula, Pasaporte)
   - Nombres y apellidos completos
   - Información de contacto
   - Datos adicionales opcionales

4. **Para Empresas**:
   - Razón social
   - RUC (validación automática)
   - Representante legal
   - Actividad económica
   - Información de contacto corporativa

5. **Validaciones automáticas**:
   - Formato de documentos
   - Unicidad de RUC/Cédula
   - Formato de emails y teléfonos

### 🏦 Gestión de Aseguradoras

#### Crear Aseguradora
1. Navega a **Aseguradoras** → **"Crear"**
2. Completa la información básica:
   - Tipo de contribuyente
   - Identificación (RUC)
   - Razón social y nombre comercial
   - País y representante legal
   - Sitio web y correo electrónico
3. Selecciona los ramos de seguros que maneja
4. Guarda la información

#### Gestionar Sucursales
1. Selecciona **"Sucursales"** en el módulo de aseguradoras
2. Elige la aseguradora
3. **Ver sucursales existentes** o **crear nueva sucursal**
4. Para nueva sucursal:
   - Nombre de la sucursal
   - Ciudad y dirección
   - Información de contacto

### 📄 Gestión de Pólizas

El proceso de creación de pólizas es el más complejo del sistema y se divide en varios pasos:

#### Paso 1: Información General

1. Navega a **Pólizas** → **"Crear"**
2. **Selecciona la aseguradora** del dropdown
3. **Selecciona la sucursal** (se carga automáticamente según la aseguradora)
4. **Información básica**:
   - Número de póliza (mínimo 10 caracteres, único)
   - Fecha de emisión
   - Tomador de la póliza (seleccionar cliente existente)
   - Beneficiario
5. **Vigencia**:
   - Fecha de inicio
   - Fecha de fin
   - Los días de cobertura se calculan automáticamente
6. **Configuración**:
   - Tipo de riesgo (Nueva/Renovación)
   - Agrupadora (si aplica)
   - Formas de pago
   - Tipo de facturación
7. Haz clic en **"Siguiente"**

#### Paso 2: Información de Facturación

1. **Selección del ramo**: Tipo de seguro
2. **Datos de anexos**:
   - Cantidad de anexos
   - Descripción de cada anexo
3. **Información económica**:
   - Prima del seguro
   - Suma asegurada
   - Observaciones de la póliza
4. **Datos de factura**:
   - Número de factura
   - Moneda
   - Cláusulas particulares
5. **Cálculos fiscales**:
   - Contribuciones SCVS
   - Derechos de emisión
   - IVA (15%)
   - Contribución solidaria (2%)
   - Otros conceptos
6. **Total automático**: Se calcula con todos los conceptos
7. Haz clic en **"Guardar datos de facturación"**

#### Paso 3: Información Adicional

1. **Configuración de renovación**:
   - Tipo renovación (Manual/Automático)
   - Tipo de movimiento (Alta/Baja/Modificación)
2. **Asignación comercial**:
   - Ejecutivo comercial responsable
   - Liberación de comisión
3. **Finalizar**: Haz clic en **"Crear Póliza"**

#### Consultar Pólizas

1. Selecciona **"Leer"** en el módulo de pólizas
2. **Visualización en formato JSON** con información estructurada:
   - Datos del tomador
   - Información de la aseguradora y sucursal
   - Detalles económicos
   - Anexos y observaciones
   - Fechas y vigencias

#### Modificar Pólizas

1. Selecciona **"Modificar"**
2. Elige la póliza del dropdown (por número de póliza)
3. **Formulario pre-llenado** con datos actuales
4. Modifica los campos necesarios
5. Guarda los cambios

### ⚙️ Gestión de Roles

#### Crear Rol
1. Navega a **Roles** → **"Crear"**
2. Ingresa el nombre del rol (único)
3. Haz clic en **"Crear Rol"**

#### Modificar Rol
1. Selecciona **"Modificar"**
2. Elige el rol a modificar
3. Ingresa el nuevo nombre
4. Confirma los cambios

## 🔧 Funciones Especiales

### 🤖 Automatizaciones (Back Office)

#### Gestionar Pólizas por Cliente
1. Navega a **Automatizaciones** → **"Gestionar pólizas por cliente"**
2. **Selecciona un cliente** del dropdown
3. **Visualiza todas sus pólizas** con opciones para:
   - Ver detalles completos
   - Modificar datos específicos
   - Actualizar estado

#### Crear Póliza por Cliente
1. Selecciona **"Crear póliza por cliente"**
2. **Formulario simplificado** con campos esenciales
3. **Pre-selecciones inteligentes** basadas en el historial del cliente
4. **Validaciones automáticas** para agilizar el proceso

### 📊 Reportes y Consultas

#### Dashboard Personalizado
Cada rol tiene un dashboard con:
- **Métricas relevantes** para su función
- **Accesos rápidos** a tareas frecuentes
- **Notificaciones** y alertas importantes

#### Generación de Reportes
- **Filtros avanzados** por fechas, usuarios, aseguradoras
- **Exportación** a diferentes formatos
- **Reportes automáticos** programados

## 💡 Consejos y Mejores Prácticas

### Para Todos los Usuarios:
1. **Logout seguro**: Siempre cierra sesión al terminar
2. **Datos únicos**: Verifica que números de póliza y documentos sean únicos
3. **Validaciones**: Presta atención a los mensajes de validación
4. **Respaldos**: Los datos se guardan automáticamente

### Para Administradores:
1. **Gestión de usuarios**: Asigna roles según responsabilidades reales
2. **Mantenimiento**: Revisa periódicamente la integridad de datos
3. **Seguridad**: Cambia contraseñas predeterminadas

### Para Ejecutivos Comerciales:
1. **Datos de clientes**: Mantén información actualizada para mejor servicio
2. **Seguimiento**: Usa el módulo de pólizas para seguimiento post-venta
3. **Reportes**: Revisa métricas regularmente para mejorar performance

### Para Back Office:
1. **Validaciones**: Verifica datos antes de procesar pólizas
2. **Automatizaciones**: Usa herramientas de automatización para eficiencia
3. **Documentación**: Mantén observaciones detalladas en las pólizas

## ❗ Solución de Problemas Comunes

### Error de Login
- **Problema**: No puedo iniciar sesión
- **Solución**: Verifica usuario y contraseña, contacta al administrador si persiste

### Error de Validación de Datos
- **Problema**: El sistema rechaza datos válidos
- **Solución**: Verifica formato exacto requerido (teléfonos, emails, documentos)

### Póliza Duplicada
- **Problema**: Error al crear póliza por número duplicado
- **Solución**: Verifica que el número de póliza sea único (mínimo 10 caracteres)

### Datos No Guardados
- **Problema**: Los cambios no se guardan
- **Solución**: Verifica que todos los campos obligatorios estén completos

### Sesión Expirada
- **Problema**: Sesión se cierra automáticamente
- **Solución**: Vuelve a iniciar sesión, es una medida de seguridad

## 📞 Soporte Técnico

### Contacto:
- **WhatsApp**: +593 99 351 3082
- **Consulta rápida**: [Enlace directo](https://wa.me/5930993513082?text=Consulta%20t%C3%A9cnica%20BCS%20Millennial%20Broker)

### Información para Soporte:
Cuando contactes soporte, incluye:
1. Tu rol de usuario
2. Módulo donde ocurre el problema
3. Descripción detallada del error
4. Pasos para reproducir el problema

---

**Desarrollado por CodeCodix AI Lab**  
*Especialistas en Soluciones Empresariales Digitales*
