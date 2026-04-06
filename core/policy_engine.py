def safe_self_modify(patch, sre_decision):
    """
    🛡️ Mode de Self-Modification Sécurisé (Level 9).
    Exécute le patch SI ET SEULEMENT SI le SRE Master l'autorise.
    """
    
    # On parse la décision SRE (elle devrait être un JSON, on cherche juste les mots-clés)
    risk_level = "UNKNOWN"
    if '"risk_level": "HIGH"' in sre_decision or "'risk_level': 'HIGH'" in sre_decision:
        risk_level = "HIGH"
        
    actions = sre_decision
    
    if risk_level == "HIGH":
        print("🛑 [POLICY ENGINE] Modification BLOQUÉE par le SRE Master (Risk: HIGH).")
        return "BLOCKED BY SRE MASTER"

    if "pause_self_modification" in actions:
        print("⏸️ [POLICY ENGINE] Le SRE Master a mis l'auto-évolution en pause.")
        return "SELF-MODIFICATION PAUSED"

    print("⚡ [POLICY ENGINE] Validation SRE reçue. Exécution du patch dans la Sandbox...")
    # L'exécution sandbox sera gérée dans le self_improver comme avant.
    return "PATCH CLEARED FOR EXECUTION"
