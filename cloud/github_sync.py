import os

def git_save(message="AGIcore auto checkpoint"):
    """
    Sauvegarde automatique GitHub (AGIcore Level 3)
    """
    print(f"📦 [GITHUB SYNC] Préparation du commit : {message}")
    os.system("git add .")
    os.system(f'git commit -m "{message}"')
    # Execution de la commande git push sur la branche main
    os.system("git push origin main")
    print("✅ [GITHUB SYNC] Push terminé.")
