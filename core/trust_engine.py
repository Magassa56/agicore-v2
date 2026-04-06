def compute_trust_score(history):
    """🌐 Trust Engine : Calcule la réputation d'une IA dans l'écosystème."""
    score = 100
    
    # On pénalise les échecs et on récompense les succès
    failures = history.get("failures", 0)
    successes = history.get("success", 0)
    
    if failures > 5:
        score -= (failures * 5)
    
    if successes > 10:
        score += 20
        
    final_score = max(0, min(100, score))
    print(f"🤝 [TRUST ENGINE] Nouveau score calculé : {final_score}/100")
    return final_score
