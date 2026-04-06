import psutil

def get_system_state():
    """👁️ Capteur Système : Analyse CPU, RAM et Disque."""
    return {
        "cpu": psutil.cpu_percent(interval=0.1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }
