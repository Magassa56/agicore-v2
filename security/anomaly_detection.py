def detect_security_anomaly(activity_metrics):
    """🚨 Anomaly Detection : Détecte les comportements suspects (DDOS, etc)."""
    if activity_metrics.get("requests_per_sec", 0) > 1000:
        return "DDOS_RISK"
    if activity_metrics.get("cpu_usage", 0) > 95:
        return "OVERLOAD_ATTACK"
    if activity_metrics.get("auth_failures", 0) > 10:
        return "BRUTE_FORCE_DETECTED"
    return "NORMAL"
