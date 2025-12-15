# 🚀 Guía de Configuración de Despliegue Automático (CD)

Esta guía detalla los pasos para configurar tu VPS y GitHub para que las actualizaciones del repo se desplieguen directamente a él.

## 1. Generar Par de Claves SSH

Generaremos las claves directamente en tu carpeta segura `.ssh` para evitar que queden en el proyecto.

1.  Abre una terminal (PowerShell).
2.  Ejecuta el siguiente comando:
    ```powershell
    ssh-keygen -t rsa -b 4096 -C "github-actions-deploy" -f $env:USERPROFILE\.ssh\github_deploy_key
    ```
3.  Cuando te pida una "passphrase", déjala vacía (presiona Enter dos veces).

## 2. Configurar el VPS (Autorizar la clave)

Debemos copiar el contenido de la **clave pública** (`.pub`) al portapapeles para pegarlo en el VPS.

1.  **Copia la clave pública al portapapeles** (sin mostrarla en pantalla):
    ```powershell
    Get-Content $env:USERPROFILE\.ssh\github_deploy_key.pub | Set-Clipboard
    ```
2.  Conéctate a tu VPS vía SSH:
    ```bash
    ssh usuario@tu-ip-vps
    ```
3.  Edita (o crea) el archivo `authorized_keys`:
    ```bash
    nano ~/.ssh/authorized_keys
    ```
4.  Pega el contenido (Ctrl+V o clic derecho) en una nueva línea al final del archivo.
5.  Guarda y sal (`Ctrl+O`, `Enter`, `Ctrl+X`).
6.  Asegúrate de que los permisos sean correctos:
    ```bash
    chmod 700 ~/.ssh
    chmod 600 ~/.ssh/authorized_keys
    ```

## 3. Configurar Secretos en GitHub

Ahora necesitamos la **clave privada** para GitHub.

1.  **Copia la clave privada al portapapeles** (sin mostrarla en pantalla):
    ```powershell
    Get-Content $env:USERPROFILE\.ssh\github_deploy_key | Set-Clipboard
    ```
2.  Ve a tu repositorio en GitHub.
3.  Navega a **Settings** > **Secrets and variables** > **Actions**.
4.  Haz clic en **New repository secret** y añade los siguientes secretos:

    | Nombre | Valor |
    | :--- | :--- |
    | `VPS_HOST` | La dirección IP de tu VPS. |
    | `VPS_USERNAME` | Tu usuario en el VPS. |
    | `VPS_SSH_KEY` | Pega el contenido que acabas de copiar (Ctrl+V). **IMPORTANTE:** Debe incluir todo, desde `-----BEGIN...` hasta `-----END...`. |

## 4. El Flujo de Trabajo (Workflow)

El archivo `.github/workflows/deploy.yml` define el proceso. Ya lo tienes creado, pero nos aseguraremos de que haga lo siguiente:

1.  **Copiar archivos:** Usa `scp` para copiar todo el código nuevo al VPS.
2.  **Reconstruir y Reiniciar:** Se conecta por SSH para reconstruir las imágenes Docker y reiniciar los servicios para aplicar cambios.

### Verificación

Una vez configurado esto, cada vez que hagas un `git push origin main`, podrás ver el progreso en la pestaña **Actions** de tu repositorio en GitHub.
