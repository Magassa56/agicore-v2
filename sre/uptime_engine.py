from perception.system_sensor import get_system_state
from sre.watchdog import detect_anomaly

def check_system():
    """🛡️ Uptime Engine : Garantit la stabilité de l'AI Company."""
    metrics = get_system_state()
    status = detect_anomaly(metrics)
    
    return {
        "metrics": metrics,
        "status": status,
        "is_healthy": status == "OK"
    }
