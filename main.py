#!/usr/bin/env python3
"""
PlatformForge - Gestor de servidores locales para Arch Linux.
Si se ejecuta sin argumentos, abre la interfaz gráfica.
Si se pasan argumentos, funciona como CLI.
Además, verifica que las dependencias Python necesarias estén instaladas
y las instala automáticamente si faltan (solo en modo GUI).
"""
import sys
import subprocess
import os

REQUIRED_PYTHON_PACKAGES = {
    "typer": "typer",
    "rich": "rich",
    "cryptography": "cryptography",
    "httpx": "httpx",
    "keyring": "keyring",
    "psutil": "psutil",
    "PySide6": "PySide6",
    "packaging": "packaging",
}


def ensure_python_dependencies():
    """Verifica e instala las dependencias Python usando pip si es necesario."""
    missing = []
    for module, package in REQUIRED_PYTHON_PACKAGES.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    if missing:
        print("PlatformForge: Faltan paquetes de Python. Instalando automáticamente...")
        # Detectar si estamos dentro de un virtualenv
        in_venv = sys.prefix != sys.base_prefix
        cmd = [sys.executable, "-m", "pip", "install"]
        if not in_venv:
            cmd.append("--user")
        cmd.extend(missing)
        try:
            subprocess.run(cmd, check=True)
            print("Instalación completada. Reiniciando...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            print(f"No se pudieron instalar las dependencias: {e}")
            print("Por favor, instala manualmente con:")
            print(f"  pip install {' '.join(missing)}")
            sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        ensure_python_dependencies()
        from core.app import App
        from ui.gui import launch_gui
        app = App()
        launch_gui(app)
    else:
        import typer
        from core.app import App
        from ui.cli import register_commands
        app_cli = typer.Typer(name="platformforge")
        application = App()
        register_commands(app_cli, application)
        app_cli()