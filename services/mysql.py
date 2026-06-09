"""
Gestor de MySQL (realmente MariaDB en Arch).
"""
import subprocess
from services.base import ServiceManager
from utils.systemd import SystemdManager
from utils.package_manager import PackageManager
from utils.helpers import run_command


class MysqlManager(ServiceManager):
    SERVICE_NAME = "mariadb"  # Arch usa mariadb para MySQL

    def __init__(self, app):
        super().__init__(app)
        self.systemd = SystemdManager()
        self.pkg = PackageManager()

    def install(self) -> bool:
        if self.is_installed():
            return True
        self.pkg.install_package("mariadb")
        # Inicializar base de datos
        run_command(["sudo", "mysql_install_db", "--user=mysql", "--basedir=/usr", "--datadir=/var/lib/mysql"])
        # Habilitar e iniciar
        self.systemd.enable_service(self.SERVICE_NAME)
        self.start()
        return True

    def uninstall(self) -> bool:
        return self.pkg.uninstall_package("mariadb")

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
            result = subprocess.run(["mysql", "--version"], capture_output=True, text=True, check=True)
            return result.stdout.split(",")[0].split("Distrib")[1].strip()
        except Exception:
            return "desconocida"

    def switch_version(self, version: str) -> bool:
        raise NotImplementedError("No se admite cambio de versión para MySQL/MariaDB.")

    def repair(self) -> bool:
        run_command(["sudo", "mysqlcheck", "--all-databases", "--auto-repair"])
        return True

    def configure(self, **kwargs) -> bool:
        if "user" in kwargs and "password" in kwargs:
            # Crear usuario (conexión local)
            user = kwargs["user"]
            password = kwargs["password"]
            # Usamos socket, asumiendo acceso root sin pass inicial
            run_command(
                ["sudo", "mysql", "-u", "root", "-e",
                 f"CREATE USER IF NOT EXISTS '{user}'@'localhost' IDENTIFIED BY '{password}';"]
            )
            run_command(
                ["sudo", "mysql", "-u", "root", "-e",
                 f"GRANT ALL PRIVILEGES ON *.* TO '{user}'@'localhost' WITH GRANT OPTION; FLUSH PRIVILEGES;"]
            )
            return True
        return False

    def change_root_password(self, new_password: str):
        run_command(
            ["sudo", "mysqladmin", "-u", "root", "password", new_password]
        )

    def is_installed(self) -> bool:
        return self.pkg.is_installed("mariadb")