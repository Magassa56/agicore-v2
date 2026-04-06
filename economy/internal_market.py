class TaskMarket:
    """🏭 Internal AI Economy : Le marché boursier interne des tâches d'AGIcore."""
    def __init__(self):
        self.tasks = []
        self.completed_value = 0

    def submit_task(self, agent_name, task_desc, value):
        """Un agent soumet une tâche avec une valeur estimée."""
        entry = {
            "agent": agent_name,
            "task": task_desc,
            "value": value,
            "status": "pending"
        }
        self.tasks.append(entry)
        print(f"💰 [ECONOMY] Nouvelle tâche sur le marché : {agent_name} -> {task_desc} ({value} pts)")

    def get_high_value_tasks(self):
        """Récupère les tâches les plus rentables pour l'organisme."""
        return sorted(self.tasks, key=lambda x: x["value"], reverse=True)

# Instance globale
internal_market = TaskMarket()
