"""
VAPID Key Generator for Web Push Notifications.
Generates URL-safe base64 encoded P-256 (prime256v1) elliptic curve key pairs for VAPID.
"""
import base64
import os
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def generate_vapid_keypair():
    """Generates standard VAPID public/private key pair (P-256)."""
    private_key = ec.generate_private_key(ec.SECP256R1())
    private_value = private_key.private_numbers().private_value
    priv_bytes = private_value.to_bytes(32, 'big')
    priv_b64 = base64.urlsafe_b64encode(priv_bytes).rstrip(b'=').decode('utf-8')

    public_key = private_key.public_key()
    pub_bytes = public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
    pub_b64 = base64.urlsafe_b64encode(pub_bytes).rstrip(b'=').decode('utf-8')

    return priv_b64, pub_b64


if __name__ == '__main__':
    priv, pub = generate_vapid_keypair()
    print("=" * 65)
    print("      VAPID Keys Generated Successfully!")
    print("=" * 65)
    print(f"VAPID_PUBLIC_KEY={pub}")
    print(f"VAPID_PRIVATE_KEY={priv}")
    print("VAPID_ADMIN_EMAIL=mailto:admin@surronbikesandparts.shop")
    print("=" * 65)
    print("\nCopy and paste these 3 lines into your .env file.")
