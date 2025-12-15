# 🔧 Troubleshooting Log - Valencia Traffic Platform

This document records technical issues encountered during development and deployment, along with their solutions, for future reference.

## 📅 2025-12-10/11: Initial VPS Deployment

### 1. Airflow Webserver "Unhealthy"
- **Symptom:** The `airflow-webserver` container remained in an `unhealthy` state, and the UI was inaccessible.
- **Cause:** The internal Airflow user (UID 50000) did not have permissions to write to the log directories mounted from the host.
- **Solution:**
  ```bash
  mkdir -p logs plugins dags data
  chmod -R 777 logs plugins dags data
  docker compose restart
  ```

### 2. DockerOperator: "Permission denied" to socket
- **Symptom:** The DAG task failed with `PermissionError(13, 'Permission denied')` when attempting to connect to `unix://var/run/docker.sock`.
- **Cause:** The Airflow user inside the container did not have permissions to access the host's Docker socket.
- **Solution:** Grant permissions to the socket on the VPS.
  ```bash
  sudo chmod 666 /var/run/docker.sock
  ```

### 3. DockerOperator: "Invalid JSON" / Mount Error
- **Symptom:** Error `400 Client Error: Bad Request ("invalid JSON...")` or `invalid mount config`.
- **Cause:**
  1. The new version of the Docker Python library requires `Mount` objects instead of simple strings (`"source:target"`).
  2. The `source` path of the mount must be **absolute on the Host**, not relative or inside the Airflow container.
- **Solution:**
  - Update the DAG to use `docker.types.Mount`.
  - Use the absolute VPS path: `/root/valencia_traffic_platform/data`.
  ```python
  from docker.types import Mount
  # ...
  mounts=[
      Mount(source='/root/valencia_traffic_platform/data', target='/app/data', type='bind')
  ]
  ```

### 4. Incorrect Folder Structure
- **Symptom:** Cloning the repo created a nested subfolder `/root/valencia_traffic_platform/valencia_traffic_platform`, breaking relative paths in `docker-compose.yml`.
- **Solution:** Move everything to the top level or re-clone in the correct path.

---
## 🛡️ Security Notes
- **Web Access:** Port 8080 was restricted to `127.0.0.1` to force the use of an SSH Tunnel (`ssh -L 8080:localhost:8080 ...`) and avoid insecure public exposure.
- **Secrets:** The `.env` file was excluded from git and created manually on the server.

---
---

# 🔧 Registro de Problemas (Troubleshooting Log)

Este documento registra los problemas técnicos encontrados durante el desarrollo y despliegue, junto con sus soluciones, para futura referencia.

## 📅 2025-12-10/11: Despliegue Inicial en VPS

### 1. Airflow Webserver "Unhealthy"
- **Síntoma:** El contenedor `airflow-webserver` se quedaba en estado `unhealthy` y no se podía acceder a la UI.
- **Causa:** El usuario interno de Airflow (UID 50000) no tenía permisos para escribir en las carpetas de logs montadas desde el host.
- **Solución:**
  ```bash
  mkdir -p logs plugins dags data
  chmod -R 777 logs plugins dags data
  docker compose restart
  ```

### 2. DockerOperator: "Permission denied" al socket
- **Síntoma:** La tarea del DAG fallaba con `PermissionError(13, 'Permission denied')` al intentar conectar a `unix://var/run/docker.sock`.
- **Causa:** El usuario de Airflow dentro del contenedor no tenía permisos para acceder al socket de Docker del host.
- **Solución:** Dar permisos al socket en el VPS.
  ```bash
  sudo chmod 666 /var/run/docker.sock
  ```

### 3. DockerOperator: "Invalid JSON" / Mount Error
- **Síntoma:** Error `400 Client Error: Bad Request ("invalid JSON...")` o `invalid mount config`.
- **Causa:**
  1. La versión nueva de la librería Docker en Python exige objetos `Mount` en lugar de strings simples (`"source:target"`).
  2. La ruta `source` del montaje debe ser **absoluta en el Host**, no relativa ni dentro del contenedor de Airflow.
- **Solución:**
  - Actualizar el DAG para usar `docker.types.Mount`.
  - Usar la ruta absoluta del VPS: `/root/valencia_traffic_platform/data`.
  ```python
  from docker.types import Mount
  # ...
  mounts=[
      Mount(source='/root/valencia_traffic_platform/data', target='/app/data', type='bind')
  ]
  ```

### 4. Estructura de Carpetas Incorrecta
- **Síntoma:** Al clonar el repo, se creó una subcarpeta anidada `/root/valencia_traffic_platform/valencia_traffic_platform`, rompiendo las rutas relativas de `docker-compose.yml`.
- **Solución:** Mover todo al nivel superior o volver a clonar en la ruta correcta.

---
## 🛡️ Notas de Seguridad
- **Acceso Web:** Se restringió el puerto 8080 a `127.0.0.1` para obligar el uso de Túnel SSH (`ssh -L 8080:localhost:8080 ...`) y evitar exposición pública insegura.
- **Secretos:** El archivo `.env` se excluyó de git y se creó manualmente en el servidor.

### 5. Internal Server Error (AttributeError: 'NoneType'...)
- **Symptom:** After deleting the `airflow` user, accessing the web UI returns `500 Internal Server Error`.
  - Log: `AttributeError: 'NoneType' object has no attribute 'is_active'`
- **Cause:** The browser still has a session cookie for the deleted user ID. The webserver tries to load the user from the DB, finds nothing (`None`), and crashes when checking `is_active`.
- **Solution:**
  1.  **Clear browser cookies** or open an **Incognito/Private** window.
  2.  Ensure the new user is created: `docker compose up airflow-init`.

## 📅 2025-12-15: Configuración de Despliegue Automático y Nginx

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
