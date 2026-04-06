from brain.llm import ask_llm

def optimize_meta(memory_history):
    """⚙️ Meta Optimizer : Apprentissage continu à partir de la mémoire."""
    if not memory_history:
        return "Pas assez de données pour optimiser."
        
    prompt = f"""
    Analyse les performances récentes d'AGIcore à partir de sa mémoire :
    {memory_history[-10:]}

    Propose une amélioration concrète sur :
    - La stratégie de trading
    - L'architecture système
    - La gestion des coûts cloud
    - La performance globale
    """
    
    return ask_llm(prompt, priority="low")
