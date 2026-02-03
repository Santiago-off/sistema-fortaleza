import subprocess
import re

class Ghost:
    def __init__(self):
        self.is_obfuscating = False
        # Cloudflare DNS (Privacidad y Velocidad)
        self.dns_v4 = ["1.1.1.1", "1.0.0.1"]

    def get_active_interface(self):
        """
        Detecta la interfaz activa usando el enrutamiento predeterminado.
        Es más preciso que listar interfaces habilitadas.
        """
        try:
            # Obtenemos la interfaz que tiene la ruta por defecto (0.0.0.0)
            route_cmd = 'netsh interface ipv4 show route'
            output = subprocess.check_output(route_cmd, shell=True).decode('latin-1')
            
            # Buscamos la interfaz con métrica de red activa
            for line in output.split('\n'):
                if "0.0.0.0/0" in line:
                    parts = re.split(r'\s+', line.strip())
                    if len(parts) >= 5:
                        interface_name = " ".join(parts[4:])
                        return interface_name.strip()
            
            # Fallback a búsqueda por estado
            status_cmd = 'netsh interface show interface'
            status = subprocess.check_output(status_cmd, shell=True).decode('latin-1')
            for line in status.split('\n'):
                if "Conectado" in line or "Connected" in line:
                    parts = re.split(r'\s{2,}', line.strip())
                    return parts[-1].strip()
                    
            return "Ethernet"
        except:
            return "Ethernet"

    def set_secure_dns(self):
        interface = self.get_active_interface()
        try:
            # 1. Configurar IPv4 Primario y Secundario
            # Usamos comillas dobles escapadas para nombres de interfaz con espacios
            subprocess.run(f'netsh interface ipv4 set dns name="{interface}" source=static address={self.dns_v4[0]} register=primary', shell=True, capture_output=True)
            subprocess.run(f'netsh interface ipv4 add dns name="{interface}" addr={self.dns_v4[1]} index=2', shell=True, capture_output=True)
            
            # 2. Blindaje contra fugas IPv6
            # En lugar de "none", usamos static sin dirección para forzar el vaciado
            subprocess.run(f'netsh interface ipv6 set dns name="{interface}" source=static address=none validate=no', shell=True, capture_output=True)
            
            # 3. Refrescar Stack de Red
            subprocess.run('ipconfig /flushdns', shell=True, capture_output=True)
            
            return True
        except Exception as e:
            print(f"[!] Error Ghost: {e}")
            return False

    def reset_dns(self):
        """Restaura la configuración original del ISP (DHCP)."""
        interface = self.get_active_interface()
        try:
            subprocess.run(f'netsh interface ipv4 set dns name="{interface}" source=dhcp', shell=True, capture_output=True)
            subprocess.run(f'netsh interface ipv6 set dns name="{interface}" source=dhcp', shell=True, capture_output=True)
            subprocess.run('ipconfig /flushdns', shell=True, capture_output=True)
            return True
        except:
            return False

    def start_stealth_mode(self):
        """Punto de entrada para el servidor Flask."""
        success = self.set_secure_dns()
        if success: 
            self.is_obfuscating = True
        return success