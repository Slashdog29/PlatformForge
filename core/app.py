"""
Orquestador principal de PlatformForge.
Carga configuración, sesión, servicios y gestiona el FeatureManager.
"""
from pathlib import Path
from typing import Dict, Optional

from core.config import Config
from core.feature_manager import FeatureManager
from core.events import EventDispatcher
from auth.session_store import load_session, save_session
from auth.session import Session

from services.base import ServiceManager
from services.apache import ApacheManager
from services.php import PhpManager
from services.mysql import MysqlManager
from services.mariadb import MariadbManager
from services.postgresql import PostgresqlManager
from services.node import NodeManager
from services.python_srv import PythonSrvManager


class App:
    def __init__(self):
        # Configuración
        self.config = Config()

        # Sesión (puede ser None si nunca se ha iniciado sesión)
        self.session: Optional[Session] = load_session()

        # Directorio de licencias
        license_dir = Path.home() / ".platformforge" / "licenses"
        license_dir.mkdir(parents=True, exist_ok=True)

        # Feature Manager (determina si Pro está activo)
        self.feature_manager = FeatureManager(self.session, license_dir)

        # Eventos (por ahora sin uso intensivo, pero disponible)
        self.events = EventDispatcher()

        # Servicios disponibles (instanciados bajo demanda)
        self._services: Dict[str, ServiceManager] = {
            "apache": ApacheManager(self),
            "php": PhpManager(self),
            "mysql": MysqlManager(self),
            "mariadb": MariadbManager(self),
            "postgresql": PostgresqlManager(self),
            "node": NodeManager(self),
            "python_srv": PythonSrvManager(self),
        }

    def get_service(self, name: str) -> ServiceManager:
        """Obtiene un servicio por su nombre."""
        service = self._services.get(name)
        if service is None:
            raise ValueError(f"Servicio '{name}' no encontrado.")
        return service

    def check_pro_feature(self, feature_name: str) -> bool:
        """Verifica si una característica Pro está habilitada."""
        return self.feature_manager.is_enabled(feature_name)

    def reload_feature_manager(self):
        """Recarga el estado de las licencias (útil después de instalar una nueva)."""
        license_dir = Path.home() / ".platformforge" / "licenses"
        self.feature_manager = FeatureManager(self.session, license_dir)

    def has_session(self) -> bool:
        return self.session is not None