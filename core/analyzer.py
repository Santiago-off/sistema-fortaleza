import os
import hashlib
import winreg
import math

class Analyzer:
    def __init__(self, api_key=None):
        self.api_key = api_key
        # Ampliamos a llaves de Sistema (Requiere Admin) y Usuario
        self.persistence_locations = [
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce")
        ]

    def get_file_hash(self, file_path):
        """Calcula SHA-256 de forma segura."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except:
            return None

    def calculate_entropy(self, file_path):
        """
        Calcula la entropía de Shannon. 
        Valores cercanos a 8.0 indican archivos cifrados o comprimidos (sospechosos).
        """
        try:
            with open(file_path, "rb") as f:
                data = f.read(1024 * 10) # Analizamos solo los primeros 10KB para velocidad
                if not data: return 0
                
                entropy = 0
                for x in range(256):
                    p_x = float(data.count(x)) / len(data)
                    if p_x > 0:
                        entropy += - p_x * math.log(p_x, 2)
                return round(entropy, 2)
        except:
            return 0

    def scan_persistence(self):
        """Escanea múltiples colmenas del registro buscando persistencia."""
        found_entries = []
        for hive, location in self.persistence_locations:
            try:
                key = winreg.OpenKey(hive, location, 0, winreg.KEY_READ)
                for i in range(0, winreg.QueryInfoKey(key)[1]):
                    name, value, _ = winreg.EnumValue(key, i)
                    
                    # Limpieza avanzada de ruta
                    clean_path = value.split(' -')[0].split(' /')[0].replace('"', '').strip()
                    
                    if os.path.exists(clean_path):
                        entropy = self.calculate_entropy(clean_path)
                        found_entries.append({
                            "name": name,
                            "path": clean_path,
                            "hash": self.get_file_hash(clean_path),
                            "entropy": entropy,
                            "suspicious": entropy > 7.2, # Umbral de sospecha
                            "type": "REGISTRY_SYSTEM" if hive == winreg.HKEY_LOCAL_MACHINE else "REGISTRY_USER"
                        })
                winreg.CloseKey(key)
            except WindowsError:
                continue
        return found_entries

    def deep_scan_directory(self, directory):
        """Escaneo selectivo para evitar el colapso del sistema."""
        suspicious_files = []
        # Solo escaneamos carpetas críticas si el usuario lo pide
        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.exe', '.dll', '.vbs', '.ps1')):
                    path = os.path.join(root, file)
                    entropy = self.calculate_entropy(path)
                    
                    # Solo reportamos archivos con alta entropía o extensiones raras
                    if entropy > 7.5 or file.endswith(('.vbs', '.ps1')):
                        suspicious_files.append({
                            "name": file,
                            "path": path,
                            "entropy": entropy,
                            "hash": self.get_file_hash(path)
                        })
        return suspicious_files