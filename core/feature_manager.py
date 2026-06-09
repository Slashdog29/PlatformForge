"""
Gestor de características Pro basado en licencias offline.
"""
from pathlib import Path
from typing import Optional

from licensing.verifier import verify_all_licenses
from auth.session import Session


class FeatureManager:
    """
    Determina si las características Pro están habilitadas.
    Comprueba las licencias almacenadas y el usuario de la sesión.
    """

    # Características que siempre son gratuitas (lista no restrictiva, solo informativa)
    FREE_FEATURES = {
        "status", "php_switch", "apache_manage", "mysql_manage",
        "mariadb_manage", "postgresql_manage", "node_manage", "python_manage",
        "login", "license_install", "pro_status",
    }

    # Características que requieren licencia Pro
    PRO_FEATURES = {"update_all"}

    def __init__(self, session: Optional[Session], license_dir: Path):
        self.session = session
        self.license_dir = license_dir
        self.is_pro = False
        # Si hay sesión, buscamos licencias que coincidan con el usuario
        if session:
            github_user = session.github_user
        else:
            github_user = "anonymous"  # sin sesión, sin posibilidad de Pro
        self.is_pro = verify_all_licenses(license_dir, github_user)

    def is_enabled(self, feature_name: str) -> bool:
        """Retorna True si la característica está permitida (gratuita o Pro activa)."""
        if feature_name in self.FREE_FEATURES:
            return True
        if feature_name in self.PRO_FEATURES:
            return self.is_pro
        # Por defecto, las características no listadas se consideran gratuitas
        return True