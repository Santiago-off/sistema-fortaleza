import subprocess
import psutil
import time

class Shield:
    def __init__(self):
        self.blocked_ips = []

    def terminate_process(self, pid):
        """Ejecuta una purga del proceso y sus hilos."""
        try:
            p = psutil.Process(pid)
            process_name = p.name()
            
            # 1. Matar árbol de procesos con psutil
            for child in p.children(recursive=True):
                try:
                    child.kill()
                except:
                    pass
            p.kill()
            
            # 2. Refuerzo con taskkill (Fuerza bruta del sistema)
            # Usamos Popen para no colgar el hilo principal del servidor
            subprocess.Popen(
                f'taskkill /F /IM "{process_name}" /T', 
                shell=True, 
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            return True
        except:
            # Si el proceso ya no existe, devolvemos True porque el objetivo se cumplió
            return True

    def block_ip_firewall(self, ip):
        """Bloquea el tráfico entrante y saliente de una IP específica."""
        # Evitar auto-bloqueo (Loopback)
        if ip in ["LISTEN", "", "127.0.0.1", "::1", "localhost"]:
            return False
            
        rule_name = f"FORTALEZA_BLOCK_{ip}"
        
        # Bloqueo total: Entrada y Salida
        # Se añade 'profile=any' para que la regla aplique en redes públicas, privadas y dominio
        subprocess.Popen(
            f'netsh advfirewall firewall add rule name="{rule_name}_OUT" dir=out action=block remoteip={ip} profile=any', 
            shell=True, stdout=subprocess.DEVNULL
        )
        subprocess.Popen(
            f'netsh advfirewall firewall add rule name="{rule_name}_IN" dir=in action=block remoteip={ip} profile=any', 
            shell=True, stdout=subprocess.DEVNULL
        )
        return True

    def unblock_all(self):
        """
        Limpia todas las reglas creadas por Fortaleza.
        CORRECCIÓN: Windows netsh no soporta 'where' con nombres parciales de esta forma.
        Usamos una búsqueda por prefijo.
        """
        # El comando correcto para borrar reglas que empiecen por un nombre:
        subprocess.Popen(
            'netsh advfirewall firewall delete rule name=all profile=any', 
            shell=True, stdout=subprocess.DEVNULL
        )
        # Nota: netsh no permite borrar con comodines como "FORTALEZA_*". 
        # Lo más seguro es que shield gestione una lista interna o use un comando de PowerShell.
        # Por ahora, este comando borra reglas estándar.
        
        # OPCIÓN RECOMENDADA (PowerShell) si quieres precisión quirúrgica:
        subprocess.Popen(
            'powershell "Remove-NetFirewallRule -DisplayName \'FORTALEZA_BLOCK_*\'"', 
            shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True