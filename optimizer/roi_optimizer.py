from brain.llm import ask_llm

def optimize_roi(system_metrics, business_data):
    """📊 ROI Optimizer : Équilibre coût infra vs valeur produite."""
    prompt = f"""
    Analyse le ROI global du système AGIcore.

    MÉTRIQUES SYSTÈME : {system_metrics}
    DONNÉES BUSINESS : {business_data[-5:] if business_data else "Aucune"}

    Optimise :
    - Revenus potentiels
    - Coût Cloud / Local
    - Productivité des agents

    Propose des ajustements pour maximiser le profit.
    """
    
    return ask_llm(prompt, priority="low")
