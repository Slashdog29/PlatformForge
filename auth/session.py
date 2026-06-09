"""
Define la estructura de una sesión de usuario.
"""
from dataclasses import dataclass


@dataclass
class Session:
    github_user: str
    access_token: str