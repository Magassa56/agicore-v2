import chromadb
from chromadb.config import Settings
import os

# Dossier de stockage persistant pour la Vector DB
DB_PATH = "memory/vector_db/chroma_storage"
os.makedirs(DB_PATH, exist_ok=True)

class SemanticMemory:
    def __init__(self):
        # Initialisation du client ChromaDB avec persistance
        self.client = chromadb.PersistentClient(path=DB_PATH)
        # Création ou récupération de la collection principale
        self.collection = self.client.get_or_create_collection(
            name="agicore_experience",
            metadata={"description": "Mémoire sémantique des actions et évolutions d'AGIcore"}
        )

    def add_memory(self, text, metadata=None, doc_id=None):
        """
        🧠 Ajoute un souvenir à la mémoire sémantique.
        """
        if not doc_id:
            import time
            doc_id = f"mem_{int(time.time() * 1000)}"
            
        print(f"🧠 [SEMANTIC MEMORY] Ajout d'un nouveau souvenir : {doc_id}")
        self.collection.add(
            documents=[text],
            metadatas=[metadata] if metadata else [{"type": "general"}],
            ids=[doc_id]
        )

    def query_memory(self, query_text, n_results=3):
        """
        🔍 Recherche les souvenirs les plus proches sémantiquement.
        """
        print(f"🔍 [SEMANTIC MEMORY] Recherche de contexte pour : '{query_text[:50]}...'")
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

# Instance globale pour un accès facile
memory_engine = SemanticMemory()
