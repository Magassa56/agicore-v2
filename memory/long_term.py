import json
import os

MEMORY_FILE = "ops/state/agicore_memory.json"

def store(log_entry):
    """🧠 Stockage dans la mémoire à long terme (JSON)."""
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    
    current_memory = load()
    current_memory.append(log_entry)
    
    # On garde les 500 derniers logs pour ne pas saturer le disque
    if len(current_memory) > 500:
        current_memory = current_memory[-500:]
        
    with open(MEMORY_FILE, 'w') as f:
        json.dump(current_memory, f, indent=4)

def load():
    """🧠 Chargement de l'historique mémoire."""
    if not os.path.exists(MEMORY_FILE):
        return []
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return []
