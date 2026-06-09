"""
Gestor de PostgreSQL.
"""
import subprocess
from services.base import ServiceManager
from utils.systemd import SystemdManager
from utils.package_manager import PackageManager
from utils.helpers import run_command


class PostgresqlManager(ServiceManager):
    SERVICE_NAME = "postgresql"

    def __init__(self, app):
        super().__init__(app)
        self.systemd = SystemdManager()
        self.pkg = PackageManager()

    def install(self) -> bool:
        if self.is_installed():
            return True
        self.pkg.install_package("postgresql")
        # Inicializar cluster
        run_command(["sudo", "-u", "postgres", "initdb", "-D", "/var/lib/postgres/data"])
        self.systemd.enable_service(self.SERVICE_NAME)
        self.start()
        return True

    def uninstall(self) -> bool:
        return self.pkg.uninstall_package("postgresql")

    def start(self) -> bool:
        return self.systemd.start_service(self.SERVICE_NAME)

    def stop(self) -> bool:
        return self.systemd.stop_service(self.SERVICE_NAME)

    def restart(self) -> bool:
        return self.systemd.restart_service(self.SERVICE_NAME)

    def status(self) -> str:
        return self.systemd.is_active(self.SERVICE_NAME)

    def get_version(self) -> str:
        try:
            result = subprocess.run(["postgres", "--version"], capture_output=True, text=True, check=True)
            return result.stdout.split()[-1]
        except Exception:
            return "desconocida"

    def switch_version(self, version: str) -> bool:
        raise NotImplementedError("PostgreSQL no admite múltiples versiones simultáneas en este contexto.")

    def repair(self) -> bool:
        # pg_ctlcheck no es reparador, pero podemos sugerir reinicio
        print("Para reparar, se reiniciará el servicio.")
        self.restart()
        return True

    def configure(self, **kwargs) -> bool:
        if "password" in kwargs:
            password = kwargs["password"]
            # Cambiar contraseña del usuario postgres
            run_command(
                ["sudo", "-u", "postgres", "psql", "-c",
                 f"ALTER USER postgres PASSWORD '{password}';"]
            )
            return True
        return False

    def is_installed(self) -> bool:
        return self.pkg.is_installed("postgresql")