"""
Almacena y recupera la sesión del usuario localmente usando keyring y archivo JSON.
"""
import json
from pathlib import Path
from typing import Optional

import keyring
from auth.session import Session

SERVICE_NAME = "platformforge"
CONFIG_DIR = Path.home() / ".platformforge"
SESSION_FILE = CONFIG_DIR / "session.json"


def save_session(session: Session):
    """Guarda el token en keyring y el username en JSON."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # Almacenar token en keyring de forma segura
    keyring.set_password(SERVICE_NAME, session.github_user, session.access_token)
    # Guardar username en JSON (para cargar más rápido)
    data = {"github_user": session.github_user}
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)


def load_session() -> Optional[Session]:
    """Carga la sesión desde keyring y archivo JSON. Retorna None si no existe."""
    if not SESSION_FILE.exists():
        return None
    try:
        with open(SESSION_FILE, "r") as f:
            data = json.load(f)
        github_user = data.get("github_user")
        if not github_user:
            return None
        token = keyring.get_password(SERVICE_NAME, github_user)
        if token:
            return Session(github_user=github_user, access_token=token)
    except (json.JSONDecodeError, KeyError):
        pass
    return None