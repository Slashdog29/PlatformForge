"""
Interfaz abstracta para todos los gestores de servicios.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import App  # solo para tipado, evita import circular


class ServiceManager(ABC):
    def __init__(self, app: "App"):
        self.app = app

    @abstractmethod
    def install(self) -> bool:
        ...

    @abstractmethod
    def uninstall(self) -> bool:
        ...

    @abstractmethod
    def start(self) -> bool:
        ...

    @abstractmethod
    def stop(self) -> bool:
        ...

    @abstractmethod
    def restart(self) -> bool:
        ...

    @abstractmethod
    def status(self) -> str:
        ...

    @abstractmethod
    def get_version(self) -> str:
        ...

    @abstractmethod
    def switch_version(self, version: str) -> bool:
        ...

    @abstractmethod
    def repair(self) -> bool:
        ...

    @abstractmethod
    def configure(self, **kwargs) -> bool:
        ...

    def is_installed(self) -> bool:
        """Método concreto opcional: comprobar si el paquete está instalado."""
        return False