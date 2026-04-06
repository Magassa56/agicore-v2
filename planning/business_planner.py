from brain.llm import ask_llm

def plan_business(user_intent, products_memory):
    """💰 Business Planner : Architecture la stratégie de revenus globale."""
    prompt = f"""
    Tu es l'Architecte Business d'AGIcore.

    INTENTION ACTUELLE : {user_intent}
    PRODUITS EXISTANTS : {products_memory[-5:] if products_memory else "Aucun"}

    Objectifs :
    - Maximiser les revenus
    - Réduire les coûts d'infrastructure
    - Automatiser la création de valeur

    Donne une stratégie business complète et exécutable.
    """
    
    return ask_llm(prompt, priority="low")
