@echo off
TITLE SISTEMA FORTALEZA - Centro de Mando
COLOR 0A
CLS

:: Verificación de existencia de Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] ERROR: Python no esta instalado en este sistema.
    echo [!] Por favor, instale Python 3.10 o superior para continuar.
    pause
    exit
)

echo ============================================================
echo           INICIANDO PROTOCOLO SISTEMA FORTALEZA
echo ============================================================
echo [*] Preparando entorno de ejecucion...
echo [*] Solicitando elevacion de privilegios...
echo.

:: Ejecutar el script principal
python main.py

:: Si el programa se cierra, mantener la ventana abierta para ver errores
if %errorlevel% neq 0 (
    echo.
    echo [!] El sistema se ha detenido con un codigo de error.
    pause
)