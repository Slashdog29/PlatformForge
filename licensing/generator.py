#!/usr/bin/env python3
"""
Script para generar una licencia firmada para un patrocinador.
Requiere el archivo license_private.pem (clave privada Ed25519) en el mismo directorio.
"""
import json
import datetime
from pathlib import Path
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def generate_license(github_user: str, tier: str = "pro"):
    private_path = Path(__file__).parent / "license_private.pem"
    if not private_path.exists():
        raise FileNotFoundError("No se encontró license_private.pem. Genera una clave privada y colócala aquí.")

    with open(private_path, "rb") as f:
        private_key = load_pem_private_key(f.read(), password=None)

    if not isinstance(private_key, Ed25519PrivateKey):
        raise ValueError("La clave privada no es Ed25519.")

    data = {
        "github_user": github_user,
        "tier": tier,
        "issued": datetime.datetime.utcnow().isoformat(),
    }
    data_bytes = json.dumps(data).encode()
    signature = private_key.sign(data_bytes)

    lic = {
        "data": data,
        "signature": signature.hex(),
    }

    filename = f"{github_user}_license.key"
    with open(filename, "w") as f:
        json.dump(lic, f, indent=2)
    print(f"Licencia generada: {filename}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python generator.py <github_username> [tier]")
        sys.exit(1)
    user = sys.argv[1]
    tier = sys.argv[2] if len(sys.argv) > 2 else "pro"
    generate_license(user, tier)