# 🚀 Guía de Despliegue (Deployment Setup)

Esta guía detalla el proceso para desplegar la plataforma en el VPS y cómo configurar la automatización con GitHub Actions.

## 1. Configuración del VPS (Hetzner)

### Requisitos Previos
- Servidor Ubuntu 24.04 (o superior).
- Docker y Docker Compose instalados.
- Puerto 8080 cerrado (Firewall) para evitar acceso público no autorizado.

### Estructura de Directorios
El proyecto se despliega en `/opt/valencia_traffic_platform`.
1.  **Crear directorio:** `sudo mkdir -p /opt/valencia_traffic_platform`
2.  **Permisos:** Asegúrate de que tu usuario (o el usuario de despliegue) tenga permisos de escritura: `sudo chown -R $USER:$USER /opt/valencia_traffic_platform`

### Variables de Entorno (.env)
En el servidor, crea el archivo `/opt/valencia_traffic_platform/.env`. Este archivo **no se sube a Git** y contiene secretos y config específica del entorno.

```bash
# ID de usuario para Airflow (IMPORTANTE: debe coincidir con el usuario del host)
AIRFLOW_UID=1000  # Ejecuta 'id -u' en el servidor para saber tu ID

# Configuración de Airflow
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=tu_contraseña_segura_aqui

# Configuración opcional
VALENCIA_TRAFFIC_API_URL=https://valencia.opendatasoft.com/api/explore/v2.1/catalog/datasets/estat-transit-temps-real-estado-trafico-tiempo-real/records
```

## 2. Automatización con GitHub Actions

El archivo `.github/workflows/deploy.yml` gestiona el despliegue automático al hacer push a `main`.

### Secretos Necesarios (GitHub Repo Settings -> Secrets)
- `VPS_HOST`: IP del servidor (ej. `x.x.x.x`)
- `VPS_USERNAME`: Usuario SSH (ej. `deploy_user`)
- `VPS_SSH_KEY`: Clave privada SSH (generada específicamente para GitHub Actions).

### Flujo de Despliegue
1.  **Checkout:** Descarga el código.
2.  **SCP:** Copia los archivos a `/opt/valencia_traffic_platform`.
3.  **SSH Commands:**
    - Reconstruye la imagen de ingestión (`docker compose build --no-cache`).
    - Reinicia los servicios (`docker compose up -d`).

## 3. Configuración de Airflow (Post-Despliegue)

- **URL:** Entra a la UI en `https://airflow.rodrigoguardamagna.com`.

- **Connections:** (Si aplica) Conexión a Postgres o APIs.
- **Variables:**
    - `valencia_traffic_data_path`: Ruta absoluta donde se guardan los datos en el HOST.
        - Valor: `/opt/valencia_traffic_platform/data`

## 4. Acceso Seguro (SSH Tunnel)

No expongas el puerto 8080 a internet. Usa un túnel SSH para acceder a Airflow y Jupyter:

```bash
# Acceso a Jupyter (8888) solamente
ssh -L 8888:127.0.0.1:8888 usuario@<VPS_IP>
```
Abrir Jupyter: `http://localhost:8888`