from cryptography.fernet import Fernet

# Génération d'une clé de session (à stocker secrètement en prod)
SESSION_KEY = Fernet.generate_key()
cipher = Fernet(SESSION_KEY)

def encrypt_data(data):
    """🔐 Chiffrement des communications inter-AGI."""
    return cipher.encrypt(data.encode()).decode()

def decrypt_data(token):
    """🔐 Déchiffrement sécurisé."""
    return cipher.decrypt(token.encode()).decode()
