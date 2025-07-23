# 🚀 Guía de Deployment - BCS Millenial Broker

## 📋 Resumen de Deployment

Esta guía cubre el proceso completo de despliegue del sistema BCS Millenial Broker en diferentes entornos: desarrollo, testing, staging y producción.

## 🏗️ Entornos de Deployment

### 1. 🛠️ Desarrollo (Development)
- **Propósito**: Desarrollo activo y pruebas unitarias
- **Base de datos**: SQLite local
- **Servidor**: Streamlit development server
- **URL**: `http://localhost:8501`
- **Características**: Hot reload, debug mode activo

### 2. 🧪 Testing/QA
- **Propósito**: Pruebas de integración y QA
- **Base de datos**: SQLite o PostgreSQL dedicada
- **Servidor**: Streamlit con configuración de testing
- **URL**: `http://testing.millennial-broker.local`
- **Características**: Datos de prueba, logging detallado

### 3. 🎭 Staging
- **Propósito**: Ambiente pre-producción
- **Base de datos**: PostgreSQL (réplica de producción)
- **Servidor**: Docker container
- **URL**: `http://staging.millennial-broker.com`
- **Características**: Configuración idéntica a producción

### 4. 🏭 Producción
- **Propósito**: Sistema en vivo para usuarios finales
- **Base de datos**: PostgreSQL con respaldos automáticos
- **Servidor**: Docker + Nginx + SSL
- **URL**: `https://app.millennial-broker.com`
- **Características**: Alta disponibilidad, monitoreo 24/7

## 🐳 Deployment con Docker

### Dockerfile

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear usuario no-root para seguridad
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 8501

