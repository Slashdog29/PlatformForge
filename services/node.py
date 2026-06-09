"""
Gestor de Node.js y npm, con soporte opcional de nvm.
"""
import subprocess
from services.base import ServiceManager
from utils.package_manager import PackageManager
from utils.helpers import run_command


class NodeManager(ServiceManager):
    def __init__(self, app):
        super().__init__(app)
        self.pkg = PackageManager()

    def install(self) -> bool:
        if self.is_installed():
            return True
        self.pkg.install_package("nodejs")
        self.pkg.install_package("npm")
        return True

    def uninstall(self) -> bool:
        return self.pkg.uninstall_package("nodejs")

    def start(self) -> bool:
        raise NotImplementedError("Node no es un servicio systemd; use start_project.")

    def stop(self) -> bool:
        raise NotImplementedError

    def restart(self) -> bool:
        raise NotImplementedError

    def status(self) -> str:
        return "active" if self.is_installed() else "inactive"

    def get_version(self) -> str:
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception:
            return "desconocida"

    def switch_version(self, version: str) -> bool:
        # Si nvm está instalado, usarlo
        try:
            subprocess.run(["nvm", "use", version], shell=True, check=True)
            return True
        except:
            print("nvm no está instalado. Se recomienda instalar nvm para gestionar versiones.")
            return False

    def repair(self) -> bool:
        self.pkg.install_package("nodejs", reinstall=True)
        return True

    def start_project(self, project_path: str, script: str = "dev"):
        """Ejecuta npm run <script> en el directorio indicado."""
        run_command(["npm", "run", script], cwd=project_path, shell=True)

    def is_installed(self) -> bool:
        return self.pkg.is_installed("nodejs")

    def configure(self, **kwargs) -> bool:
        return False