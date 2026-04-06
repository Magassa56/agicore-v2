import random

def get_market_state():
    """👁️ Capteur Marché : Simule/Récupère les données live."""
    # Simulation de données pour le test (peut être remplacé par Alpaca/Binance API)
    return {
        "price": random.uniform(145, 155),
        "volume": random.randint(1000, 5000),
        "trend": random.choice(["UP", "DOWN", "SIDEWAYS"])
    }
