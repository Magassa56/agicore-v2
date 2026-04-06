import os

# Liste des répertoires à ignorer pour ne pas saturer le contexte LLM
EXCLUDE_DIRS = {'.git', 'venv', '__pycache__', '.pytest_cache', '.ruff_cache', 'ops', 'docs'}
EXCLUDE_FILES = {'agicore_log.txt', 'nohup.out', 'trades.csv'}

def scan_codebase(root_dir="."):
    """
    Scanne la codebase d'AGIcore (uniquement les fichiers .py pertinents).
    """
    files = []
    for root, dirs, filenames in os.walk(root_dir):
        # Filtrage des répertoires exclus
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for f in filenames:
            if f.endswith(".py") and f not in EXCLUDE_FILES:
                files.append(os.path.join(root, f))
    return files

def read_file(path):
    """
    Lit le contenu d'un fichier source.
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def get_full_codebase_string():
    """
    Génère une chaîne unique contenant toute la structure du code actuel.
    """
    files = scan_codebase()
    codebase_str = ""
    for f in files:
        codebase_str += f"\n# --- FILE: {f} ---\n"
        codebase_str += read_file(f)
        codebase_str += "\n# --- END FILE ---\n"
    return codebase_str
