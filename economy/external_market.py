class ExternalMarket:
    """💰 External Economy Engine : Interface avec le monde réel (clients humains)."""
    def __init__(self):
        self.orders = []
        self.total_revenue = 0

    def receive_order(self, client, request, budget):
        """AGIcore reçoit une commande d'un client réel."""
        order = {
            "client": client,
            "request": request,
            "budget": budget,
            "status": "received"
        }
        self.orders.append(order)
        print(f"💼 [EXTERNAL MARKET] Nouvelle commande : {client} -> {request} (${budget})")

    def process_orders(self):
        """Priorise les commandes par budget (maximisation du ROI)."""
        return sorted(self.orders, key=lambda x: x["budget"], reverse=True)

# Instance globale
external_market = ExternalMarket()
