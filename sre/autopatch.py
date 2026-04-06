import os
from brain.llm import ask_llm

# Mandat SRE pour guider l'auto-patch
MANDATE_PATH = "prompts/MASTER_SRE_MANDATE.md"
system_instruction = ""
if os.path.exists(MANDATE_PATH):
    with open(MANDATE_PATH, 'r') as f:
        system_instruction = f.read()

def generate_fix(error_context):
    """
    Génère un patch de correction automatique pour une erreur donnée.
    """
    prompt = f"""
    Tu es un ingénieur logiciel senior SRE.

    Contexte de l'erreur / Incident :
    {error_context}

    Donne un patch de correction de code simple, robuste et applicable immédiatement.
    Privilégie les solutions qui empêchent la récurrence du problème.
    """

    return ask_llm(prompt, system_instruction=system_instruction)
