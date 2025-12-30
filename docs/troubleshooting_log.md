# 🔧 Registro de Problemas (Troubleshooting Log) - Valencia Traffic Platform

Este documento registra los problemas técnicos encontrados durante el desarrollo y despliegue, junto con sus soluciones, para futura referencia.

## 📅 2025-12-20: Calidad de Datos y Hardening de Despliegue

### 12. "Stale Docker Image" (Código nuevo, Comportamiento viejo)
- **Síntoma:** Tras actualizar el código de ingestión (`git pull`) para arreglar la paginación, el DAG seguía trayendo solo 100 registros.
- **Causa:** `DockerOperator` ejecutaba la imagen antigua (`valencia-traffic-ingestion:latest`) porque `docker compose build` usaba la caché de capas anteriores, ignorando los cambios en los archivos copiados (`COPY src/ ./src/`).
- **Solución:** Forzar el rebuild sin caché en el pipeline de despliegue (`deploy.yml`).
  ```yaml
  docker compose build --no-cache
  ```

### 11. Duplicados en API Paginada (Inestabilidad del Orden)
- **Síntoma:** Se obtenían 400 registros (paginados), pero 22 eran duplicados del primer lote, faltando 22 reales.
- **Causa:** La API de OpenDataSoft (live) cambia el orden de los registros mientras se pagina, provocando que registros de la página 1 aparezcan de nuevo en la página 2.
- **Solución:** Implementar lógica de deduplicación en `ingest_traffic.py` usando el identificador único `idtramo` antes de guardar el JSON.

### 10. Jupyter Data Path vs. Airflow Path
- **Síntoma:** El notebook no encontraba datos en `../data/raw`.
- **Causa:** Confusión entre la migración de datos manual y la automática. Había una carpeta `/opt/.../data/2025` (antigua) y `/opt/.../data/raw/2025` (nueva).
- **Solución:** Unificar directorios y asegurar permisos recursivos.
  ```bash
  sudo rsync -av data/2025/ data/raw/2025/
  sudo chown -R 50000:0 data
  ```

## 📅 2025-12-19: Migración a /opt y Configuración Dinámica

### 9. Jupyter "Permission Denied" al guardar notebooks
- **Síntoma:** Error `Permission denied: work/notebooks/01_inspection.ipynb` al intentar guardar desde Jupyter Lab.
- **Causa:** La carpeta `notebooks/` en el host pertenecía a `root` (UID 0), mientras que el contenedor de Jupyter se ejecuta típicamente con un usuario no root (ej. UID 50000 o 1000).
- **Solución (Best Practice):** Asignar la propiedad de la carpeta al usuario de Airflow/Jupyter (UID 50000).
  ```bash
  sudo chown -R 50000:0 /opt/valencia_traffic_platform/notebooks
  ```

### 8. Docker Compose "Variable not set"
- **Síntoma:** Advertencia `WARN[0000] The "VALENCIA_TRAFFIC_API_URL" variable is not set. Defaulting to a blank string`.
- **Causa:** `docker-compose.yml` esperaba una variable de entorno que no existía en el host de desarrollo (Windows) ni en el `.env` inicial.
- **Solución:** Usar sintaxis de fallback en `docker-compose.yml`: `${VALENCIA_TRAFFIC_API_URL:-}` para silenciar el aviso si no es crítica.

## 📅 2025-12-15: Configuración de Despliegue Automático y Nginx

### 7. Airflow "Connection Reset" / "Starting" Loop
- **Síntoma:** Después del despliegue, Airflow no arrancaba y los logs mostraban `ValueError: Unable to configure handler 'processor'`.
- **Causa:** Al desplegar código nuevo, los permisos de las carpetas `logs`, `dags` y `plugins` en el host no pertenecían al usuario interno de Airflow (UID 50000), impidiendo la escritura de logs.
- **Solución:** Restaurar permisos en el VPS.
  ```bash
  cd /opt/valencia_traffic_platform
  sudo chown -R 50000:0 logs dags plugins
  sudo chmod -R 775 logs dags plugins
  docker compose restart
  ```

