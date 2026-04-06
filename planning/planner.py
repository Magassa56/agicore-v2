from brain.llm import ask_llm

def decide_action(market_state, system_state, memory_history):
    """🎯 Planificateur Intelligent : Décide de l'action globale."""
    prompt = f"""
    Tu es l'Agent de Décision Central AGIcore.

    ÉTAT DU MARCHÉ :
    {market_state}

    ÉTAT DU SYSTÈME :
    {system_state}

    MÉMOIRE RÉCENTE (Historique) :
    {memory_history[-5:] if memory_history else "Aucun historique"}

    Décide de la meilleure action à entreprendre :
    - Action Trading (BUY/SELL/HOLD + raison)
    - Action Système (OPTIMIZE_CPU / REFACTOR_CODE / SLEEP / SCALE_CLOUD)

    Réponds au format JSON structuré avec "action_type", "details" et "priority".
    """
    
    return ask_llm(prompt, priority="low")
