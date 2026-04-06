def get_user_intent(message):
    """👁️ Perception Utilisateur : Analyse l'intention derrière un message."""
    # Simulation simple d'analyse d'intention
    intent = "unknown"
    if "create" in message or "build" in message:
        intent = "creation"
    elif "optimize" in message or "repair" in message:
        intent = "maintenance"
    
    return {
        "message": message,
        "intent": intent,
        "category": "business" if intent == "creation" else "technical"
    }
