def validate_patch(file_path, new_code):
    """
    🛡️ SAFETY GUARD (Niveau 4)
    Empêche AGIcore de se détruire lui-même ou de générer du code vide.
    """
    checks = {
        "is_not_empty": len(new_code) > 10,
        "is_python": "def " in new_code or "import " in new_code or "class " in new_code,
        "no_critical_deletion": "main.py" not in file_path or ("main" in new_code and "run_sre_loop" in new_code),
        "basic_syntax": True # On pourrait ajouter un compile(new_code) ici pour tester la syntaxe
    }
    
    # Test de syntaxe basique via compile()
    try:
        compile(new_code, file_path, 'exec')
    except Exception as e:
        print(f"❌ [SAFETY GUARD] Erreur de syntaxe détectée : {e}")
        checks["basic_syntax"] = False

    passed = all(checks.values())
    if not passed:
        print(f"❌ [SAFETY GUARD] Patch REJETÉ pour {file_path}: {checks}")
    
    return passed
