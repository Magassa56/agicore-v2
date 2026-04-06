def run_in_sandbox(code_str):
    """
    🧪 Execution Sandbox (Level 8)
    Exécute un patch de code de manière isolée (dans un scope global vierge).
    """
    sandbox_globals = {}
    
    try:
        print("🧪 [SANDBOX] Exécution du code dans l'environnement isolé...")
        exec(code_str, sandbox_globals)
        print("✅ [SANDBOX] Exécution réussie.")
        return sandbox_globals
    except Exception as e:
        print(f"❌ [SANDBOX] Erreur d'exécution : {e}")
        return str(e)
