from brain.llm import ask_llm
import os

# Mandat CEO V7
CEO_PROMPT_PATH = "prompts/ceo_strategy.md"
system_instruction = ""
if os.path.exists(CEO_PROMPT_PATH):
    with open(CEO_PROMPT_PATH, 'r') as f:
        system_instruction = f.read()

def ceo_decision(company_state):
    """🧠 CEO AI Engine : Prend les décisions stratégiques globales."""
    prompt = f"""
    Tu es le CEO AI d'AGIcore. Voici l'état actuel de ton entreprise :
    {company_state}

    Prends une décision stratégique majeure incluant :
    - Allocation des ressources aux départements
    - Priorité du jour (Trading, Marketing, Produit)
    - Réduction des coûts SRE
    - Innovation & R&D
    """
    
    # Priorité critique pour le CEO
    return ask_llm(prompt, system_instruction=system_instruction, priority="critical")
