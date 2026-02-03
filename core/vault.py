import ctypes
import os
import psutil

class Vault:
    def __init__(self):
        self.is_protected = False
        self.kernel32 = ctypes.windll.kernel32

    def elevate_priority(self):
        """Mantiene al proceso en la cima de la cola de ejecución del SO."""
        try:
            p = psutil.Process(os.getpid())
            # Prioridad ALTA: 0x00000080 (Suficiente para dominar sin causar lag)
            p.nice(psutil.HIGH_PRIORITY_CLASS) 
            return True
        except Exception:
            return False

    def prevent_sleep(self):
        """
        Impide que el sistema entre en modo suspensión o que la CPU baje 
        su rendimiento por ahorro de energía mientras Fortaleza opera.
        """
        try:
            # ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED
            self.kernel32.SetThreadExecutionState(0x80000001 | 0x00000040)
        except:
            pass

    def lock_memory(self):
        """
        Sugerencia Táctica: Intenta evitar que Windows mueva Fortaleza 
        al archivo de paginación (swap) del disco, manteniéndolo en RAM física.
        """
        try:
            process = self.kernel32.GetCurrentProcess()
            # Aumentamos el tamaño mínimo de trabajo en RAM
            self.kernel32.SetProcessWorkingSetSize(process, 1024*1024*10, 1024*1024*50)
        except:
            pass

    def check_admin(self):
        """Verifica privilegios de Administrador (Necesario para netsh y prioridades)."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False

    def protect_process(self):
        """Activa el protocolo de persistencia y rendimiento."""
        if self.check_admin():
            self.elevate_priority()
            self.prevent_sleep()
            self.lock_memory() # Blindaje extra de RAM
            self.is_protected = True
            return True
        return False