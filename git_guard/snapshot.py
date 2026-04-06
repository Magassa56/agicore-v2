import os
from datetime import datetime

def create_snapshot():
    """📦 Git Auto Snapshot System : Création d'un point de restauration git avant modification."""
    name = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"📸 [GIT GUARD] Création du snapshot : {name}")
    
    os.system("git add .")
    os.system(f'git commit -m "AGIcore L8 Auto-Snapshot {name}"')
    
    print("✅ [GIT GUARD] Snapshot sauvegardé.")
