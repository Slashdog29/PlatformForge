"""
Verificación offline de licencias usando clave pública Ed25519 incrustada.
"""
import json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature

# Clave pública incrustada (generada previamente, formato PEM)
# Esta clave debe ser reemplazada por la tuya. Puedes generar un par con:
#   from cryptography.hazmat.primitives.asymmetric import ed25519
#   key = ed25519.Ed25519PrivateKey.generate()
#   print(key.public_key().public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo).decode())
# Y la privada guardarla aparte para generator.py
PUBLIC_KEY_PEM = b"""
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEA7qK9rHrXxZ5pZY3N+bXq7x8V1sL4Lq6q4/7Ld3G9c8E=
-----END PUBLIC KEY-----
"""


def load_public_key():
    return serialization.load_pem_public_key(PUBLIC_KEY_PEM)


def verify_license(license_path: Path, github_user: str) -> bool:
    """Verifica un archivo de licencia y comprueba que corresponda al usuario."""
    try:
        with open(license_path, "r") as f:
            lic = json.load(f)
        signature = bytes.fromhex(lic["signature"])
        data = json.dumps(lic["data"]).encode()
        public_key = load_public_key()
        public_key.verify(signature, data)
        # Firma válida, comprobar usuario
        return lic["data"]["github_user"] == github_user
    except (InvalidSignature, KeyError, json.JSONDecodeError, FileNotFoundError):
        return False


def verify_all_licenses(license_dir: Path, github_user: str) -> bool:
    """Busca todos los archivos .key en el directorio y devuelve True si alguno coincide."""
    for lic_file in license_dir.glob("*.key"):
        if verify_license(lic_file, github_user):
            return True
    return False