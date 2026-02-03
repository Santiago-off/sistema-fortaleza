import sys
import subprocess
import ctypes
import os

# Lista de dependencias necesarias
DEPENDENCIES = ["flask", "psutil", "requests", "axios-python"]

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_and_install_dependencies():
    """Verifica si las librerías están presentes; si no, las descarga."""
    print("[*] Verificando integridad del entorno...")
    
    for lib in DEPENDENCIES:
        try:
            # Intentamos importar la librería (manejando nombres de pip vs nombres de importación)
            import_name = lib.split('-')[0] if '-' in lib else lib
            __import__(import_name)
        except ImportError:
            print(f"[!] Dependencia faltante: {lib}. Iniciando despliegue...")
            try:
                # Ejecutamos pip de forma silenciosa pero efectiva
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                print(f"[+] {lib} instalada correctamente.")
            except Exception as e:
                print(f"[X] Error crítico instalando {lib}: {e}")
                sys.exit(1)

if __name__ == "__main__":
    # 1. Asegurar privilegios de Administrador
    if is_admin():
        # 2. Gestión de dependencias antes de importar el servidor
        check_and_install_dependencies()
        
        # 3. Una vez instaladas, procedemos al arranque
        from web.server import start_server
        start_server()
    else:
        # Re-ejecutar el script con privilegios de administrador
        print("[?] Solicitando privilegios de Administrador para el blindaje...")
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        except Exception as e:
            print(f"Error al elevar privilegios: {e}")
        sys.exit()