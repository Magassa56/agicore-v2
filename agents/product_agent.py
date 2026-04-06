from brain.llm import ask_llm

def generate_product_strategy(user_input, product_memory):
    """🤖 Product Agent : Génère une stratégie de monétisation automatique."""
    prompt = f"""
    Tu es un Business AI Agent spécialisé dans la monétisation.

    INPUT UTILISATEUR :
    {user_input}

    HISTORIQUE PRODUITS :
    {product_memory[-5:] if product_memory else "Aucun"}

    Génère une stratégie complète :
    1. Idée de produit monétisable
    2. Nom du produit
    3. Description marketing percutante
    4. Potentiel de vente (Estimation ROI)
    5. Stratégie de distribution (YouTube / TikTok / e-commerce)
    """
    
    # On utilise une priorité 'low' pour le routage intelligent
    return ask_llm(prompt, priority="low")
