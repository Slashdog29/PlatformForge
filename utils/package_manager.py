"""
Gestor de paquetes de Arch Linux (pacman + AUR helpers).
"""
import subprocess
from utils.helpers import run_command


class PackageManager:
    def is_installed(self, pkg_name: str) -> bool:
        result = subprocess.run(["pacman", "-Q", pkg_name], capture_output=True)
        return result.returncode == 0

    def install_package(self, pkg_name: str, reinstall: bool = False):
        """Instala un paquete desde repos oficiales."""
        cmd = ["sudo", "pacman", "-S", "--noconfirm"]
        if reinstall:
            cmd.append("--overwrite=*")
        cmd.append(pkg_name)
        run_command(cmd)

    def uninstall_package(self, pkg_name: str):
        run_command(["sudo", "pacman", "-R", "--noconfirm", pkg_name])

    def install_aur_package(self, pkg_name: str, reinstall: bool = False):
        """Instala un paquete desde AUR usando yay o paru."""
        helper = self._detect_aur_helper()
        if helper is None:
            raise RuntimeError("No se encontró yay, paru ni trizen. Instala uno manualmente.")
        cmd = [helper, "-S", "--noconfirm"]
        if reinstall:
            cmd.append("--overwrite=*")
        cmd.append(pkg_name)
        run_command(cmd)

    def update_system(self):
        run_command(["sudo", "pacman", "-Syu", "--noconfirm"])

    def _detect_aur_helper(self):
        for helper in ["yay", "paru", "trizen"]:
            if subprocess.run(["which", helper], capture_output=True).returncode == 0:
                return helper
        return None