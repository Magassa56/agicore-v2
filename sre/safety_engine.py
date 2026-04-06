def validate_patch(patch: str) -> bool:
    """
    🧯 SRE Safety Engine : Anti-catastrophe.
    Filtre les mots-clés destructeurs avant toute exécution dynamique.
    """
    dangerous_keywords = [
        "os.system",
        "rm -rf",
        "subprocess",
        "format",
        "del memory",
        "overwrite git history",
        "sys.exit",
        "exec", # On ne veut pas qu'un patch fasse un exec dans un exec
        "eval"
    ]

    for keyword in dangerous_keywords:
        if keyword in patch:
            print(f"❌ [SAFETY ENGINE] Mot-clé dangereux détecté : '{keyword}'")
            return False

    print("✅ [SAFETY ENGINE] Patch validé (aucun mot-clé dangereux).")
    return True
