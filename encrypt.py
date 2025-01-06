import hashlib
from base64 import b64decode, b64encode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

def get_enc_key(key:str):
    key_bytes = key.encode('utf-8')  # Ensure the key is a byte string
    sha256_hash = hashlib.sha256(key_bytes).digest()
    return sha256_hash

def decrypt(enc_key: bytes, enc_data: str) -> str:
    try:
        # Decode the base64 encoded data
        enc = b64decode(enc_data)

        # Define the AES-GCM nonce size (typically 12 bytes)
        nonce_size = 12

        # Split the nonce and ciphertext
        nonce, ciphertext = enc[:nonce_size], enc[nonce_size:]

        # Initialize AESGCM with the encryption key
        aesgcm = AESGCM(enc_key)

        # Decrypt the data
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)

        return plaintext.decode('utf-8')

    except Exception as e:
        raise RuntimeError("Decryption failed") from e
    
def encrypt(enc_key: bytes, enc_data: str) -> str:
    try:

        plaintext = enc_data.encode("utf-8")

        # Initialize AESGCM with the encryption key
        aesgcm = AESGCM(enc_key)

        # Define the AES-GCM nonce size (typically 12 bytes)
        nonce = os.urandom(12)

        cipertext = aesgcm.encrypt(nonce, plaintext, None)

        encrypted_data = nonce + cipertext

        # Decode the base64 encoded data
        b = b64encode(encrypted_data)

        return b.decode("utf-8")

    except Exception as e:
        raise RuntimeError("Encryption failed") from e
    