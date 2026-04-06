def authenticate(api_key, valid_keys):
    """🔐 Authentification simple par clé d'API."""
    return api_key in valid_keys

def verify_node_trust(node_data):
    """
    🛡️ Zero Trust Policy (Level 13)
    Aucun nœud n'est fiable par défaut.
    """
    if not node_data.get("authenticated", False):
        return False
    if node_data.get("risk_score", 100) > 70:
        print(f"⚠️ [ZERO TRUST] Nœud REJETÉ (Score de risque élevé : {node_data['risk_score']})")
        return False
    return True
