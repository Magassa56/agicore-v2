import os

def apply_patch(file_path, new_code):
    """
    Applique physiquement un patch de code généré par l'IA.
    Sauvegarde d'abord une copie de secours (.bak) pour la sécurité.
    """
    if os.path.exists(file_path):
        os.rename(file_path, file_path + ".bak")
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_code)
    
    print(f"✅ [CODE WRITER] Fichier {file_path} mis à jour.")
