def dynamic_pricing(base_cost, demand_level, competition_score=0.5):
    """💵 Pricing AI : Ajustement dynamique des prix en temps réel."""
    # Formule : Coût + (Demande * Boost) - (Compétition * Penalty)
    price = base_cost * 1.5 + demand_level * 0.3 - competition_score * 0.2
    return round(max(price, base_cost * 1.1), 2)
