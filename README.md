# Sistema de Monitoreo del Plan de Descontaminación

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1%2B-green)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-blue)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sistema de gestión y monitoreo para el Plan de Descontaminación de Concón, Quinteros y Puchuncaví, permitiendo el seguimiento del avance de medidas por los diferentes organismos participantes y ofreciendo transparencia a la ciudadanía.

## 🚀 Características

- ✅ **Multi-usuario y multi-rol**: Superadmin, Admin SMA, Organismos y Ciudadanos
- 📊 **Dashboards interactivos** con visualización del avance global y por componente
- 📝 **Gestión de medidas** organizadas por componentes temáticos
- 📋 **Registro de avances** por cada organismo responsable
- 📈 **Generación de reportes** en múltiples formatos (web, PDF)
- 🔑 **Sistema de permisos** basado en roles
- 🔍 **Auditoría** de todas las acciones realizadas en el sistema
- 🌐 **API REST** completa con documentación Swagger/OpenAPI
- 🖥️ **Portal público** para transparencia ciudadana

## 📋 Requisitos

- Python 3.10+
- PostgreSQL 13+
- Pip y Virtualenv

## 🛠️ Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/your-username/sma_monitor.git
cd sma_monitor
```

### 2. Crear y activar entorno virtual

```bash
python -m venv .venv

# En Windows
.venv\Scripts\activate

# En macOS/Linux
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos PostgreSQL


````bash
# Crear la base de datos
createdb plan_descontaminacion

# Configurar credenciales en .env

Crear un archivo llamado `.env` en la raíz del proyecto con el siguiente contenido:

DB_NAME=plan_descontaminacion
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432

Reemplazar los valores con tus credenciales.
=======
```bash
# Crear la base de datos
createdb plan_descontaminacion

# Configurar credenciales en .env (si archivo .env - env no existe, crearlo en la raíz del directorio)
cp .env.example .env
# Editar .env con tus credenciales
```

### 5. Aplicar migraciones

```bash
python manage.py migrate
````

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

### 7. Iniciar el servidor

```bash
python manage.py runserver
```

La aplicación estará disponible en 
- [http://127.0.0.1:8000/](http://127.0.0.1:8000/) -> Para acceder al front
- [http://127.0.0.1:8000/api/v1/](http://127.0.0.1:8000/api/v1/) -> Acceder a la interfaz de DRF(API)
- [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/asmin/) -> Para acceder al DRF Admin
- [http://127.0.0.1:8000/api/v1/swagger/](http://127.0.0.1:8000/api/v1/swagger/) -> Para acceder a la API mediante Swagger

## 🏗️ Estructura del Proyecto

```
sma_monitor/
├── apps/
│   ├── api/                # API REST
│   ├── auditorias/         # Sistema de auditoría
│   ├── medidas/            # Gestión de medidas y avances
│   ├── organismos/         # Gestión de organismos
│   ├── publico/            # Portal público
│   ├── reportes/           # Generación de reportes
│   └── usuarios/           # Autenticación y perfiles
├── ppda_core/              # Configuración principal
├── templates/              # Plantillas HTML
├── static/                 # Archivos estáticos
├── media/                  # Archivos subidos por usuarios
├── requirements.txt        # Dependencias
└── manage.py               # Script de gestión de Django
```

## 🧩 Modelos Principales

### Organismos

- **TipoOrganismo**: Categorías de organismos participantes
- **Organismo**: Entidades responsables de implementar medidas
- **ContactoOrganismo**: Personas de contacto de cada organismo

### Medidas

- **Componente**: Áreas temáticas del plan de descontaminación
- **Medida**: Acciones específicas del plan
- **AsignacionMedida**: Relación entre medidas y organismos responsables
- **RegistroAvance**: Seguimiento del avance de cada medida

### Usuarios

- **Usuario**: Extensión del modelo User de Django con roles específicos
- **Perfil**: Información adicional del usuario

### Reportes

- **TipoReporte**: Definición de reportes disponibles
- **ReporteGenerado**: Instancias de reportes generados

## 📊 API REST

La API del sistema permite la integración con otras aplicaciones y el consumo de datos desde el frontend.

### Documentación

- Swagger UI: `/api/swagger/`
- ReDoc: `/api/redoc/`
- Esquema OpenAPI: `/api/schema/`

### Endpoints principales

- `/api/organismos/`: Gestión de organismos
- `/api/medidas/`: Administración de medidas
- `/api/registros-avance/`: Registro de avances
- `/api/componentes/`: Componentes del plan
- `/api/dashboard/`: Datos resumidos para visualización

## 👥 Perfiles de Usuario

### Superadmin

- Acceso completo al sistema
- Configuración técnica
- Gestión de usuarios y permisos

### Admin SMA

- Gestión de medidas y componentes
- Seguimiento de avances
- Validación de datos

### Organismos

- Registro de avances en medidas asignadas
- Visualización de sus medidas y plazos
- Consulta de reportes específicos

### Ciudadanos

- Visualización del avance general del plan
- Consulta de información pública

## 📚 Historias de Usuario

Puedes revisar el tablero Kanban del proyecto con todas las historias de usuario y su estado actual:

🔗 [Ver Tablero en Taiga](https://tree.taiga.io/project/natalitarivera-curso-python-grupo-5/kanban)

## 🧪 Testing

Para ejecutar las pruebas:

```bash
# Ejecutar todas las pruebas
python manage.py test

# Ejecutar pruebas específicas
python manage.py test apps.medidas
```

## 🚀 Despliegue

### Preparación

```bash
# Recolectar archivos estáticos
python manage.py collectstatic

# Verificar configuración
python manage.py check --deploy
```

### Configuración de Producción

En producción, asegúrese de configurar correctamente:

1. Valores `DEBUG = False` y `SECRET_KEY` segura
2. Configuración HTTPS con certificado SSL
3. Servidor web (Nginx/Apache) y WSGI (Gunicorn/uWSGI)
4. Base de datos PostgreSQL optimizada
5. Cache (Redis/Memcached)
6. Firewall y medidas de seguridad

## 📝 Contribución

1. Haz un fork del proyecto
2. Crea una rama para tu característica (`git checkout -b feature/nueva-caracteristica`)
3. Haz commit de tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Empuja a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 📧 Contacto

Para soporte o consultas: [grupo5@chinorios.com](mailto:jesushippie@chinorios.com)

---

Desarrollado por [Grupo 5](https://grupo-5.com) © 2025
