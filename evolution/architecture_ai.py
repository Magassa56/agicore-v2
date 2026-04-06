import os
from brain.llm import ask_llm
from evolution.code_analyzer import get_full_codebase_string

# Chargement du prompt master Evolution V4
EVOLUTION_PROMPT_PATH = "prompts/self_evolution.md"
system_instruction = ""
if os.path.exists(EVOLUTION_PROMPT_PATH):
    with open(EVOLUTION_PROMPT_PATH, 'r') as f:
        system_instruction = f.read()

def evolve_system():
    """
    Moteur d'auto-évolution (Architecture AI).
    Analyse le code total et propose des améliorations.
    """
    print("🧠 [ARCHITECTURE AI] Analyse de la codebase entière...")
    codebase = get_full_codebase_string()
    
    # On utilise une priorité 'critical' pour que l'orchestrateur route vers le Cloud 
    # car l'analyse de codebase demande beaucoup de contexte et de raisonnement.
    prompt = f"Voici ma base de code actuelle :\n{codebase}\n\nIdentifie un module à améliorer ou propose une nouvelle fonctionnalité utile. Réponds avec le code complet du fichier modifié."
    
    return ask_llm(prompt, system_instruction=system_instruction, priority="critical")
