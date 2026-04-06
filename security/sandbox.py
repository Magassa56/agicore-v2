def safe_execute(code_string):
    """🧪 Security Sandbox : Exécution isolée sans accès aux builtins dangereux."""
    # On vide les builtins pour empêcher l'accès aux fonctions système (os, open, etc)
    safe_globals = {"__builtins__": {}}
    
    try:
        exec(code_string, safe_globals)
        return "SAFE EXECUTION COMPLETED"
    except Exception as e:
        print(f"🛡️ [SANDBOX] Exécution BLOQUÉE : {e}")
        return f"BLOCKED: {str(e)}"
