import vertexai
from vertexai.generative_models import GenerativeModel

# Configuration de votre projet
PROJECT_ID = "ace-forest-420208"
LOCATION = "europe-west9" # Région recommandée par défaut

try:
    print("Initialisation de l'Agent...")
    # Connexion à Vertex AI
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    # Choix du modèle (le cerveau de l'agent). Ici Gemini 1.5 Flash, rapide et performant
    model = GenerativeModel(model_name="gemini-1.5-flash-001")
    
    print("Envoi du message au cerveau (Vertex AI)...")
    # Requête envoyée à l'agent
    response = model.generate_content("Bonjour ! Tu es le premier agent du système agicore. Présente-toi en une phrase.")
    
    # Affichage de la réponse
    print("\n🤖 Réponse de l'Agent :")
    print(response.text)

except Exception as e:
    print(f"\n❌ Aïe, une erreur est survenue : {e}")