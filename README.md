# 🛡️ SISTEMA FORTALEZA (V.1.0)

![Status](https://img.shields.io/badge/STATUS-OPERATIONAL-00ff41?style=for-the-badge&logo=target)
![Python](https://img.shields.io/badge/PYTHON-3.14-0088ff?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/PLATFORM-WINDOWS-red?style=for-the-badge&logo=windows&logoColor=white)
![License](https://img.shields.io/badge/SECURITY-MAXIMUM-yellow?style=for-the-badge)

**SISTEMA FORTALEZA** es una suite de seguridad proactiva y telemetría de red diseñada para el monitoreo en tiempo real, protección de procesos críticos y defensa perimetral. Utiliza un motor híbrido de análisis de integridad y reglas de firewall dinámicas.

---

## ⚡ Instalación y Arranque Rápido

El sistema cuenta con un **Bootloader Táctico** en `main.py` que verifica e instala todas las dependencias necesarias de forma automática.

1.  **Clonar Repositorio:**
    ```bash
    git clone [https://github.com/Santiago-off/sistema-fortaleza.git](https://github.com/Santiago-off/sistema-fortaleza.git)
    cd sistema-fortaleza
    ```
2.  **Ejecutar:**
    Localiza el archivo `run.bat` en la carpeta principal y ejecútalo con doble click.

> 💡 **Nota:** El sistema solicitará automáticamente privilegios de **Administrador** para poder interactuar con el Firewall y las prioridades del Kernel.

---

## 🛠️ Arquitectura del Núcleo (Core)

El sistema se divide en módulos especializados para garantizar un blindaje 360°:

| Módulo | Componente | Función Operativa |
| :--- | :--- | :--- |
| 🔍 | **Guardian** | Escaneo de conexiones, rutas de ejecutables y verificación de firmas SHA-256 con caché de alta eficiencia. |
| 🛡️ | **Shield** | Brazo ejecutor. Realiza bloqueos de IP mediante `netsh` y exterminio de procesos persistentes vía `taskkill`. |
| 👻 | **Ghost** | Módulo de invisibilidad. Configura DNS seguros (Cloudflare) y bloquea fugas de datos en protocolos IPv6. |
| 🔒 | **Vault** | Protección del proceso Fortaleza. Eleva la prioridad en la CPU y bloquea el Working Set en la RAM física. |
| 🧠 | **Analyzer** | Escaneo heurístico de persistencia en el Registro de Windows (HKCU/HKLM) y cálculo de entropía de archivos. |

---

## 📊 Centro de Mando (Interfaz Web)

Una vez iniciado, el sistema despliega un servidor Flask de alta disponibilidad. Puedes acceder a la consola táctica en:

🔗 **Consola:** `http://localhost:5000`

### Acciones Disponibles:
* **PAUSE (⏸️):** Suspende los hilos del proceso sin terminarlo (Modo Cuarentena).
* **BLOCK IP (🛡️):** Corta toda comunicación entrante y saliente con la IP remota seleccionada.
* **TERMINATE (🚫):** Cierra el proceso y lo añade a una **Lista Negra** activa que impide su reapertura.

---
## 🛡️ Seguridad y Privacidad
Cero Fugas: Ghost desactiva DNS de IPv6 para forzar el tráfico por túneles conocidos.

Integridad: Cada proceso detectado es verificado contra un Hash SHA-256 único.

Auto-Purga: El sistema incluye un hilo daemon que escanea el sistema cada 3 segundos en busca de procesos reincidentes en la lista negra.


## ⚠️ ADVERTENCIA:
    Este software interactúa con configuraciones críticas del sistema operativo. Úselo de manera responsable.

---

## 📂 Estructura del Proyecto

El proyecto mantiene una jerarquía estricta para asegurar la estabilidad:

```text
sistema-fortaleza/
├── core/                # Librerías de seguridad y motores de análisis
│   ├── analyzer.py      # Escáner de persistencia y entropía
│   ├── ghost.py         # Gestión de DNS y privacidad
│   ├── guardian.py      # Telemetría de red y hashes
│   ├── shield.py        # Control de Firewall y procesos
│   └── vault.py         # Autoprotección y prioridad
├── web/                 # Servidor de interfaz y recursos estáticos
│   ├── static/          # CSS (Cyberpunk Style) y JS (Radar SVG)
│   ├── templates/       # HTML principal (index.html)
│   └── server.py        # Cerebro de la API y Vigilante (auto_purge)
├── logs/                # Historial de detecciones y bloqueos
├── main.py              # Bootloader y Elevador de Privilegios
└── run.bat              # Lanzador rápido (Directo a ejecución)