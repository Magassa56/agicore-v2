import os
import requests
import google.generativeai as genai
from typing import Optional
from cloud.gemini_bridge import ask_gemini as ask_gemini_cli
from sre.watchdog import system_health

# Configuration Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Configuration Ollama Local
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_DEFAULT_MODEL = "llama3" # Modifiez selon votre modèle local (ex: gemma, mistral)

def check_ollama():
    """Vérifie si le démon Ollama local est actif et répond."""
    try:
        r = requests.get("http://localhost:11434/", timeout=2)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False

def ask_ollama(prompt: str, system_instruction: Optional[str] = None) -> str:
    """Appel au modèle local via l'API Ollama."""
    full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_DEFAULT_MODEL,
            "prompt": full_prompt,
            "stream": False
        }, timeout=120)
        
        if response.status_code == 200:
            return response.json().get("response", "")
        return f"Erreur API Ollama: Status {response.status_code}"
    except Exception as e:
        return f"Erreur de connexion Ollama: {str(e)}"

def ask_gemini_api(prompt: str, system_instruction: Optional[str] = None, model_name: str = "gemini-2.0-flash") -> str:
    """Appel à l'API Google Gemini Cloud."""
    try:
        if not api_key:
            return "Erreur: GEMINI_API_KEY non configurée."
        model = genai.GenerativeModel(model_name=model_name, system_instruction=system_instruction)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erreur appel Gemini API: {str(e)}"

def ask_llm(prompt: str, system_instruction: Optional[str] = None, priority: str = "low") -> str:
    """
    Orchestrateur Multi-Cloud AGIcore (Prompt 6)
    Décide intelligemment où router la requête (Ollama Local, Gemini API, ou Gemini CLI).
    """
    metrics = system_health()
    cpu_load = metrics['cpu']
    ram_load = metrics['ram']
    
    use_cloud = False
    reason = ""
    
    # 1. Logique de décision (Orchestration Multi-Cloud)
    if priority == "critical":
        use_cloud = True
        reason = "Priorité CRITICAL -> besoin du meilleur raisonnement Cloud."
    elif cpu_load > 85 or ram_load > 90:
        use_cloud = True
        reason = f"Ressources locales saturées (CPU: {cpu_load}%, RAM: {ram_load}%)."
        
    # 2. Exécution Locale (Ollama)
    if not use_cloud:
        if check_ollama():
            print(f"🧠 [ORCHESTRATOR] Routage LOCAL ({OLLAMA_DEFAULT_MODEL}) -> Zéro coût, latence minimale.")
            return ask_ollama(prompt, system_instruction)
        else:
            print("⚠️ [ORCHESTRATOR] Ollama local inactif ou injoignable. Fallback vers le Cloud.")
            use_cloud = True
            reason = "Ollama indisponible."

    # 3. Exécution Cloud (Gemini API ou CLI Bridge)
    if use_cloud:
        print(f"☁️ [ORCHESTRATOR] Décision Cloud prise. Raison: {reason}")
        if api_key:
            print("☁️ [ORCHESTRATOR] Routage CLOUD -> Gemini API.")
            return ask_gemini_api(prompt, system_instruction)
        else:
            print("☁️ [ORCHESTRATOR] Routage CLOUD -> Gemini CLI Fallback Bridge.")
            # Le CLI Bridge ne gère pas nativement le system_instruction séparé, on concatène
            full_prompt = f"INSTRUCTION SYSTEME:\n{system_instruction}\n\nPROMPT:\n{prompt}" if system_instruction else prompt
            return ask_gemini_cli(full_prompt)
