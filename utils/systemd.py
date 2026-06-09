"""
Manejo de servicios systemd.
"""
from utils.helpers import run_command


class SystemdManager:
    def start_service(self, name: str):
        run_command(["sudo", "systemctl", "start", name])

    def stop_service(self, name: str):
        run_command(["sudo", "systemctl", "stop", name])

    def restart_service(self, name: str):
        run_command(["sudo", "systemctl", "restart", name])

    def enable_service(self, name: str):
        run_command(["sudo", "systemctl", "enable", name])

    def is_active(self, name: str) -> str:
        import subprocess
        result = subprocess.run(
            ["systemctl", "is-active", name], capture_output=True, text=True
        )
        return result.stdout.strip()  # "active" o "inactive"