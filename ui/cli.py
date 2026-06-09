"""
Interfaz de línea de comandos (CLI) usando Typer y Rich.
"""
from typing import Optional
import shutil
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from core.app import App
from auth.github_oauth import start_flow
from auth.session_store import save_session, load_session

console = Console()


def status(app: App):
    """Muestra el estado de todos los servicios."""
    table = Table(title="Estado de Servicios")
    table.add_column("Servicio", style="cyan")
    table.add_column("Instalado", style="green")
    table.add_column("Estado", style="yellow")
    table.add_column("Versión", style="magenta")

    services = ["apache", "php", "mysql", "mariadb", "postgresql", "node", "python_srv"]
    for name in services:
        srv = app.get_service(name)
        installed = "Sí" if srv.is_installed() else "No"
        try:
            estado = srv.status()
        except NotImplementedError:
            estado = "N/A"
        version = srv.get_version() if installed == "Sí" else "-"
        table.add_row(name, installed, estado, version)

    console.print(table)


def php_list(app: App):
    """Lista versiones de PHP disponibles."""
    php = app.get_service("php")
    current = php.get_version()
    avail = php.get_available_versions()
    console.print(f"Versión activa: [bold]{current}[/bold]")
    console.print("Versiones disponibles (AUR):")
    for v in avail:
        mark = " *" if v in current else ""
        console.print(f"  {v}{mark}")


def php_switch(app: App, version: str):
    """Cambia a una versión específica de PHP."""
    php = app.get_service("php")
    success = php.switch_version(version)
    if success:
        console.print(f"[green]Ahora usando PHP {version}[/green]")
    else:
        console.print("[red]No se pudo cambiar de versión.[/red]")


def php_version(app: App):
    """Muestra la versión de PHP activa."""
    console.print(app.get_service("php").get_version())


def apache_start(app: App):
    app.get_service("apache").start()
    console.print("[green]Apache iniciado.[/green]")


def apache_stop(app: App):
    app.get_service("apache").stop()
    console.print("[yellow]Apache detenido.[/yellow]")


def apache_restart(app: App):
    app.get_service("apache").restart()
    console.print("[green]Apache reiniciado.[/green]")


def apache_repair(app: App):
    if app.get_service("apache").repair():
        console.print("[green]Apache reparado.[/green]")
    else:
        console.print("[red]No se pudo reparar Apache.[/red]")


def apache_configure(app: App, port: int):
    app.get_service("apache").configure(port=port)
    console.print(f"[green]Apache ahora escucha en el puerto {port}.[/green]")


def mysql_start(app: App):
    app.get_service("mysql").start()
    console.print("[green]MySQL iniciado.[/green]")


def mysql_stop(app: App):
    app.get_service("mysql").stop()
    console.print("[yellow]MySQL detenido.[/yellow]")


def mysql_restart(app: App):
    app.get_service("mysql").restart()
    console.print("[green]MySQL reiniciado.[/green]")


def mysql_repair(app: App):
    app.get_service("mysql").repair()
    console.print("[green]MySQL reparado.[/green]")


def mysql_root_password(app: App, new_password: str):
    app.get_service("mysql").change_root_password(new_password)
    console.print("[green]Contraseña de root cambiada.[/green]")


def mariadb_start(app: App):
    app.get_service("mariadb").start()


def mariadb_stop(app: App):
    app.get_service("mariadb").stop()


def mariadb_restart(app: App):
    app.get_service("mariadb").restart()


def mariadb_repair(app: App):
    app.get_service("mariadb").repair()


def postgresql_start(app: App):
    app.get_service("postgresql").start()


def postgresql_stop(app: App):
    app.get_service("postgresql").stop()


def postgresql_restart(app: App):
    app.get_service("postgresql").restart()


def postgresql_repair(app: App):
    app.get_service("postgresql").repair()


def postgresql_configure(app: App, password: str):
    app.get_service("postgresql").configure(password=password)
    console.print("[green]Contraseña de postgres actualizada.[/green]")


def login(app: App):
    """Inicia sesión con GitHub (solo una vez)."""
    if app.session:
        console.print("Ya hay una sesión activa. ¿Desea reemplazarla? (s/n)")
        r = input().lower()
        if r != "s":
            return
    console.print("Abriendo navegador para autenticación con GitHub...")
    try:
        session = start_flow()
        save_session(session)
        app.session = session
        app.reload_feature_manager()
        console.print(f"[green]Sesión iniciada como {session.github_user}.[/green]")
    except Exception as e:
        console.print(f"[red]Error durante el login: {e}[/red]")


def license_install(app: App, file: str):
    """Instala un archivo de licencia Pro."""
    src = Path(file)
    if not src.exists():
        console.print("[red]Archivo no encontrado.[/red]")
        return
    dest_dir = Path.home() / ".platformforge" / "licenses"
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dest_dir)
    # Recargar el FeatureManager para activar la licencia
    app.reload_feature_manager()
    console.print("[green]Licencia instalada. Verifique con 'pro status'.[/green]")


