def compute_profit(revenue, cost):
    """💰 Calculateur de Profit Simple."""
    return revenue - cost

def economic_state(history_data):
    """💰 Analyse l'état financier de l'AI Company."""
    # Simulation: On pourrait ici lire des balances réelles via API
    total_rev = sum([d.get("revenue", 0) for d in history_data])
    total_cost = sum([d.get("cost", 0) for d in history_data])
    
    return {
        "revenue": total_rev,
        "cost": total_cost,
        "net_profit": total_rev - total_cost
    }
