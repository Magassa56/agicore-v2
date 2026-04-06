import psutil

def system_health():
    """
    Récupère les métriques de santé système essentielles.
    """
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

def detect_anomaly(metrics):
    """
    Détecte les anomalies basées sur des seuils critiques.
    """
    if metrics["cpu"] > 85:
        return "HIGH_CPU"
    if metrics["ram"] > 90:
        return "HIGH_RAM"
    if metrics["disk"] > 90:
        return "LOW_DISK"
    return "OK"
