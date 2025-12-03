"""
Rapid Response - Cryptographic Utilities
ECDSA signature generation and verification using SECP256R1 curve
"""

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
import base64
import json


class CryptoUtils:
    """Cryptographic utilities for employee status signing/verification"""
    
    @staticmethod
    def generate_key_pair():
        """
        Generate an ECDSA key pair using SECP256R1 curve
        
        Returns:
            tuple: (private_key, public_key_pem)
        """
        private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
        
        # Serialize public key to PEM format
        public_key = private_key.public_key()
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode('utf-8')
        
        return private_key, public_key_pem
    
    @staticmethod
    def sign_status(private_key, employee_id: int, status: str, timestamp: str):
        """
        Sign a status update message
        
        Args:
            private_key: ECDSA private key object
            employee_id: Employee ID
            status: Status string ("Safe", "Needs Help", "Unknown")
            timestamp: ISO format timestamp
        
        Returns:
            str: Base64-encoded signature
        """
        # Create canonical message to sign
        message_data = {
            "employee_id": employee_id,
            "status": status,
            "timestamp": timestamp
        }
        message_bytes = json.dumps(message_data, sort_keys=True).encode('utf-8')
        
        # Sign with ECDSA
        signature = private_key.sign(
            message_bytes,
            ec.ECDSA(hashes.SHA256())
        )
        
        # Return base64-encoded signature
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def verify_signature(public_key_pem: str, employee_id: int, status: str, 
                        timestamp: str, signature_b64: str):
        """
        Verify a signed status update
        
        Args:
            public_key_pem: PEM-encoded public key
            employee_id: Employee ID
            status: Status string
            timestamp: ISO format timestamp
            signature_b64: Base64-encoded signature
        
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )
            
            # Reconstruct message
            message_data = {
                "employee_id": employee_id,
                "status": status,
                "timestamp": timestamp
            }
            message_bytes = json.dumps(message_data, sort_keys=True).encode('utf-8')
            
            # Decode signature
            signature = base64.b64decode(signature_b64)
            
            # Verify
            public_key.verify(
                signature,
                message_bytes,
                ec.ECDSA(hashes.SHA256())
            )
            
            return True
        
        except Exception as e:
            print(f"Signature verification failed: {e}")
            return False


# Example usage
if __name__ == "__main__":
    crypto = CryptoUtils()
    
    # Generate key pair
    private_key, public_key_pem = crypto.generate_key_pair()
    print("Generated key pair")
    print(f"Public Key:\n{public_key_pem}")
    
    # Sign a status update
    signature = crypto.sign_status(private_key, 1, "Safe", "2025-12-02T14:30:00Z")
    print(f"\nSignature: {signature[:50]}...")
    
    # Verify signature
    is_valid = crypto.verify_signature(
        public_key_pem, 1, "Safe", "2025-12-02T14:30:00Z", signature
    )
    print(f"\nSignature valid: {is_valid}")
    
    # Try tampering
    is_valid_tampered = crypto.verify_signature(
        public_key_pem, 1, "Needs Help", "2025-12-02T14:30:00Z", signature
    )
    print(f"Tampered signature valid: {is_valid_tampered}")
