# 📚 Índice de Documentación - BCS Millenial Broker

Bienvenido al centro de documentación del sistema BCS Millenial Broker. Esta es tu guía completa para entender, instalar, usar y mantener el sistema.

## 🎯 Navegación Rápida

### 👥 Para Usuarios
- [📖 Manual de Usuario](docs/MANUAL_USUARIO.md) - Guía completa para usar el sistema
- [🚀 Guía de Inicio Rápido](#guía-de-inicio-rápido) - Comenzar en 5 minutos

### 👨‍💻 Para Desarrolladores  
- [🔧 Documentación Técnica](docs/DOCUMENTACION_TECNICA.md) - Arquitectura y especificaciones técnicas
- [🛠️ Guía de Instalación](docs/GUIA_INSTALACION.md) - Configuración e instalación detallada

### 🚀 Para DevOps
- [🐳 Guía de Deployment](docs/GUIA_DEPLOYMENT.md) - Despliegue en producción
- [📊 Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento) - Operaciones y soporte

### 📋 Información General
- [📄 README Principal](README.md) - Visión general del proyecto
- [📝 Changelog](CHANGELOG.md) - Historial de versiones y cambios

---

## 🚀 Guía de Inicio Rápido

### Para Nuevos Usuarios

1. **¿Qué es BCS Millenial Broker?**
   - Sistema integral para gestión de seguros
   - Administra clientes, pólizas, aseguradoras y usuarios
   - Interfaz web moderna y fácil de usar

2. **Primeros Pasos**
   ```
   👤 Login → 🏠 Dashboard → 📋 Seleccionar Módulo → ✏️ Trabajar
   ```

3. **Funcionalidades Principales**
   - 👥 Gestión de usuarios y roles
   - 🏢 Administración de clientes  
   - 📄 Creación y gestión de pólizas
   - 🏦 Gestión de aseguradoras
   - 📊 Reportes y consultas

### Para Administradores

1. **Configuración Inicial**
   - [Instalar el sistema](docs/GUIA_INSTALACION.md#proceso-de-instalación)
   - [Crear usuario administrador](docs/GUIA_INSTALACION.md#configuración-de-usuario-inicial)
   - [Configurar roles y permisos](docs/MANUAL_USUARIO.md#gestión-de-roles)

2. **Gestión Diaria**
   - [Crear usuarios](docs/MANUAL_USUARIO.md#gestión-de-usuarios)
   - [Supervisar operaciones](docs/MANUAL_USUARIO.md#roles-y-accesos)
   - [Generar reportes](docs/MANUAL_USUARIO.md#reportes-y-consultas)

### Para Desarrolladores

1. **Configuración de Desarrollo**
   ```bash
   git clone [repo]
   cd Millenial_broker
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # o venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   streamlit run app1.py
   ```

2. **Estructura del Proyecto**
   ```
   📁 Millenial_broker/
   ├── 🐍 app1.py              # Aplicación principal
   ├── 📊 database_config.py   # Configuración BD
   ├── 📁 crud/                # Lógica de negocio
   ├── 📁 dashboards/          # Interfaces por rol
   └── 📁 docs/                # Documentación
   ```

---

## 📚 Documentación Detallada

### 📖 [Manual de Usuario](docs/MANUAL_USUARIO.md)
**Para todos los usuarios del sistema**

#### 🏠 Contenido Principal:
- **Navegación y uso general**
- **Guías por módulo (Usuarios, Clientes, Pólizas, etc.)**
- **Roles y permisos específicos**
- **Resolución de problemas comunes**

#### 👥 Dirigido a:
- ✅ Administradores
- ✅ Ejecutivos Comerciales  
- ✅ Personal de Back Office
- ✅ Usuarios finales

### 🛠️ [Guía de Instalación](docs/GUIA_INSTALACION.md)
**Para configurar el sistema desde cero**

#### 🔧 Contenido Principal:
- **Requisitos del sistema**
- **Instalación paso a paso**
- **Configuración inicial**
- **Resolución de problemas de instalación**

#### 👨‍💻 Dirigido a:
- ✅ Administradores de sistemas
- ✅ Desarrolladores
- ✅ Personal técnico

### 🔧 [Documentación Técnica](docs/DOCUMENTACION_TECNICA.md)
**Para desarrolladores y arquitectos**

#### 🏗️ Contenido Principal:
- **Arquitectura del sistema**
- **Diseño de base de datos**
- **APIs y servicios**
- **Patrones de diseño**
- **Guías de desarrollo**

#### 👨‍💻 Dirigido a:
- ✅ Desarrolladores
- ✅ Arquitectos de software
- ✅ Technical leads

### 🐳 [Guía de Deployment](docs/GUIA_DEPLOYMENT.md)
**Para despliegue en producción**

#### 🚀 Contenido Principal:
- **Configuración de entornos**
- **Docker y contenedores**
- **CI/CD y automatización**
- **Monitoreo y logs**
- **Backup y recovery**

#### 🔧 Dirigido a:
- ✅ DevOps engineers
- ✅ Administradores de sistemas
- ✅ SRE (Site Reliability Engineers)

---

## 📂 Estructura de la Documentación

```
📁 docs/
├── 📖 MANUAL_USUARIO.md          # Guía completa para usuarios
├── 🛠️ GUIA_INSTALACION.md       # Instalación y configuración
├── 🔧 DOCUMENTACION_TECNICA.md   # Especificaciones técnicas
├── 🐳 GUIA_DEPLOYMENT.md         # Despliegue en producción
├── 📷 screenshots/               # Capturas de pantalla
│   ├── dashboard-admin.png
│   ├── login-screen.png
│   └── poliza-creation.png
├── 📐 diagrams/                  # Diagramas técnicos
│   ├── architecture.svg
│   ├── database-erd.svg
│   └── user-flow.svg
└── 📄 templates/                 # Plantillas y ejemplos
    ├── docker-compose.example.yml
    ├── .env.example
    └── nginx.conf.example
```

---

## 🎯 Documentación por Audiencia

### 👤 Usuarios Finales

#### 📱 Uso Básico
1. [Cómo hacer login](docs/MANUAL_USUARIO.md#acceso-al-sistema)
2. [Navegación básica](docs/MANUAL_USUARIO.md#navegación-general)
3. [Crear clientes](docs/MANUAL_USUARIO.md#gestión-de-clientes)
4. [Gestionar pólizas](docs/MANUAL_USUARIO.md#gestión-de-pólizas)

#### ⚡ Acciones Rápidas
- [Buscar cliente existente](docs/MANUAL_USUARIO.md#consultar-usuarios)
- [Crear póliza nueva](docs/MANUAL_USUARIO.md#crear-póliza)
- [Generar reporte](docs/MANUAL_USUARIO.md#reportes-y-consultas)
- [Cerrar sesión segura](docs/MANUAL_USUARIO.md#navegación-general)

### 🔧 Administradores

#### 🏗️ Configuración
1. [Instalación inicial](docs/GUIA_INSTALACION.md#proceso-de-instalación)
2. [Crear usuarios](docs/MANUAL_USUARIO.md#crear-usuario)
3. [Configurar roles](docs/MANUAL_USUARIO.md#gestión-de-roles)
4. [Gestionar aseguradoras](docs/MANUAL_USUARIO.md#gestión-de-aseguradoras)

#### 📊 Operaciones
- [Supervisar usuarios](docs/MANUAL_USUARIO.md#consultar-usuarios)
- [Revisar pólizas](docs/MANUAL_USUARIO.md#consultar-pólizas)
- [Generar reportes](docs/MANUAL_USUARIO.md#reportes-y-consultas)
- [Configurar sistema](docs/GUIA_INSTALACION.md#configuración-avanzada)

### 👨‍💻 Desarrolladores

#### 🔨 Desarrollo
1. [Setup local](docs/GUIA_INSTALACION.md#instalación)
2. [Arquitectura](docs/DOCUMENTACION_TECNICA.md#arquitectura-del-sistema)
3. [Base de datos](docs/DOCUMENTACION_TECNICA.md#diseño-de-base-de-datos)
4. [APIs](docs/DOCUMENTACION_TECNICA.md#apis-y-servicios)

#### 🧪 Testing y Deploy
- [Tests unitarios](docs/DOCUMENTACION_TECNICA.md#testing-y-calidad)
- [Deploy local](docs/GUIA_DEPLOYMENT.md#desarrollo)
- [Deploy producción](docs/GUIA_DEPLOYMENT.md#producción)
- [Monitoring](docs/GUIA_DEPLOYMENT.md#monitoreo-y-logging)

---

## 🔍 Búsqueda Rápida

### 📋 Por Funcionalidad

| Quiero... | Ir a |
|-----------|------|
| **Instalar el sistema** | [Guía de Instalación](docs/GUIA_INSTALACION.md) |
| **Aprender a usar pólizas** | [Manual - Gestión de Pólizas](docs/MANUAL_USUARIO.md#gestión-de-pólizas) |
| **Entender la arquitectura** | [Documentación Técnica](docs/DOCUMENTACION_TECNICA.md#arquitectura-del-sistema) |
| **Desplegar en producción** | [Guía de Deployment](docs/GUIA_DEPLOYMENT.md) |
| **Resolver un problema** | [Manual - Solución de Problemas](docs/MANUAL_USUARIO.md#solución-de-problemas-comunes) |
| **Ver cambios recientes** | [Changelog](CHANGELOG.md) |

### 🏷️ Por Rol

| Soy... | Mi documentación |
|--------|------------------|
| **👤 Usuario nuevo** | [Manual de Usuario](docs/MANUAL_USUARIO.md) |
| **🔴 Administrador** | [Manual](docs/MANUAL_USUARIO.md) + [Instalación](docs/GUIA_INSTALACION.md) |
| **🟡 Ejecutivo Comercial** | [Manual - Ejecutivo](docs/MANUAL_USUARIO.md#ejecutivo-comercial) |
| **🟢 Back Office** | [Manual - Back Office](docs/MANUAL_USUARIO.md#back-office---operación) |
| **👨‍💻 Desarrollador** | [Documentación Técnica](docs/DOCUMENTACION_TECNICA.md) |
| **🚀 DevOps** | [Guía de Deployment](docs/GUIA_DEPLOYMENT.md) |

---

## 🆘 Soporte y Ayuda

### 📞 Contacto Inmediato
- **WhatsApp**: +593 99 351 3082
- **Consulta rápida**: [Mensaje directo](https://wa.me/5930993513082?text=Ayuda%20con%20BCS%20Millennial%20Broker)

### 📧 Soporte por Email
- **Técnico**: soporte@codecodix.com
- **Comercial**: ventas@codecodix.com
- **General**: info@codecodix.com

### ⏰ Horarios de Soporte
- **Lunes a Viernes**: 8:00 AM - 6:00 PM (GMT-5)
- **Emergencias**: 24/7 via WhatsApp
- **Fines de semana**: Solo emergencias críticas

### 🎫 Tipos de Soporte

| Tipo | Respuesta | Canal |
|------|-----------|-------|
| **🚨 Emergencia crítica** | < 1 hora | WhatsApp |
| **⚠️ Problema importante** | < 4 horas | Email/WhatsApp |
| **❓ Consulta general** | < 24 horas | Email |
| **💡 Nueva funcionalidad** | < 3 días | Email |

---

## 🔄 Actualizaciones de Documentación

### 📅 Cronograma de Revisión
- **Mensual**: Revisión de precisión y actualidad
- **Con cada release**: Actualización completa
- **Feedback usuarios**: Mejoras continuas

### 📝 Cómo Contribuir
1. **Reportar errores** en documentación
2. **Sugerir mejoras** o aclaraciones
3. **Solicitar ejemplos** adicionales
4. **Proponer nuevas secciones**

### 📊 Versiones de Documentación

| Versión Sistema | Versión Docs | Fecha | Estado |
|-----------------|--------------|-------|--------|
| **v1.0.0** | v1.0.0 | 2025-07-23 | ✅ Actual |
| v0.9.0 | v0.9.0 | 2025-07-15 | 📚 Archivo |
| v0.8.0 | v0.8.0 | 2025-07-08 | 📚 Archivo |

---

## 🏆 Mejores Prácticas de Documentación

### ✅ Para Contribuir
1. **Claridad**: Escribir para el usuario objetivo
2. **Ejemplos**: Incluir casos de uso reales  
3. **Capturas**: Usar imágenes cuando sea útil
4. **Actualidad**: Mantener sincronizado con el código
5. **Navegación**: Enlaces internos y externos útiles

### 📋 Checklist del Escritor
- [ ] ¿El título es descriptivo?
- [ ] ¿Hay ejemplos prácticos?
- [ ] ¿Los enlaces funcionan?
- [ ] ¿Es fácil de escanear?
- [ ] ¿Responde las preguntas comunes?

---

## 📈 Estadísticas de Documentación

### 📊 Métricas Actuales
- **📄 Páginas totales**: 5 documentos principales
- **📝 Palabras**: ~15,000 palabras
- **🖼️ Imágenes**: 12 diagramas y capturas
- **🔗 Enlaces**: 50+ enlaces internos
- **🌍 Idioma**: Español (ES)

### 🎯 Cobertura
- **✅ Instalación**: 100% completa
- **✅ Uso básico**: 100% completa  
- **✅ Administración**: 95% completa
- **✅ Desarrollo**: 90% completa
- **⚠️ API Reference**: 80% completa

---

**🎉 ¡Gracias por usar BCS Millenial Broker!**

*Esta documentación es un trabajo en progreso. Tu feedback nos ayuda a mejorarla continuamente.*

---

**Desarrollado con ❤️ por CodeCodix AI Lab**  
*Especialistas en Soluciones Empresariales Digitales*  
*WhatsApp: +593 99 351 3082*
