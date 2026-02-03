import psutil
import hashlib
import functools

class Guardian:
    def __init__(self):
        self.identity_cache = {}

    # El argumento correcto es maxsize, no max_id
    @functools.lru_cache(maxsize=128)
    def _get_file_hash(self, path):
        """Calcula el hash SHA-256 de forma eficiente y lo guarda en caché."""
        try:
            hasher = hashlib.sha256()
            # Leemos en bloques para no saturar la RAM
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return "INTEGRIDAD_DESCONOCIDA"

    def scan_connections(self):
        nodes = []
        try:
            # Obtener todas las conexiones de red activas
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                # Solo nos interesan conexiones establecidas con una IP remota
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    try:
                        pid = conn.pid
                        if pid is None: continue
                        
                        proc = psutil.Process(pid)
                        path = proc.exe()
                        
                        # Aquí usamos la caché corregida
                        file_hash = self._get_file_hash(path)
                        
                        nodes.append({
                            "pid": pid,
                            "name": proc.name(),
                            "remote_ip": f"{conn.raddr.ip}:{conn.raddr.port}",
                            "hash": file_hash,
                            "status": proc.status()
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
        except Exception as e:
            print(f"[!] Error en escaneo de red: {e}")
            
        return nodes