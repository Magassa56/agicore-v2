import time
import os
from sre.watchdog import system_health, detect_anomaly
from sre.incident import analyze_incident
from sre.autopatch import generate_fix

# Variable globale pour suivre la position dans le fichier de log entre deux boucles
LAST_LOG_POS = 0

def check_logs(log_file="agicore_log.txt", last_pos=0):
    if not os.path.exists(log_file):
        return [], 0
    
    errors = []
    with open(log_file, 'r') as f:
        f.seek(last_pos)
        lines = f.readlines()
        current_pos = f.tell()
        for line in lines:
            if "ERROR" in line or "CRITICAL" in line or "Exception" in line:
                errors.append(line.strip())
    
    return errors, current_pos

def run_sre_loop():
    """
    Exécute une passe de contrôle SRE (Niveau 2/3 Automation).
    Cette fonction est appelée à chaque itération du main()
    """
    global LAST_LOG_POS
    
    metrics = system_health()
    status = detect_anomaly(metrics)
    
    print(f"[MONITOR] CPU: {metrics['cpu']}% | RAM: {metrics['ram']}% | STATUS: {status}")
    
    errors, LAST_LOG_POS = check_logs(last_pos=LAST_LOG_POS)
    
    if status != "OK":
        print(f"🚨 ANOMALIE SYSTÈME DÉTECTÉE: {status}")
        incident = analyze_incident(f"System status: {status}", metrics)
        print(f"🔍 ANALYSE LLM: {incident}")
        fix = generate_fix(incident)
        print(f"🔧 AUTO-PATCH SUGGÉRÉ: {fix}")
    
    for error in errors:
        print(f"🚨 ERREUR LOG DÉTECTÉE: {error}")
        incident = analyze_incident("Application error in logs", {"error": error, "system": metrics})
        print(f"🔍 ANALYSE LLM: {incident}")
        fix = generate_fix(incident)
        print(f"🔧 AUTO-PATCH SUGGÉRÉ: {fix}")

    time.sleep(5)
