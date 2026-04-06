import subprocess

def ask_gemini(prompt):
    """
    Pont vers l'outil Gemini CLI (Fallback Cloud)
    Utilisé en cas de faiblesse du modèle local Ollama.
    """
    print("☁️ [GEMINI BRIDGE] Envoi de la requête via Gemini CLI...")
    try:
        # On passe le prompt en stdin à la commande gemini CLI
        result = subprocess.run(
            ['gemini'], 
            input=prompt.encode('utf-8'),
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=True
        )
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"Erreur Gemini CLI Bridge (code {e.returncode}): {e.stderr.decode('utf-8')}"
    except FileNotFoundError:
        return "Erreur Gemini CLI Bridge: commande 'gemini' introuvable."
