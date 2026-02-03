from flask import Flask, render_template, jsonify, request
from core.guardian import Guardian
from core.shield import Shield
from core.ghost import Ghost
from core.analyzer import Analyzer
from core.vault import Vault
import threading
import psutil
import time
import os
from datetime import datetime

app = Flask(__name__)

# --- Inicialización de Componentes ---
guardian = Guardian()
shield = Shield()
ghost = Ghost()
analyzer = Analyzer()
vault = Vault()

action_history = []
blacklisted_names = set()

def auto_purge_worker():
    """Vigilancia Activa: Ejecuta la limpieza de la lista negra."""
    while True:
        try:
            if blacklisted_names:
                # Usamos un set local para comparación ultra-rápida
                current_blacklist = set(blacklisted_names)
                for proc in psutil.process_iter(['name']):
                    try:
                        if proc.info['name'] in current_blacklist:
                            proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            
            # Refuerzo de prioridad para Fortaleza
            vault.elevate_priority()
        except:
            pass
        time.sleep(3)

threading.Thread(target=auto_purge_worker, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/nodes')
def get_nodes():
    return jsonify(guardian.scan_connections())

@app.route('/api/history')
def get_history():
    return jsonify(action_history)

@app.route('/api/scan_proactive')
def scan_proactive():
    return jsonify(analyzer.scan_persistence())

@app.route('/api/ghost/toggle', methods=['POST'])
def toggle_ghost():
    if not ghost.is_obfuscating:
        success = ghost.start_stealth_mode()
        msg = "MODO GHOST: ACTIVADO" if success else "Error de Configuración"
    else:
        success = ghost.reset_dns()
        ghost.is_obfuscating = False
        msg = "MODO GHOST: DESACTIVADO"
    return jsonify({"status": "success" if success else "error", "message": msg, "active": ghost.is_obfuscating})

@app.route('/api/action', methods=['POST'])
def action():
    data = request.json
    pid = int(data.get('pid', 0))
    method = data.get('method')
    target_name = data.get('name', 'Desconocido')
    
    # CORRECCIÓN CRÍTICA: Limpieza de IP para el Firewall
    # Extraemos solo la IP eliminando el puerto si existe
    raw_ip = data.get('remote_ip', "")
    remote_ip = raw_ip.split(':')[0] if ":" in raw_ip else raw_ip

    msg = "Comando procesado"

    if method == "isolate":
        try:
            p = psutil.Process(pid)
            if p.status() == psutil.STATUS_STOPPED:
                p.resume()
                msg = f"REANUDADO: {target_name}"
            else:
                p.suspend()
                msg = f"PAUSADO: {target_name}"
        except:
            msg = "Error: Proceso inaccesible"

    else:
        # Acción asíncrona para evitar lag en la UI
        def background_task(m, p, ip, name):
            if m == "terminate":
                blacklisted_names.add(name)
                shield.terminate_process(p)
            elif m == "block_ip" and ip:
                # Aquí es donde el escudo de Shield.py actúa
                shield.block_ip_firewall(ip)

        threading.Thread(target=background_task, args=(method, pid, remote_ip, target_name)).start()
        msg = f"EJECUTANDO {method.upper()}..."

    action_history.append({
        "type": "RED" if method == "block_ip" else "PROCESO",
        "target": remote_ip if method == "block_ip" else f"{target_name} ({pid})",
        "action": method.upper(),
        "time": datetime.now().strftime("%H:%M:%S"),
        "raw_target": target_name if method == "terminate" else (remote_ip if method == "block_ip" else pid)
    })
    
    return jsonify({"status": "success", "message": msg})

@app.route('/api/revert', methods=['POST'])
def revert():
    data = request.json
    action_type = data.get('action')
    target = data.get('target')

    if action_type == "BLOCK_IP":
        shield.unblock_all()
        return jsonify({"status": "success", "message": "Firewall limpio."})
    elif action_type == "TERMINATE":
        blacklisted_names.discard(target)
        return jsonify({"status": "success", "message": f"Whitelist: {target}"})

    return jsonify({"status": "error", "message": "No reversible"})

def start_server():
    print("\n" + "!"*60)
    print("   SISTEMA FORTALEZA - PROTOCOLO DE SEGURIDAD MÁXIMA")
    print("   Consola: http://127.0.0.1:5000")
    print("!"*60 + "\n")
    vault.protect_process()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

if __name__ == "__main__":
    start_server()