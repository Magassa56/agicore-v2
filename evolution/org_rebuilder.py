from brain.llm import ask_llm
import os

ORG_PROMPT_PATH = "prompts/org_rebuilder.md"
system_instruction = ""
if os.path.exists(ORG_PROMPT_PATH):
    with open(ORG_PROMPT_PATH, 'r') as f:
        system_instruction = f.read()

def evolve_company(company_history):
    """🔥 Organization Rebuilder : Auto-structure l'entreprise IA."""
    print("🏢 [ORG REBUILDER] Analyse de la structure organisationnelle...")
    prompt = f"""
    En tant qu'Architecte Organisationnel, analyse l'historique de l'entreprise :
    {company_history[-10:]}

    Reconstruis ou optimise la structure actuelle d'AGIcore pour maximiser l'efficacité.
    """
    
    return ask_llm(prompt, system_instruction=system_instruction, priority="low")
