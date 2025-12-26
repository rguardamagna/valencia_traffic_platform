# 🚀 Future Improvements - The Chronicler (Ingestion Phase)

This document collects technical improvements identified for the data ingestion phase ("The Chronicler"). These improvements are not blocking for current operations but will elevate the quality, robustness, and maintainability of the project as it scales.

## 1. Code and Ingestion Logic (`src/ingestion/`)

- [ ] **External Configuration:**
    - Move the API URL (`API_URL`) to an environment variable or configuration file (`config.yaml`). Avoid hardcoding.
- [ ] **Storage Efficiency:**
    - Currently, we save JSON with indentation (`indent=2`), which takes up unnecessary space.
    - **Improvement:** Save in **NDJSON** (Newline Delimited JSON) format compressed with **GZIP** (`.json.gz`). This will drastically reduce disk usage on the VPS.
- [ ] **Resilience (Internal Retries):**
    - Implement retry logic within the script (using libraries like `tenacity` or `requests.HTTPAdapter`) to handle network micro-outages without failing the entire Airflow task immediately.
- [ ] **Data Validation (Data Quality):**
    - Add light schema validation (e.g., using `Pydantic` or `Great Expectations`) to ensure the API hasn't changed its format and we aren't saving garbage.

## 2. Orchestration (Airflow DAGs)

- [ ] **Path Portability:**
    - The DAG has the path `/root/valencia_traffic_platform/data` hardcoded.
    - **Improvement:** Use an Airflow Variable (`{{ var.value.project_path }}`) or environment variable so the DAG works in any environment (Dev/Prod) without editing code.
- [ ] **Failure Alerts:**
    - Currently, `email_on_failure` is set to `False`.
    - **Improvement:** Configure notifications to **Telegram** or **Slack** when ingestion fails. (You already have experience with this in the Job Hunter project).
- [ ] **Image Versioning:**
    - The DAG uses `valencia-traffic-ingestion:latest`.
    - **Improvement:** Use specific version tags (e.g., `:v1.0.1`) to ensure immutability and reproducibility.

## 3. Infrastructure and Security

- [ ] **Docker User (Security):**
    - The ingestion container runs as `root` by default (inside the container). It would be ideal to create a non-root user in the `Dockerfile` to improve security.
- [ ] **Data Cleanup (Retention Policy):**
    - There is no deletion policy. The VPS disk will eventually fill up.
    - **Improvement:** Create a maintenance DAG that moves old data (> 30 days) to cheap storage (S3/GCS) or compresses/archives it.

## 4. Testing

- [ ] **Unit Tests:**
    - Create unit tests for `ingest_traffic.py` (mocking the API response) to ensure that saving logic and filenames don't break with future changes.

## 5. Modeling and Machine Learning (The Oracle)

- [ ] **Automated Champion vs Challenger Strategy:**
    - Implement a periodic re-evaluation process (e.g., every 15 days).
    - Train a "Top 5" of models with different hyperparameters or algorithms.
    - Automatically promote a "Challenger" to "Champion" if it outperforms key metrics (e.g., F1-Score on minority classes).
- [ ] **Business/Traffic Metrics:**
    - Beyond Recall, measure time error (e.g., how many minutes of lag does the prediction have?).
- [ ] **MLOps with MLflow:**
    - Integrate MLflow for experiment tracking, model registry, and artifact versioning.

---
---

# 🚀 Mejoras Futuras - The Chronicler (Fase de Ingestión)

Este documento recopila las mejoras técnicas identificadas para la fase de ingestión de datos ("The Chronicler"). Estas mejoras no son bloqueantes para el funcionamiento actual, pero elevarán la calidad, robustez y mantenibilidad del proyecto a medida que escale.

## 1. Código y Lógica de Ingestión (`src/ingestion/`)

- [ ] **Configuración Externa:**
    - Mover la URL de la API (`API_URL`) a una variable de entorno o archivo de configuración (`config.yaml`). Evitar hardcoding.
