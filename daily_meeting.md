# 📅 Project Status - Valencia Traffic Data Platform

**Objetivo:** Construir una plataforma de datos "Cloud-Native" que ingeste, almacene y procese datos de tráfico de Valencia en tiempo real para crear un histórico y realizar predicciones.

## 🚀 Estado Actual
- **Fase:** Operación y Mantenimiento ("The Chronicler").
- **Estado:** 🟢 Desplegado en VPS (Producción).
- **Hito:** Ingestión de datos activa y segura.

## ✅ Log de Avances

### Infraestructura y Despliegue
- [x] **Arquitectura:** Definida estrategia GitOps (GitHub -> VPS).
- [x] **Orquestación:** Airflow desplegado con Docker Compose (Webserver, Scheduler, Postgres).
- [x] **Seguridad:**
    - Configurado Reverse Proxy (Nginx) + SSL (HTTPS).
    - Deshabilitada exposición de puertos inseguros.
    - Gestión de usuarios y contraseñas asegurada.

### Ingestión de Datos ("The Chronicler")
- [x] **Pipeline:** DAG `valencia_traffic_ingestion` ejecutándose cada 10 minutos.
- [x] **Source:** API Open Data Valencia.
- [x] **Storage:** Datos crudos (JSON) almacenados en estructura particionada `data/raw/YYYY/MM/DD/`.

### DevOps & Mantenimiento (Nuevo)
- [x] **CI/CD:** Configurado pipeline de despliegue automático en GitHub Actions.
- [x] **Documentación:** Creada guía de despliegue `docs/deployment_setup.md`.
- [x] **Troubleshooting:** Solucionados problemas de conexión (IPv6 vs IPv4) en Nginx para n8n y Airflow.

## 📋 Próximos Pasos
1.  **Análisis Exploratorio ("The Refiner"):**
    - Cargar datos históricos en Notebooks.
    - Análisis de calidad de datos y estructura.
2.  **Optimización:**
    - Implementar mejoras del roadmap (compresión, alertas).

## 📝 Notas Técnicas
- **Fuente de Datos:** API Open Data Valencia (actualización cada 3 min).
- **Estrategia:** Ingestión "Snapshot" (foto completa) cada 10 min.
- **Formato:** JSON crudo con metadatos de ingestión (timestamp).
- **Infraestructura:** VPS Hetzner + Docker + Airflow.
