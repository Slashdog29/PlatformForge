"""
Funciones auxiliares para ejecutar comandos del sistema.
"""
import subprocess
import sys
from typing import Optional


def run_command(cmd, cwd=None, shell=False, sudo=False, check=True):
    """Ejecuta un comando y muestra salida en tiempo real. Lanza excepción si falla."""
    if sudo and not isinstance(cmd, str):
        cmd = ["sudo"] + list(cmd)
    elif sudo and isinstance(cmd, str):
        cmd = "sudo " + cmd

    try:
        subprocess.run(cmd, cwd=cwd, shell=shell, check=check)
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando comando: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        raise