class GlobalMarket:
    """💰 Global Market : Centralise les opportunités d'affaires mondiales."""
    def __init__(self):
        self.requests = []

    def add_request(self, client, need, budget):
        self.requests.append({
            "client": client,
            "need": need,
            "budget": budget,
            "status": "open"
        })
        print(f"🌍 [GLOBAL MARKET] Nouvelle opportunité : {client} cherche '{need}' (Budget: ${budget})")

    def get_best_opportunities(self, limit=3):
        """Retourne les deals les plus rentables (High Budget)."""
        return sorted(self.requests, key=lambda x: x["budget"], reverse=True)[:limit]

# Instance globale
global_market = GlobalMarket()
