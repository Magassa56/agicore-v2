import os
from brain.llm import ask_llm

# Chargement automatique du mandat SRE
MANDATE_PATH = "prompts/MASTER_SRE_MANDATE.md"
system_instruction = ""
if os.path.exists(MANDATE_PATH):
    with open(MANDATE_PATH, 'r') as f:
        system_instruction = f.read()

def analyze_incident(issue, metrics):
    """
    Analyse un incident en utilisant le LLM et le mandat SRE.
    """
    prompt = f"""
    Tu es un ingénieur SRE.

    Problème détecté : {issue}
    Métriques système : {metrics}

    Donne :
    1. cause probable
    2. niveau de gravité (LOW / MEDIUM / HIGH / CRITICAL)
    3. action immédiate (correction, redémarrage, nettoyage)
    """

    return ask_llm(prompt, system_instruction=system_instruction)