### 6. Nginx 502 Bad Gateway / Connection Refused (IPv6 vs IPv4)
- **Síntoma:** Al acceder a `airflow.rodrigoguardamagna.com` o `n8n.rodrigoguardamagna.com`, Nginx devolvía error 502.
- **Log de Error:** `connect() failed (111: Connection refused) ... upstream: "http://[::1]:8080/..."`
- **Causa:** Nginx intentaba conectar al upstream (Airflow/n8n) usando **IPv6** (`[::1]`) porque `localhost` resolvía a esa dirección, pero los servicios Docker solo escuchaban en **IPv4** (`127.0.0.1`).
- **Solución:** Forzar el uso de IPv4 en la configuración de Nginx (`proxy_pass`).
  ```nginx
  # Antes (Incorrecto)
  proxy_pass http://localhost:8080;
  
  # Después (Correcto)
  proxy_pass http://127.0.0.1:8080;
  ```

## 📅 2025-12-10/11: Despliegue Inicial en VPS

### 5. Internal Server Error (AttributeError: 'NoneType'...)
- **Síntoma:** Tras borrar el usuario `airflow` y recrearlo, la UI devuelve `500 Internal Server Error`.
- **Causa:** El navegador guarda una cookie de sesión del usuario antiguo. El webserver intenta cargar ese usuario, no lo encuentra (`None`) y falla.
- **Solución:** Borrar cookies o usar modo incógnito.

### 4. Estructura de Carpetas Incorrecta
- **Síntoma:** Al clonar el repo, se creó una subcarpeta anidada `/root/valencia_traffic_platform/valencia_traffic_platform`, rompiendo las rutas relativas de `docker-compose.yml`.
- **Solución:** Mover todo al nivel superior o volver a clonar en la ruta correcta.

### 3. DockerOperator: "Invalid JSON" / Mount Error
- **Síntoma:** Error `400 Client Error: Bad Request ("invalid JSON...")` o `invalid mount config`.
- **Causa:**
  1. La versión nueva de la librería Docker en Python exige objetos `Mount` en lugar de strings simples (`"source:target"`).
  2. La ruta `source` del montaje debe ser **absoluta en el Host**, no relativa ni dentro del contenedor de Airflow.
- **Solución:**
  - Actualizar el DAG para usar `docker.types.Mount`.
  - Usar la ruta absoluta del VPS (ahora gestionada vía Variable).
  ```python
  from docker.types import Mount
  # ...
  mounts=[
      Mount(source=PROJECT_DATA_PATH, target='/app/data', type='bind')
  ]
  ```

### 2. DockerOperator: "Permission denied" al socket
- **Síntoma:** La tarea del DAG fallaba con `PermissionError(13, 'Permission denied')` al intentar conectar a `unix://var/run/docker.sock`.
- **Causa:** El usuario de Airflow dentro del contenedor no tenía permisos para acceder al socket de Docker del host.
- **Solución:** Dar permisos al socket en el VPS.
  ```bash
  sudo chmod 666 /var/run/docker.sock
  ```

### 1. Airflow Webserver "Unhealthy"
- **Síntoma:** El contenedor `airflow-webserver` se quedaba en estado `unhealthy` y no se podía acceder a la UI.
- **Causa:** El usuario interno de Airflow (UID 50000) no tenía permisos para escribir en las carpetas de logs montadas desde el host.
- **Solución:**
  ```bash
  mkdir -p logs plugins dags data
  chmod -R 777 logs plugins dags data
  docker compose restart
  ```

---
## 📅 2025-12-29: Integración de Machine Learning ("The Oracle")

### 13. Fatal Error in Launcher (Path Corruption)
- **Síntoma:** Error `Fatal error in launcher: Unable to create process...` al ejecutar `pip` o `python`.
- **Causa:** El entorno virtual original (`envdata`) contenía rutas absolutas que se rompieron al mover el proyecto o renombrar carpetas superiores (`/proyects/`). Los ejecutables de Python/Pip en Windows tienen la ruta hardcodeada en el `.exe`.
- **Solución:** Abandonar el entorno global y crear un entorno virtual local dedicado por proyecto.
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

---
## 🛡️ Notas de Seguridad
- **Acceso Web:** Se restringió el puerto 8080 a `127.0.0.1` para obligar el uso de Túnel SSH (`ssh -L 8080:localhost:8080 ...`) y evitar exposición pública insegura.
- **Secretos:** El archivo `.env` se excluyó de git y se gestiona manualmente en el servidor.
