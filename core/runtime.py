from optimizer.self_improver import propose_improvement, apply_self_modification
from sre.health_monitor import system_state

def runtime_step(logs):
    """
    🔄 SELF-LEARNING LOOP (LEVEL 8 CORE RUNTIME)
    """
    print("\n--- 🧠 L8 SELF-MODIFICATION CYCLE ---")
    
    # 1. Analyser le système
    state = system_state()
    print(f"[RUNTIME] System State : CPU {state['cpu']}% | RAM {state['ram']}%")

    # 2. Proposer une amélioration via le LLM
    print("🤖 [RUNTIME] Réflexion sur une potentielle amélioration du code...")
    patch = propose_improvement(state, logs)
    
    # 3. Filtrer les réponses vides ou non-code (ex: messages du bridge)
    if "Erreur" in patch or len(patch) < 10:
        result = "Aucun patch valide proposé."
    else:
        # 4. Appliquer si safe (inclut Git Snapshot + Sandbox execution)
        result = apply_self_modification(patch)

    print(f"💡 [RUNTIME] Résultat : {result}")
    return result