def pro_status(app: App):
    """Muestra el estado de la licencia Pro."""
    if app.feature_manager.is_pro:
        user = app.session.github_user if app.session else "desconocido"
        console.print(f"[green]Licencia PRO activa para {user}.[/green]")
    else:
        console.print("[yellow]Versión gratuita. Patrocina para funciones PRO.[/yellow]")


def update_all(app: App):
    """(Pro) Actualiza todos los servicios a la última versión."""
    if not app.check_pro_feature("update_all"):
        console.print("[red]Esta función requiere una licencia Pro. Considera patrocinar el proyecto.[/red]")
        return
    console.print("Actualizando sistema y servicios...")
    from utils.package_manager import PackageManager
    pm = PackageManager()
    pm.update_system()
    # Reinstalar servicios clave
    for srv_name in ["apache", "php", "mariadb", "postgresql", "nodejs"]:
        pm.install_package(srv_name, reinstall=True)
    console.print("[green]Actualización completada.[/green]")


def register_commands(app_typer: typer.Typer, app: App):
    """Registra todos los comandos en la app Typer."""

    @app_typer.command()
    def status_cmd():
        status(app)

    # PHP
    php_typer = typer.Typer()
    app_typer.add_typer(php_typer, name="php", help="Gestión de PHP")

    @php_typer.command("list")
    def php_list_cmd():
        php_list(app)

    @php_typer.command("switch")
    def php_switch_cmd(version: str = typer.Argument(..., help="Versión de PHP (ej. 8.2)")):
        php_switch(app, version)

    @php_typer.command("version")
    def php_version_cmd():
        php_version(app)

    # Apache
    apache_typer = typer.Typer()
    app_typer.add_typer(apache_typer, name="apache", help="Gestión de Apache")

    @apache_typer.command("start")
    def apache_start_cmd():
        apache_start(app)

    @apache_typer.command("stop")
    def apache_stop_cmd():
        apache_stop(app)

    @apache_typer.command("restart")
    def apache_restart_cmd():
        apache_restart(app)

    @apache_typer.command("repair")
    def apache_repair_cmd():
        apache_repair(app)

    @apache_typer.command("configure")
    def apache_configure_cmd(port: int = typer.Option(80, help="Nuevo puerto")):
        apache_configure(app, port)

    # MySQL
    mysql_typer = typer.Typer()
    app_typer.add_typer(mysql_typer, name="mysql", help="Gestión de MySQL")

    @mysql_typer.command("start")
    def mysql_start_cmd():
        mysql_start(app)

    @mysql_typer.command("stop")
    def mysql_stop_cmd():
        mysql_stop(app)

    @mysql_typer.command("restart")
    def mysql_restart_cmd():
        mysql_restart(app)

    @mysql_typer.command("repair")
    def mysql_repair_cmd():
        mysql_repair(app)

    @mysql_typer.command("root-password")
    def mysql_root_password_cmd(new_password: str = typer.Argument(..., help="Nueva contraseña")):
        mysql_root_password(app, new_password)

    # MariaDB
    mariadb_typer = typer.Typer()
    app_typer.add_typer(mariadb_typer, name="mariadb", help="Gestión de MariaDB")

    @mariadb_typer.command("start")
    def mariadb_start_cmd():
        mariadb_start(app)

    @mariadb_typer.command("stop")
    def mariadb_stop_cmd():
        mariadb_stop(app)

    @mariadb_typer.command("restart")
    def mariadb_restart_cmd():
        mariadb_restart(app)

    @mariadb_typer.command("repair")
    def mariadb_repair_cmd():
        mariadb_repair(app)

    # PostgreSQL
    pg_typer = typer.Typer()
    app_typer.add_typer(pg_typer, name="postgresql", help="Gestión de PostgreSQL")

    @pg_typer.command("start")
    def pg_start_cmd():
        postgresql_start(app)

    @pg_typer.command("stop")
    def pg_stop_cmd():
        postgresql_stop(app)

    @pg_typer.command("restart")
    def pg_restart_cmd():
        postgresql_restart(app)

    @pg_typer.command("repair")
    def pg_repair_cmd():
        postgresql_repair(app)

    @pg_typer.command("configure")
    def pg_configure_cmd(password: str = typer.Option(..., help="Nueva contraseña de postgres")):
        postgresql_configure(app, password)

    # Comandos generales
    @app_typer.command()
    def login_cmd():
        login(app)

    @app_typer.command()
    def license_install_cmd(file: str = typer.Argument(..., help="Archivo de licencia .key")):
        license_install(app, file)

    @app_typer.command()
    def pro_status_cmd():
        pro_status(app)

    @app_typer.command()
    def update_all_cmd():
        update_all(app)