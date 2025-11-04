"""
Cryptographic utilities for MVP B2
Implements ECDSA (signatures), ECDH (key exchange), and AES-GCM (encryption)
"""

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidSignature
import os
import base64
from typing import Tuple, Optional


class CryptoManager:
    """
    Manages cryptographic operations for a node.
    Each node has one CryptoManager instance with its permanent keypair.
    """
    
    def __init__(self):
        """Generate a new ECDSA keypair for this node"""
        self.private_key = ec.generate_private_key(ec.SECP256R1())
        self.public_key = self.private_key.public_key()
        
    def get_public_key_bytes(self) -> bytes:
        """Export public key as bytes for transmission/storage"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
    
    def get_public_key_id(self) -> str:
        """Get a short ID for this public key (for use as node_id)"""
        pub_bytes = self.get_public_key_bytes()
        return base64.b64encode(pub_bytes[:32]).decode('utf-8')[:16]
    
    @staticmethod
    def load_public_key_from_bytes(key_bytes: bytes):
        """Load a public key from bytes"""
        return serialization.load_pem_public_key(key_bytes)
    
    # ===== ECDH: Key Exchange =====
    
    def derive_shared_secret(self, peer_public_key) -> bytes:
        """
        Perform ECDH key exchange to derive a shared secret.
        This secret can be used as an AES key.
        
        Args:
            peer_public_key: The other party's EC public key object
            
        Returns:
            32-byte shared secret suitable for AES-256
        """
        shared_key = self.private_key.exchange(ec.ECDH(), peer_public_key)
        
        # Use HKDF to derive a proper 32-byte key
        derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'communication-breakdown-aes-key',
        ).derive(shared_key)
        
        return derived_key
    
    # ===== AES-GCM: Authenticated Encryption =====
    
    @staticmethod
    def encrypt_message(shared_secret: bytes, plaintext: str, associated_data: str = "") -> dict:
        """
        Encrypt a message using AES-GCM.
        Provides both Confidentiality and Integrity/Authentication.
        
        Args:
            shared_secret: 32-byte key from ECDH
            plaintext: Message to encrypt
            associated_data: Optional plaintext metadata (e.g., sender_id) that must not be tampered
            
        Returns:
            dict with 'ciphertext' (base64), 'nonce' (base64), 'tag' (included in ciphertext)
        """
        aesgcm = AESGCM(shared_secret)
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        
        ad_bytes = associated_data.encode('utf-8')
        plaintext_bytes = plaintext.encode('utf-8')
        
        # encrypt_and_digest returns ciphertext with authentication tag appended
        ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, ad_bytes)
        
        return {
            'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
            'nonce': base64.b64encode(nonce).decode('utf-8'),
        }
    
    @staticmethod
    def decrypt_message(shared_secret: bytes, ciphertext_b64: str, nonce_b64: str, 
                       associated_data: str = "") -> Optional[str]:
        """
        Decrypt and verify an AES-GCM message.
        
        Args:
            shared_secret: 32-byte key from ECDH
            ciphertext_b64: Base64-encoded ciphertext (includes auth tag)
            nonce_b64: Base64-encoded nonce
            associated_data: Must match the AD used during encryption
            
        Returns:
            Decrypted plaintext string, or None if authentication fails
        """
        try:
            aesgcm = AESGCM(shared_secret)
            ciphertext = base64.b64decode(ciphertext_b64)
            nonce = base64.b64decode(nonce_b64)
            ad_bytes = associated_data.encode('utf-8')
            
            plaintext_bytes = aesgcm.decrypt(nonce, ciphertext, ad_bytes)
            return plaintext_bytes.decode('utf-8')
        except Exception as e:
            # Any exception (InvalidTag, decoding errors) means tampering or wrong key
            print(f"Decryption failed: {e}")
            return None
    
    # ===== ECDSA: Digital Signatures =====
    
    def sign_message(self, message: str) -> str:
        """
        Create an ECDSA signature for a message.
        Used for "Help" messages that must be publicly verifiable.
        
        Args:
            message: The message to sign
            
        Returns:
            Base64-encoded signature
        """
        message_bytes = message.encode('utf-8')
        signature = self.private_key.sign(
            message_bytes,
            ec.ECDSA(hashes.SHA256())
        )
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def verify_signature(public_key, message: str, signature_b64: str) -> bool:
        """
        Verify an ECDSA signature.
        
        Args:
            public_key: The signer's EC public key object
            message: The original message
            signature_b64: Base64-encoded signature
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            message_bytes = message.encode('utf-8')
            signature = base64.b64decode(signature_b64)
            
            public_key.verify(
                signature,
                message_bytes,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except InvalidSignature:
            return False
        except Exception as e:
            print(f"Signature verification error: {e}")
            return False
    
    # ===== Hash Functions (for integrity checks) =====
    
    @staticmethod
    def hash_data(data: str) -> str:
        """
        Compute SHA-256 hash of data.
        Used for integrity checks and as message IDs.
        
        Args:
            data: String to hash
            
        Returns:
            Hex-encoded hash (64 characters)
        """
        from hashlib import sha256
        return sha256(data.encode('utf-8')).hexdigest()


# ===== Utility Functions =====

def generate_message_id(sender_id: int, message_text: str, timestamp: str) -> str:
    """Generate a unique message ID using cryptographic hash"""
    data = f"{sender_id}:{message_text}:{timestamp}"
    return CryptoManager.hash_data(data)


def simulate_zkp_proof() -> str:
    """
    Simulate a Zero-Knowledge Proof for "Safe" messages.
    In reality, this would be a complex zk-SNARK proof.
    For simulation, we use a static validation string.
    
    Returns:
        A constant string that validates as a "valid ZKP"
    """
    return "SIMULATED_ZKP_V1_VALID"


def verify_zkp_proof(proof: str) -> bool:
    """
    Verify a simulated ZKP proof.
    
    Args:
        proof: The proof string to verify
        
    Returns:
        True if proof is the valid simulation string
    """
    return proof == "SIMULATED_ZKP_V1_VALID"
