import json
import os

PRODUCT_MEMORY_FILE = "memory/products.json"

def store_product(data):
    """🧠 Mémoire Produit : Enregistre une stratégie produit."""
    os.makedirs(os.path.dirname(PRODUCT_MEMORY_FILE), exist_ok=True)
    with open(PRODUCT_MEMORY_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

def load_products():
    """🧠 Chargement de l'historique des produits générés."""
    if not os.path.exists(PRODUCT_MEMORY_FILE):
        return []
    try:
        with open(PRODUCT_MEMORY_FILE, "r") as f:
            return [json.loads(line) for line in f.readlines()]
    except:
        return []
