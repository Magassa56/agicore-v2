class Node:
    def __init__(self, name, capacity):
        self.name = name
        self.capacity = capacity
        self.load = 0

    def execute(self, task):
        self.load += 10 # Simule l'augmentation de charge
        print(f"📡 [NODE {self.name}] Exécution de la tâche : {task}")
        return f"Result from {self.name}"

class NodeManager:
    """🌐 Node System : Gère le réseau distribué de machines AGIcore."""
    def __init__(self):
        self.nodes = []

    def register_node(self, name, capacity):
        node = Node(name, capacity)
        self.nodes.append(node)
        print(f"🔗 [NETWORK] Nouveau nœud enregistré : {name} (Capacité: {capacity})")

    def distribute_task(self, task):
        """Envoie la tâche au meilleur nœud disponible (load balancing)."""
        if not self.nodes:
            return "Erreur : Aucun nœud disponible."
        
        best_node = min(self.nodes, key=lambda n: n.load)
        return best_node.execute(task)

# Instance globale
node_manager = NodeManager()
