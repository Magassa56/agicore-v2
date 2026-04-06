class AGIMarketplace:
    """🤝 AGI Marketplace : Le marché inter-IA où les agents deviennent prestataires."""
    def __init__(self):
        self.services = []

    def register_service(self, agi_id, service_name, price):
        """Une IA enregistre ses compétences sur le marché."""
        self.services.append({
            "agi": agi_id,
            "service": service_name,
            "price": price
        })
        print(f"🛒 [AGI MARKET] Service enregistré : {agi_id} offre '{service_name}' pour {price} pts")

    def find_service(self, search_query):
        """Trouve les prestataires IA correspondant à un besoin."""
        results = [s for s in self.services if search_query.lower() in s["service"].lower()]
        return results

# Instance globale
agi_marketplace = AGIMarketplace()
