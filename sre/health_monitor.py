import psutil

def system_state():
    """🛡️ SRE Health Monitor : Récupère l'état instantané du système."""
    return {
        "cpu": psutil.cpu_percent(interval=0.1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }
