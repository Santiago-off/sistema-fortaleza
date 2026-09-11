import subprocess
import ipaddress
import psutil
import time


def _is_valid_ip(value):
    """Devuelve True solo si `value` es una dirección IPv4/IPv6 literal y válida.

    Es la barrera entre lo que llega por la red y lo que se pasa a `netsh`.
    Cualquier cosa que no sea una IP exacta (una IP con puerto, un nombre de
    host, o una cadena con metacaracteres de shell como `&`, `|` o `;`) se
    rechaza aquí, antes de construir ningún comando.
    """
    try:
        ipaddress.ip_address(value)
        return True
    except ValueError:
        return False


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
                except Exception:
                    pass
            p.kill()

            # 2. Refuerzo con taskkill (fuerza bruta del sistema).
            # Lista de argumentos, sin shell: el nombre del proceso nunca se
            # interpreta como parte de un comando, solo como un argumento.
            subprocess.Popen(
                ["taskkill", "/F", "/IM", process_name, "/T"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except Exception:
            # Si el proceso ya no existe, devolvemos True porque el objetivo se cumplió
            return True

    def block_ip_firewall(self, ip):
        """Bloquea el tráfico entrante y saliente de una IP específica."""
        # Evitar auto-bloqueo (loopback) y descartar todo lo que no sea una IP.
        if ip in ["LISTEN", "", "127.0.0.1", "::1", "localhost"]:
            return False
        if not _is_valid_ip(ip):
            return False

        rule_name = "FORTALEZA_BLOCK_" + ip

        # Bloqueo total: entrada y salida, en los tres perfiles de red.
        # Lista de argumentos, sin `shell=True`: la IP ya está validada y,
        # aun así, no la interpreta ningún intérprete de comandos.
        subprocess.Popen(
            ["netsh", "advfirewall", "firewall", "add", "rule",
             "name=" + rule_name + "_OUT", "dir=out", "action=block",
             "remoteip=" + ip, "profile=any"],
            stdout=subprocess.DEVNULL,
        )
        subprocess.Popen(
            ["netsh", "advfirewall", "firewall", "add", "rule",
             "name=" + rule_name + "_IN", "dir=in", "action=block",
             "remoteip=" + ip, "profile=any"],
            stdout=subprocess.DEVNULL,
        )
        return True

    def unblock_all(self):
        """Elimina únicamente las reglas creadas por Fortaleza.

        Se borran por prefijo de nombre con PowerShell. No se tocan las demás
        reglas del cortafuegos del sistema.
        """
        subprocess.Popen(
            ["powershell", "-NoProfile", "-Command",
             "Remove-NetFirewallRule -DisplayName 'FORTALEZA_BLOCK_*' "
             "-ErrorAction SilentlyContinue"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
