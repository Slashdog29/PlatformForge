"""
Gestor del servicio Apache (httpd).
"""
import subprocess
from services.base import ServiceManager
from utils.systemd import SystemdManager
from utils.package_manager import PackageManager
from utils.helpers import run_command


class ApacheManager(ServiceManager):
    SERVICE_NAME = "httpd"

    def __init__(self, app):
        super().__init__(app)
        self.systemd = SystemdManager()
        self.pkg = PackageManager()

    def install(self) -> bool:
        if self.is_installed():
            return True
        return self.pkg.install_package("apache")

    def uninstall(self) -> bool:
        return self.pkg.uninstall_package("apache")

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
            result = subprocess.run(["httpd", "-v"], capture_output=True, text=True, check=True)
            # primera línea: "Server version: Apache/2.4.57 (Unix)"
            return result.stdout.splitlines()[0].split(":")[1].strip()
        except Exception:
            return "desconocida"

    def switch_version(self, version: str) -> bool:
        raise NotImplementedError("Apache no admite múltiples versiones en Arch.")

    def repair(self) -> bool:
        """Comprueba la configuración y repara si es necesario."""
        try:
            subprocess.run(["sudo", "httpd", "-t"], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            # Configuración rota, intentar restaurar backup si existe
            print("Configuración de Apache dañada. Intentando restaurar...")
            # En Arch, tras instalar, podría existir /etc/httpd/conf/httpd.conf.pacsave
            backup = "/etc/httpd/conf/httpd.conf.pacsave"
            if Path(backup).exists():
                run_command(["sudo", "cp", backup, "/etc/httpd/conf/httpd.conf"])
                run_command(["sudo", "systemctl", "restart", self.SERVICE_NAME])
                return True
            else:
                print("No se encontró backup. Se sugiere reinstalar Apache.")
                return False

    def configure(self, **kwargs) -> bool:
        """Permite cambiar puerto (--port)"""
        if "port" in kwargs:
            port = kwargs["port"]
            conf_path = "/etc/httpd/conf/httpd.conf"
            # Reemplazar la línea Listen 80
            run_command(["sudo", "sed", "-i", f"s/^Listen .*/Listen {port}/", conf_path])
            self.restart()
            self.app.config.set("ports.apache", port)
            return True
        return False

    def is_installed(self) -> bool:
        return self.pkg.is_installed("apache")