# Configurar healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando de inicio
CMD ["streamlit", "run", "app1.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Docker Compose para Desarrollo

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - .:/app
      - /app/__pycache__
    environment:
      - DEBUG=True
      - SECRET_KEY=dev-secret-key-change-in-production
      - DATABASE_URL=sqlite:///database.db
    command: ["streamlit", "run", "app1.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.runOnSave=true"]
    
  db:
    image: postgres:13
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=millennial_broker_dev
      - POSTGRES_USER=dev_user
      - POSTGRES_PASSWORD=dev_password
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data

volumes:
  postgres_dev_data:
```

### Docker Compose para Producción

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build: .
    restart: unless-stopped
    environment:
      - DEBUG=False
      - SECRET_KEY_FILE=/run/secrets/secret_key
      - DATABASE_URL=postgresql://prod_user:prod_password@db:5432/millennial_broker
    secrets:
      - secret_key
    depends_on:
      - db
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped
    networks:
      - app-network

  db:
    image: postgres:13
    restart: unless-stopped
    environment:
      - POSTGRES_DB=millennial_broker
      - POSTGRES_USER=prod_user
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_prod_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - app-network

  backup:
    image: postgres:13
    depends_on:
      - db
    volumes:
      - ./backups:/backups
    environment:
      - POSTGRES_DB=millennial_broker
      - POSTGRES_USER=prod_user
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    entrypoint: |
      bash -c 'bash -s <<EOF
      trap "break;exit" SIGHUP SIGINT SIGTERM
      sleep 30m
      while /bin/true; do
        pg_dump -h db -U prod_user millennial_broker | gzip > /backups/backup_$(date +"%Y%m%d_%H%M%S").sql.gz
        find /backups -name "backup_*.sql.gz" -mtime +7 -exec rm {} \;
        sleep 24h
      done
      EOF'
    networks:
      - app-network

secrets:
  secret_key:
    file: ./secrets/secret_key.txt
  db_password:
    file: ./secrets/db_password.txt

volumes:
  postgres_prod_data:

networks:
  app-network:
    driver: bridge
```

## 🌐 Configuración de Nginx

### nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    upstream app {
        server app:8501;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;

    server {
        listen 80;
        server_name app.millennial-broker.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name app.millennial-broker.com;

        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;

        # Security Headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Compression
        gzip on;
        gzip_vary on;
        gzip_comp_level 6;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

        # File upload limits
        client_max_body_size 100M;

        location / {
            # Rate limiting for login
            location /login {
                limit_req zone=login burst=10 nodelay;
                proxy_pass http://app;
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Proto $scheme;
            }

            # General rate limiting
            limit_req zone=api burst=50 nodelay;

            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            # WebSocket support for Streamlit
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 86400;
        }

        # Static files caching
        location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

## 🔐 Configuración de Seguridad

### Secrets Management

```bash
# Generar secrets para producción
mkdir -p secrets

# Secret key para JWT
openssl rand -base64 32 > secrets/secret_key.txt

# Database password
openssl rand -base64 24 > secrets/db_password.txt

# Configurar permisos
chmod 600 secrets/*
```

### Variables de Entorno

```bash
# .env.production
DEBUG=False
SECRET_KEY_FILE=/run/secrets/secret_key
DATABASE_URL=postgresql://prod_user:prod_password@db:5432/millennial_broker
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=False
```

### SSL/TLS Configuration

```bash
# Generar certificados SSL (para testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=EC/ST=Pichincha/L=Quito/O=Millennial Broker/CN=app.millennial-broker.com"

# Para producción, usar Let's Encrypt
certbot certonly --webroot -w /var/www/html -d app.millennial-broker.com
```

## 🚀 Proceso de Deployment

### 1. Pre-Deployment Checklist

```bash
#!/bin/bash
# pre-deploy-check.sh

echo "🔍 Verificando prerequisitos..."

# Verificar que Docker está ejecutándose
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker no está ejecutándose"
    exit 1
fi

# Verificar que existen los archivos necesarios
required_files=("Dockerfile" "docker-compose.prod.yml" "requirements.txt" "app1.py")
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Archivo faltante: $file"
        exit 1
    fi
done

# Verificar secrets
if [[ ! -f "secrets/secret_key.txt" ]] || [[ ! -f "secrets/db_password.txt" ]]; then
    echo "❌ Secrets faltantes en directorio secrets/"
    exit 1
fi

# Verificar sintaxis Python
python -m py_compile app1.py
if [[ $? -ne 0 ]]; then
    echo "❌ Error de sintaxis en app1.py"
    exit 1
fi

echo "✅ Verificaciones completadas"
```

### 2. Build y Deploy Script

```bash
#!/bin/bash
# deploy.sh

set -e  # Exit on any error

ENVIRONMENT=${1:-production}
VERSION=$(git rev-parse --short HEAD)

echo "🚀 Iniciando deployment para ambiente: $ENVIRONMENT"
echo "📦 Versión: $VERSION"

# Función para cleanup en caso de error
cleanup() {
    echo "🧹 Limpiando recursos en caso de error..."
    docker-compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true
}
trap cleanup ERR

# Pre-deployment checks
./scripts/pre-deploy-check.sh

# Construir imagen
echo "🔨 Construyendo imagen Docker..."
docker build -t millennial-broker:$VERSION .
docker tag millennial-broker:$VERSION millennial-broker:latest

# Hacer backup de la base de datos actual (solo en producción)
if [[ "$ENVIRONMENT" == "production" ]]; then
    echo "💾 Creando backup de base de datos..."
    docker-compose -f docker-compose.prod.yml exec -T db \
        pg_dump -U prod_user millennial_broker | \
        gzip > "backups/pre-deploy-backup-$(date +%Y%m%d_%H%M%S).sql.gz"
fi

# Detener servicios existentes
echo "⏹️ Deteniendo servicios existentes..."
docker-compose -f docker-compose.prod.yml down

# Iniciar nuevos servicios
echo "▶️ Iniciando servicios..."
docker-compose -f docker-compose.prod.yml up -d

# Verificar que los servicios están saludables
echo "🏥 Verificando salud de servicios..."
sleep 30

for i in {1..10}; do
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up (healthy)"; then
        echo "✅ Servicios saludables"
        break
    fi
    if [[ $i -eq 10 ]]; then
        echo "❌ Servicios no respondieron a tiempo"
        docker-compose -f docker-compose.prod.yml logs
        exit 1
    fi
    echo "⏳ Esperando servicios... ($i/10)"
    sleep 10
done

# Verificar conectividad
echo "🌐 Verificando conectividad..."
if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "✅ Aplicación respondiendo correctamente"
else
    echo "❌ Aplicación no responde"
    docker-compose -f docker-compose.prod.yml logs app
    exit 1
fi

echo "🎉 Deployment completado exitosamente!"
echo "📊 Estado de servicios:"
docker-compose -f docker-compose.prod.yml ps
```

### 3. Health Checks y Monitoring

```bash
#!/bin/bash
# health-check.sh

echo "🏥 Verificando salud del sistema..."

# Check application health
if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "✅ Aplicación: OK"
else
    echo "❌ Aplicación: FAIL"
    exit 1
fi

# Check database connection
if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U prod_user > /dev/null 2>&1; then
    echo "✅ Base de datos: OK"
else
    echo "❌ Base de datos: FAIL"
    exit 1
fi

# Check disk space
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [[ $DISK_USAGE -lt 80 ]]; then
    echo "✅ Espacio en disco: $DISK_USAGE% usado"
else
    echo "⚠️ Espacio en disco: $DISK_USAGE% usado (crítico)"
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
if [[ $MEMORY_USAGE -lt 80 ]]; then
    echo "✅ Uso de memoria: $MEMORY_USAGE%"
else
    echo "⚠️ Uso de memoria: $MEMORY_USAGE% (alto)"
fi

echo "🎯 Sistema operativo correctamente"
```

## 📊 Monitoreo y Logging

### Configuración de Logging

```python
# logging_config.py
import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    """Configurar logging para producción"""
    
    # Crear directorio de logs si no existe
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO if not os.getenv('DEBUG') else logging.DEBUG)
    
    # Handler para archivo con rotación
    file_handler = logging.handlers.RotatingFileHandler(
        f"{log_dir}/millennial_broker.log",
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler específico para errores
    error_handler = logging.handlers.RotatingFileHandler(
        f"{log_dir}/errors.log",
        maxBytes=5*1024*1024,  # 5 MB
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger
```

### Docker Logging Configuration

```yaml
# Agregar a docker-compose.prod.yml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    
  nginx:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 🔄 Backup y Recovery

### Script de Backup Automático

```bash
#!/bin/bash
# backup.sh

set -e

BACKUP_DIR="/backups"
DATE=$(date +"%Y%m%d_%H%M%S")
RETENTION_DAYS=30

echo "💾 Iniciando backup: $DATE"

# Crear backup de base de datos
docker-compose -f docker-compose.prod.yml exec -T db \
    pg_dump -U prod_user millennial_broker | \
    gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Crear backup de archivos de aplicación
tar -czf "$BACKUP_DIR/app_backup_$DATE.tar.gz" \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='logs/*' \
    .

# Limpiar backups antiguos
find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "app_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "✅ Backup completado: $DATE"
echo "📁 Archivos de backup:"
ls -lh "$BACKUP_DIR"/*$DATE*
```

### Script de Recovery

```bash
#!/bin/bash
# recovery.sh

BACKUP_FILE=$1

if [[ -z "$BACKUP_FILE" ]]; then
    echo "❌ Uso: $0 <archivo_backup.sql.gz>"
    echo "📁 Backups disponibles:"
    ls -lt /backups/db_backup_*.sql.gz | head -10
    exit 1
fi

echo "⚠️ ADVERTENCIA: Esto reemplazará la base de datos actual"
read -p "¿Continuar? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Operación cancelada"
    exit 1
fi

echo "🔄 Restaurando base de datos desde: $BACKUP_FILE"

# Detener aplicación
docker-compose -f docker-compose.prod.yml stop app

# Restaurar base de datos
zcat "$BACKUP_FILE" | docker-compose -f docker-compose.prod.yml exec -T db \
    psql -U prod_user -d millennial_broker

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml start app

echo "✅ Recovery completado"
```

## 📈 Escalabilidad y Alta Disponibilidad

### Load Balancer Configuration

```yaml
# docker-compose.ha.yml - Para alta disponibilidad
version: '3.8'

services:
  app1:
    build: .
    environment:
      - NODE_ID=1
    networks:
      - app-network

  app2:
    build: .
    environment:
      - NODE_ID=2
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-ha.conf:/etc/nginx/nginx.conf
    depends_on:
      - app1
      - app2
    networks:
      - app-network

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=millennial_broker
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - app-network

  redis:
    image: redis:alpine
    networks:
      - app-network
```

### Nginx HA Configuration

```nginx
# nginx-ha.conf
upstream app_servers {
    least_conn;
    server app1:8501 max_fails=3 fail_timeout=30s;
    server app2:8501 max_fails=3 fail_timeout=30s;
}

server {
    listen 80;
    
    location / {
        proxy_pass http://app_servers;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Health check
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }
}
```

## 🔧 Troubleshooting Deployment

### Problemas Comunes y Soluciones

#### 1. **Contenedor no inicia**
```bash
# Verificar logs
docker-compose -f docker-compose.prod.yml logs app

# Verificar configuración
docker-compose -f docker-compose.prod.yml config

# Ejecutar en modo interactivo para debug
docker run -it --rm millennial-broker:latest /bin/bash
```

#### 2. **Base de datos no conecta**
```bash
# Verificar estado de PostgreSQL
docker-compose -f docker-compose.prod.yml exec db pg_isready

# Verificar logs de BD
docker-compose -f docker-compose.prod.yml logs db

# Conectar manualmente para pruebas
docker-compose -f docker-compose.prod.yml exec db psql -U prod_user millennial_broker
```

#### 3. **SSL/TLS issues**
```bash
# Verificar certificados
openssl x509 -in ssl/cert.pem -text -noout

# Test SSL connection
openssl s_client -connect app.millennial-broker.com:443
```

#### 4. **Performance issues**
```bash
# Monitorear recursos
docker stats

# Verificar logs de Nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Verificar métricas de aplicación
curl http://localhost:8501/_stcore/metrics
```

### Recovery Procedures

#### Emergency Rollback
```bash
#!/bin/bash
# emergency-rollback.sh

echo "🚨 Iniciando rollback de emergencia..."

# Detener servicios actuales
docker-compose -f docker-compose.prod.yml down

# Restaurar imagen anterior
docker tag millennial-broker:previous millennial-broker:latest

# Restaurar base de datos
LATEST_BACKUP=$(ls -t /backups/db_backup_*.sql.gz | head -1)
./scripts/recovery.sh "$LATEST_BACKUP"

# Reiniciar servicios
docker-compose -f docker-compose.prod.yml up -d

echo "✅ Rollback completado"
```

## 📞 Soporte de Deployment

### Contacto Técnico
- **WhatsApp**: +593 99 351 3082
- **Email**: devops@codecodix.com
- **Emergencias 24/7**: [WhatsApp directo](https://wa.me/5930993513082?text=Emergencia%20deployment%20BCS%20Millennial%20Broker)

### Escalación de Incidentes
1. **Severidad 1** (Sistema caído): Contacto inmediato
2. **Severidad 2** (Funcionalidad crítica afectada): < 2 horas
3. **Severidad 3** (Problemas menores): < 24 horas
4. **Severidad 4** (Mejoras): Próximo ciclo de desarrollo

---

**Desarrollado por CodeCodix AI Lab**  
*Especialistas en DevOps y Deployment de Aplicaciones Empresariales*
