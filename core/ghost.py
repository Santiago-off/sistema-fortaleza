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
            output = subprocess.check_output(
                ["netsh", "interface", "ipv4", "show", "route"]
            ).decode('latin-1')

            # Buscamos la interfaz con métrica de red activa
            for line in output.split('\n'):
                if "0.0.0.0/0" in line:
                    parts = re.split(r'\s+', line.strip())
                    if len(parts) >= 5:
                        interface_name = " ".join(parts[4:])
                        return interface_name.strip()

            # Fallback a búsqueda por estado
            status = subprocess.check_output(
                ["netsh", "interface", "show", "interface"]
            ).decode('latin-1')
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
            # 1. Configurar IPv4 Primario y Secundario.
            # Lista de argumentos: el nombre de la interfaz, aunque lleve
            # espacios, es un solo argumento y no lo interpreta ningún shell.
            subprocess.run(["netsh", "interface", "ipv4", "set", "dns",
                            "name=" + interface, "source=static",
                            "address=" + self.dns_v4[0], "register=primary"],
                           capture_output=True)
            subprocess.run(["netsh", "interface", "ipv4", "add", "dns",
                            "name=" + interface, "addr=" + self.dns_v4[1],
                            "index=2"], capture_output=True)

            # 2. Blindaje contra fugas IPv6
            # En lugar de "none", usamos static sin dirección para forzar el vaciado
            subprocess.run(["netsh", "interface", "ipv6", "set", "dns",
                            "name=" + interface, "source=static",
                            "address=none", "validate=no"], capture_output=True)

            # 3. Refrescar Stack de Red
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True)

            return True
        except Exception as e:
            print(f"[!] Error Ghost: {e}")
            return False

    def reset_dns(self):
        """Restaura la configuración original del ISP (DHCP)."""
        interface = self.get_active_interface()
        try:
            subprocess.run(["netsh", "interface", "ipv4", "set", "dns",
                            "name=" + interface, "source=dhcp"], capture_output=True)
            subprocess.run(["netsh", "interface", "ipv6", "set", "dns",
                            "name=" + interface, "source=dhcp"], capture_output=True)
            subprocess.run(["ipconfig", "/flushdns"], capture_output=True)
            return True
        except:
            return False

    def start_stealth_mode(self):
        """Punto de entrada para el servidor Flask."""
        success = self.set_secure_dns()
        if success: 
            self.is_obfuscating = True
        return success