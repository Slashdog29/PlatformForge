"""
Gestor de entornos Python para desarrollo local.
"""
import subprocess
from services.base import ServiceManager
from utils.package_manager import PackageManager
from utils.helpers import run_command


class PythonSrvManager(ServiceManager):
    def __init__(self, app):
        super().__init__(app)
        self.pkg = PackageManager()

    def install(self) -> bool:
        if self.is_installed():
            return True
        self.pkg.install_package("python")
        self.pkg.install_package("python-pip")
        # Instalar uvicorn/gunicorn globalmente (opcional)
        run_command(["sudo", "pip", "install", "uvicorn", "gunicorn"])
        return True

    def uninstall(self) -> bool:
        return self.pkg.uninstall_package("python")

    def start(self) -> bool:
        raise NotImplementedError("Use start_project para lanzar servidores Python.")

    def stop(self) -> bool:
        raise NotImplementedError

    def restart(self) -> bool:
        raise NotImplementedError

    def status(self) -> str:
        return "active" if self.is_installed() else "inactive"

    def get_version(self) -> str:
        try:
            result = subprocess.run(["python", "--version"], capture_output=True, text=True, check=True)
            return result.stdout.split()[1]
        except Exception:
            return "desconocida"

    def switch_version(self, version: str) -> bool:
        # pyenv podría usarse
        print("Use pyenv para cambiar versiones de Python.")
        return False

    def repair(self) -> bool:
        self.pkg.install_package("python", reinstall=True)
        return True

    def start_project(self, project_path: str, app_module: str, server: str = "uvicorn"):
        """Crea un venv si no existe, instala dependencias y lanza el servidor."""
        import os
        venv_dir = os.path.join(project_path, "venv")
        if not os.path.exists(venv_dir):
            run_command(["python", "-m", "venv", "venv"], cwd=project_path)
        # Activar e instalar (según requirements.txt)
        pip = os.path.join(venv_dir, "bin", "pip")
        if os.path.exists(os.path.join(project_path, "requirements.txt")):
            run_command([pip, "install", "-r", "requirements.txt"], cwd=project_path)
        # Lanzar
        if server == "uvicorn":
            run_command([os.path.join(venv_dir, "bin", "uvicorn"), f"{app_module}:app", "--reload"], cwd=project_path)
        elif server == "gunicorn":
            run_command([os.path.join(venv_dir, "bin", "gunicorn"), f"{app_module}:app"], cwd=project_path)
        else:
            print(f"Servidor '{server}' no soportado.")

    def is_installed(self) -> bool:
        return self.pkg.is_installed("python")

    def configure(self, **kwargs) -> bool:
        return False