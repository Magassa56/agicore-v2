def self_growth_cycle(state):
    """🧬 Self-Growth Engine : Décide si l'organisme doit s'étendre ou se stabiliser."""
    
    # Logique organique basée sur les métriques
    opportunity_score = state.get("opportunity_score", 0)
    system_load = state.get("load", 0)
    
    print(f"🧬 [GROWTH] Analyse organique... Opp Score: {opportunity_score} | Load: {system_load}%")

    if opportunity_score > 80 and system_load < 70:
        return "EXPAND: CREATE NEW AGENT"
    
    if system_load > 90:
        return "CONTRACTION: OPTIMIZE OR SHUT DOWN AGENTS"

    return "STABLE"
