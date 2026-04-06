
import os
import logging
from google.cloud import secretmanager
from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Generate or load an encryption key
# In a real production system, this key should be managed securely (e.g., stored in a KMS)
# For this example, we'll generate it and assume it's securely distributed.
ENCRYPTION_KEY = Fernet.generate_key()
cipher_suite = Fernet(ENCRYPTION_KEY)

def get_secret(project_id, secret_id, version_id="latest"):
    """
    Retrieves a secret from Google Secret Manager and logs the access.
    """
    try:
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
        response = client.access_secret_version(request={"name": name})
        secret_payload = response.payload.data.decode("UTF-8")
        
        logging.info(f"Accessed secret: {secret_id}")
        return secret_payload
    except Exception as e:
        logging.error(f"Failed to retrieve secret {secret_id}: {e}")
        raise

def encrypt_data(data):
    """
    Encrypts data using the in-memory key.
    """
    if not isinstance(data, bytes):
        data = data.encode('utf-8')
    return cipher_suite.encrypt(data)

def decrypt_data(encrypted_data):
    """
    Decrypts data using the in-memory key.
    """
    return cipher_suite.decrypt(encrypted_data).decode('utf-8')

def is_kill_switch_active(project_id, secret_id="trading_kill_switch"):
    """
    Checks if the trading kill switch is active.
    The secret's value is expected to be 'true' or 'false'.
    """
    try:
        kill_switch_value = get_secret(project_id, secret_id)
        return kill_switch_value.lower() == 'true'
    except Exception:
        # If the kill switch secret is not found or fails to load,
        # we default to a "fail-safe" position and halt trading.
        logging.error("CRITICAL: Kill switch status could not be determined. Halting all trading activity.")
        return True

class SecureAPICredentials:
    def __init__(self, project_id, key_id_secret, secret_key_secret):
        self._project_id = project_id
        self._key_id_secret = key_id_secret
        self._secret_key_secret = secret_key_secret
        
        self._encrypted_api_key = None
        self._encrypted_secret_key = None
        
        self._load_and_encrypt_credentials()

    def _load_and_encrypt_credentials(self):
        """

        Loads the API credentials from the secret manager and encrypts them in memory.
        """
        api_key = get_secret(self._project_id, self._key_id_secret)
        secret_key = get_secret(self._project_id, self._secret_key_secret)
        
        self._encrypted_api_key = encrypt_data(api_key)
        self._encrypted_secret_key = encrypt_data(secret_key)
        
        logging.info("API credentials loaded and encrypted in memory.")

    @property
    def api_key(self):
        """
        Decrypts and returns the API key on demand.
        """
        return decrypt_data(self._encrypted_api_key)
        
    @property
    def secret_key(self):
        """
        Decrypts and returns the secret key on demand.
        """
        return decrypt_data(self._encrypted_secret_key)

    def __enter__(self):
        # This allows using the credentials in a 'with' statement, ensuring they are securely handled
        # and decrypted only for the duration of the block.
        return {
            "api_key": self.api_key,
            "secret_key": self.secret_key,
        }

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Here you could add logic to clear the decrypted keys from memory if needed,
        # although Python's garbage collection will handle it.
        # For extreme security, you could overwrite the variables.
        pass

if __name__ == '__main__':
    # This is an example of how to use the SecureAPICredentials class.
    # You would need to set your GCP Project ID.
    # In a real application, you wouldn't hardcode this.
    # It might come from an environment variable that is NOT the secret itself,
    # but rather configuration for accessing the secrets.
    
    GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
    if not GCP_PROJECT_ID:
        print("Please set the GCP_PROJECT_ID environment variable to run this example.")
    else:
        # Example usage:
        # Create secrets in your GCP project named 'alpaca_api_key_id' and 'alpaca_secret_key'
        print("Checking kill switch status...")
        if is_kill_switch_active(GCP_PROJECT_ID):
            print("Kill switch is ACTIVE. No trading allowed.")
        else:
            print("Kill switch is INACTIVE. Trading is allowed.")

            print("
Loading credentials securely...")
            # The credentials will be fetched from Secret Manager and encrypted in memory upon instantiation.
            secure_creds = SecureAPICredentials(
                project_id=GCP_PROJECT_ID,
                key_id_secret="alpaca_api_key_id",
                secret_key_secret="alpaca_secret_key"
            )

            # The credentials are only decrypted when accessed.
            print(f"Decrypted API Key on-demand: {secure_creds.api_key[:4]}... (truncated)")
            print(f"Decrypted Secret Key on-demand: {secure_creds.secret_key[:4]}... (truncated)")

            # Example of using the credentials in a secure context
            with secure_creds as creds:
                print("
Using credentials within a secure context:")
                print(f"  API Key: {creds['api_key'][:4]}...")
                print(f"  Secret Key: {creds['secret_key'][:4]}...")
            
            print("
Exited secure context.")