- [ ] **Eficiencia de Almacenamiento:**
    - Actualmente guardamos JSON con indentación (`indent=2`), lo cual ocupa mucho espacio innecesario.
    - **Mejora:** Guardar en formato **NDJSON** (Newline Delimited JSON) comprimido con **GZIP** (`.json.gz`). Esto reducirá drásticamente el uso de disco en el VPS.
- [ ] **Resiliencia (Retries Internos):**
    - Implementar lógica de reintento dentro del script (usando librerías como `tenacity` o `HTTPAdapter` de `requests`) para manejar micro-cortes de red sin necesidad de fallar toda la tarea de Airflow inmediatamente.
- [ ] **Validación de Datos (Data Quality):**
    - Añadir una validación ligera del esquema de respuesta (ej. usar `Pydantic` o `Great Expectations`) para asegurar que la API no ha cambiado su formato y estamos guardando basura.

## 2. Orquestación (Airflow DAGs)

- [ ] **Portabilidad de Paths:**
    - El DAG tiene hardcodeada la ruta `/root/valencia_traffic_platform/data`.
    - **Mejora:** Usar una Variable de Airflow (`{{ var.value.project_path }}`) o variable de entorno para que el DAG funcione en cualquier entorno (Dev/Prod) sin editar código.
- [ ] **Alertas de Fallo:**
    - Actualmente `email_on_failure` está en `False`.
    - **Mejora:** Configurar notificaciones a **Telegram** o **Slack** cuando falle la ingestión. (Ya tienes experiencia con esto en el proyecto Job Hunter).
- [ ] **Versionado de Imágenes:**
    - El DAG usa `valencia-traffic-ingestion:latest`.
    - **Mejora:** Usar tags de versión específicos (ej. `:v1.0.1`) para garantizar inmutabilidad y reproducibilidad.

## 3. Infraestructura y Seguridad

- [ ] **Usuario de Docker (Seguridad):**
    - El contenedor de ingestión corre como `root` por defecto (dentro del contenedor). Sería ideal crear un usuario no-root en el `Dockerfile` para mejorar la seguridad.
- [ ] **Limpieza de Datos (Retention Policy):**
    - No hay política de borrado. El disco del VPS se llenará eventualmente.
    - **Mejora:** Crear un DAG de mantenimiento que mueva datos antiguos (> 30 días) a un almacenamiento barato (S3/GCS) o los comprima/archive.

## 4. Testing

- [ ] **Unit Tests:**
    - Crear tests unitarios para `ingest_traffic.py` (mockeando la respuesta de la API) para asegurar que la lógica de guardado y nombres de archivo no se rompa con cambios futuros.

## 5. Modelado y Machine Learning (The Oracle)

- [ ] **Estrategia Champion vs Challenger Automatizada:**
    - Implementar un proceso de reevaluación periódica (ej. cada 15 días).
    - Entrenar un Top 5 de modelos con diferentes hiperparámetros o algoritmos (ej. XGBoost, Random Forest, LightGBM).
    - Promover automáticamente al "Challenger" a "Champion" si supera métricas clave (ej. F1-Score en clases minoritarias).
- [ ] **Métricas de Negocio / Tráfico:**
    - Más allá del Recall, medir el error en tiempo (ej. ¿cuántos minutos de desfase tiene la predicción?).
- [ ] **MLOps con MLflow:**
    - Integrar MLflow para el seguimiento de experimentos, registro de modelos y versionado de artefactos.

## 6. Visualización ("The Spotlight")

- [ ] **Despliegue en Producción:**
    - Actualmente el dashboard corre localmente. El siguiente paso es desplegarlo en el VPS usando Docker y exponerlo de forma segura tras Nginx.
- [ ] **Filtros Avanzados:**
    - Permitir filtrar por barrios, tipos de vía o niveles de congestión específicos.
- [ ] **Histórico Dinámico:**
    - Añadir un "Time Slider" para visualizar cómo ha evolucionado el tráfico en las últimas horas/días basándose en el histórico almacenado.
- [ ] **Alertas en Dashboard:**
    - Notificaciones visuales cuando un tramo crítico supere el umbral de congestión.
