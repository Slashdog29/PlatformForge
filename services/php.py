"""
Gestor de PHP, incluyendo múltiples versiones desde AUR.
"""
import subprocess
from pathlib import Path
from services.base import ServiceManager
from utils.package_manager import PackageManager
from utils.helpers import run_command


class PhpManager(ServiceManager):
    AUR_PACKAGES = {
        "7.4": "php74",
        "8.1": "php81",
        "8.2": "php82",
        "8.3": "php83",
    }

    def __init__(self, app):
        super().__init__(app)
        self.pkg = PackageManager()

    # ---------- Métodos obligatorios de ServiceManager ----------
    def install(self) -> bool:
        self.pkg.install_package("php")
        self.pkg.install_package("php-apache")
        return True

    def uninstall(self) -> bool:
        return self.pkg.uninstall_package("php")

    def start(self) -> bool:
        raise NotImplementedError("PHP no es un servicio independiente; se usa con Apache.")

    def stop(self) -> bool:
        raise NotImplementedError

    def restart(self) -> bool:
        raise NotImplementedError

    def status(self) -> str:
        return "active" if self.is_installed() else "inactive"

    def get_version(self) -> str:
        try:
            result = subprocess.run(["php", "-v"], capture_output=True, text=True, check=True)
            # Ejemplo de salida: "PHP 8.2.15 (cli)..."
            return result.stdout.splitlines()[0].split()[1]
        except Exception:
            return "desconocida"

    def switch_version(self, version: str) -> bool:
        """Cambia la versión activa de PHP CLI y el módulo de Apache."""
        pkg = self.AUR_PACKAGES.get(version)
        if not pkg:
            print(f"Versión {version} no disponible. Disponibles: {list(self.AUR_PACKAGES.keys())}")
            return False

        # Instalar si falta
        if not self.pkg.is_installed(pkg):
            print(f"Instalando PHP {version} desde AUR...")
            self.install_version(version)

        # Cambiar enlace simbólico de php
        run_command(["sudo", "ln", "-sf", f"/usr/bin/php{version.replace('.', '')}", "/usr/bin/php"])

        # Copiar módulo de Apache
        src = f"/usr/lib/httpd/modules/libphp{version.replace('.', '')}.so"
        if Path(src).exists():
            run_command(["sudo", "cp", src, "/usr/lib/httpd/modules/libphp.so"])
        else:
            print(f"Advertencia: no se encontró {src}. Asegúrate de instalar el paquete php{version}-apache.")

        # Enlazar php.ini adecuado
        ini_dir = f"/etc/php{version.replace('.', '')}"
        if Path(ini_dir).exists():
            run_command(["sudo", "ln", "-sf", f"{ini_dir}/php.ini", "/etc/php/php.ini"])

        # Reiniciar Apache
        apache = self.app.get_service("apache")
        apache.restart()

        # Emitir evento
        self.app.events.dispatch("php.version_changed", version=version)
        return True

    def repair(self) -> bool:
        """Reinstala la versión actual de PHP."""
        current = self.get_version()
        for ver, pkg in self.AUR_PACKAGES.items():
            if ver in current:
                self.pkg.install_aur_package(pkg, reinstall=True)
                return True
        # Si no coincide, reinstalar el paquete base
        self.pkg.install_package("php", reinstall=True)
        return True

    def configure(self, **kwargs) -> bool:
        """No hay configuración específica en este gestor."""
        return False

    def is_installed(self) -> bool:
        return self.pkg.is_installed("php")

    # ---------- Métodos auxiliares propios ----------
    def get_available_versions(self) -> list:
        return list(self.AUR_PACKAGES.keys())

    def is_version_installed(self, version: str) -> bool:
        pkg = self.AUR_PACKAGES.get(version)
        if not pkg:
            return False
        return self.pkg.is_installed(pkg)

    def install_version(self, version: str):
        pkg = self.AUR_PACKAGES.get(version)
        if not pkg:
            raise ValueError(f"Versión {version} no soportada.")
        self.pkg.install_aur_package(pkg)
        # Módulo Apache
        self.pkg.install_aur_package(f"{pkg}-apache")