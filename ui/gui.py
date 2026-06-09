"""
PlatformForge GUI - Dashboard completo con menú contextual, traducciones,
                    herramientas, servicios, logs y autenticación sudo gráfica.
"""
import sys
import subprocess
import os
import shutil
import json
import glob
from pathlib import Path
from datetime import datetime

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QComboBox, QProgressBar, QTextEdit,
        QFrame, QGridLayout, QLineEdit, QFileDialog, QMessageBox,
        QGroupBox, QSystemTrayIcon, QMenu, QStyle, QDialog, QScrollArea,
        QInputDialog
    )
    from PySide6.QtCore import Qt, QTimer, QThread, Signal
    from PySide6.QtGui import QFont, QIcon
except ImportError:
    print("Error: PySide6 no está instalado.")
    sys.exit(1)

from core.app import App
from auth.github_oauth import start_flow
from auth.session_store import save_session

# ------------------- TRADUCCIONES -------------------
TRANSLATIONS = {
    "EN": {
        "title": "PlatformForge - Arch Admin",
        "header_title": "PLATFORM FORGE",
        "php_unit": "PHP UNIT:",
        "project": "PROJECT:",
        "maintenance": "SYSTEM MAINTENANCE",
        "open_proj": "🚀 OPEN PROJECT",
        "link_start": "⚡ LINK START",
        "log_out": "🛑 LOG OUT",
        "yui_btn": "📄 ACTIVATE LOG MONITOR (YUI TERMINAL)",
        "lang_menu": "🇺🇸 Change Language",
        "opt_root": "📂 Root Folder",
        "opt_add": "🖥️ Add to Menu",
        "opt_rm": "❌ Remove from Menu",
        "opt_php": "⚙️ PHP Config",
        "opt_clear": "🧹 Clear Logs",
        "opt_update_panel": "🔼 Update Panel",
        "opt_check_releases": "🔔 Check Releases",
        "opt_save_token": "🔐 Save Git Token",
        "opt_repair_panel": "🛠️ Repair Panel",
        "opt_about": "ℹ️ About",
        "opt_hide": "👻 Hide Panel",
        "opt_sync": "🔄 Sync Web Folder",
        "tools": ["Repair Apache", "Optimize RAM", "🐘 Change PHP", "📧 Mailpit", "🧹 Clear Logs", "⚙️ Config Root", "Hide Yui"],
        "tray_toggle": "Show/Hide Panel",
        "tray_start": "🚀 Link Start (Services)",
        "tray_stop": "💤 Log Out (Stop All)",
        "tray_open": "📂 Open Projects Root",
        "tray_exit": "❌ Exit PlatformForge",
    },
    "ES": {
        "title": "PlatformForge - Administrador Arch",
        "header_title": "PLATFORM FORGE",
        "php_unit": "UNIDAD PHP:",
        "project": "PROYECTO:",
        "maintenance": "MANTENIMIENTO DEL SISTEMA",
        "open_proj": "🚀 ABRIR PROYECTO",
        "link_start": "⚡ LINK START",
        "log_out": "🛑 LOG OUT",
        "yui_btn": "📄 ACTIVAR MONITOR DE LOGS (TERMINAL YUI)",
        "lang_menu": "🇪🇸 Cambiar Idioma",
        "opt_root": "📂 Carpeta Raíz",
        "opt_add": "🖥️ Añadir al Menú",
        "opt_rm": "❌ Quitar del Menú",
        "opt_php": "⚙️ Configuración PHP",
        "opt_clear": "🧹 Limpiar Logs",
        "opt_update_panel": "🔼 Actualizar Panel",
        "opt_check_releases": "🔔 Comprobar Lanzamientos",
        "opt_save_token": "🔐 Guardar Token Git",
        "opt_repair_panel": "🛠️ Reparar Panel",
        "opt_about": "ℹ️ Acerca de",
        "opt_hide": "👻 Ocultar Panel",
        "opt_sync": "🔄 Sincronizar Carpeta Web",
        "tools": ["Reparar Apache", "Optimizar RAM", "🐘 Cambiar PHP", "📧 Mailpit", "🧹 Vaciar Logs", "⚙️ Config Raíz", "Hide Yui"],
        "tray_toggle": "Mostrar/Ocultar Panel",
        "tray_start": "🚀 Link Start (Servicios)",
        "tray_stop": "💤 Log Out (Detener Todo)",
        "tray_open": "📂 Abrir Raíz Proyectos",
        "tray_exit": "❌ Salir de PlatformForge",
    }
}

# ------------------- ESTILO MODERNO -------------------
STYLE = """
QMainWindow { background-color: #1e1e2e; }
QWidget { color: #cdd6f4; font-family: "Segoe UI", sans-serif; }
QTabWidget::pane { border: 1px solid #45475a; background: #1e1e2e; }
QTabBar::tab { background: #313244; color: #cdd6f4; padding: 8px 16px; margin-right: 2px; }
QTabBar::tab:selected { background: #45475a; font-weight: bold; }
QGroupBox { border: 1px solid #45475a; border-radius: 6px; margin-top: 10px; color: #cdd6f4; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QPushButton { background-color: #89b4fa; color: #1e1e2e; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
QPushButton:hover { background-color: #74c7ec; }
QPushButton:pressed { background-color: #89dceb; }
QPushButton:disabled { background-color: #585b70; color: #a6adc8; }
QLabel { color: #cdd6f4; }
QComboBox { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; padding: 4px; border-radius: 4px; }
QLineEdit { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; padding: 6px; border-radius: 4px; }
QTextEdit { background-color: #181825; color: #cdd6f4; border: 1px solid #45475a; font-family: "Fira Code", monospace; }
QProgressBar { border: 1px solid #45475a; background-color: #313244; text-align: center; color: #cdd6f4; border-radius: 4px; }
QProgressBar::chunk { background-color: #a6e3a1; }
QMenu {
    background-color: rgba(15, 15, 22, 0.98);
    border: 1px solid #00ffcc;
    color: white;
}
QMenu::item {
    padding: 8px 25px;
    background: transparent;
}
QMenu::item:selected {
    background-color: rgba(0, 255, 204, 0.2);
    color: #00ffcc;
}
"""

# ------------------- DIÁLOGO SUDO -------------------
class SudoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Autenticación requerida")
        self.setFixedSize(400, 180)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        title = QLabel("Se requieren privilegios de administrador")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(title)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Contraseña sudo")
        layout.addWidget(self.password_input)
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Autorizar")
        btn_ok.clicked.connect(self.accept)
        btn_ok.setDefault(True)
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)
        self.password_input.setFocus()

    def get_password(self):
        return self.password_input.text()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

# ------------------- DIÁLOGO DEPENDENCIAS -------------------
class MissingDepsDialog(QDialog):
    def __init__(self, missing_crit, missing_recom, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dependencias faltantes")
        self.setFixedSize(500, 300)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        title = QLabel("Verificación de dependencias del sistema")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f9e2af;")
        layout.addWidget(title)
        if missing_crit:
            layout.addWidget(QLabel("⚠️ Paquetes críticos faltantes:"))
            for pkg in missing_crit:
                layout.addWidget(QLabel(f"  • {pkg}"))
        if missing_recom:
            layout.addWidget(QLabel("ℹ️ Paquetes recomendados faltantes:"))
            for pkg in missing_recom:
                layout.addWidget(QLabel(f"  • {pkg}"))
        layout.addStretch()
        btn_layout = QHBoxLayout()
        btn_ignore = QPushButton("Ignorar")
        btn_ignore.clicked.connect(self.reject)
        btn_install = QPushButton("Instalar automáticamente")
        btn_install.setStyleSheet("background-color: #a6e3a1; color: #1e1e2e;")
        btn_install.clicked.connect(self.accept)
        btn_layout.addWidget(btn_ignore)
        btn_layout.addWidget(btn_install)
        layout.addLayout(btn_layout)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()

# ------------------- HILO GENÉRICO -------------------
class ServiceWorker(QThread):
    finished = Signal(bool, str)
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(True, str(result))
        except Exception as e:
            self.finished.emit(False, str(e))

# ------------------- VENTANA PRINCIPAL -------------------
class MainWindow(QMainWindow):
    def __init__(self, app: App):
        super().__init__()
        self.app = app
        self.sudo_password = None
        self.idioma = "ES"
        self.favoritos = []
        self.dir_proyectos = "/srv/http" if Path("/etc/arch-release").exists() else "/var/www/html"
        self.ruta_config = Path.home() / ".platformforge" / "config_gui.json"
        self.critical_deps = ["php", "apache", "mariadb", "php-apache", "postgresql"]
        self.recommended_deps = ["nodejs", "npm", "python-pip", "git"]

        self.setWindowTitle("PlatformForge - Panel de Control")
        self.setMinimumSize(1050, 780)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.cargar_configuracion()

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget(objectName="MainContainer")
        self.scroll.setWidget(self.container)
        self.setCentralWidget(self.scroll)

        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(150)
        self.log_view.hide()  # Inicialmente oculto

        self.init_ui()

        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.refresh_stats)
        self.stats_timer.start(2000)

        self.setup_tray()

        QTimer.singleShot(500, self.check_environment_dependencies)
        QTimer.singleShot(100, self.refresh_php_combo)
        QTimer.singleShot(200, self.refresh_projects)

    # ==================== CONFIGURACIÓN PERSISTENTE ====================
    def cargar_configuracion(self):
        if self.ruta_config.exists():
            try:
                data = json.loads(self.ruta_config.read_text())
                self.dir_proyectos = data.get("project_dir", self.dir_proyectos)
                self.favoritos = data.get("favorites", [])
                self.idioma = data.get("language", "ES")
            except:
                pass

    def guardar_configuracion(self):
        self.ruta_config.parent.mkdir(parents=True, exist_ok=True)
        datos = {
            "project_dir": self.dir_proyectos,
            "favorites": self.favoritos,
            "language": self.idioma
        }
        self.ruta_config.write_text(json.dumps(datos, indent=2))

    # ==================== SUDO ====================
    def request_sudo_password(self):
        if QThread.currentThread() != QApplication.instance().thread():
            return False
        dialog = SudoDialog(self)
        if dialog.exec() == QDialog.Accepted:
            password = dialog.get_password()
            check = subprocess.run(["sudo", "-S", "true"], input=f"{password}\n", text=True, capture_output=True)
            if check.returncode == 0:
                self.sudo_password = password
                self.log("Autenticación exitosa.")
                return True
            else:
                self.log("Contraseña incorrecta.")
        return False

    def run_sudo_command(self, cmd_list, capture=True):
        if not self.sudo_password and not self.request_sudo_password():
            return None
        return subprocess.run(["sudo", "-S"] + cmd_list, input=f"{self.sudo_password}\n", text=True, capture_output=capture)

    # ==================== INTERFAZ GRÁFICA ====================
    def init_ui(self):
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # --- ENCABEZADO ---
        header = QHBoxLayout()
        self.title_lbl = QLabel(TRANSLATIONS[self.idioma]["header_title"])
        self.title_lbl.setStyleSheet("font-size: 22px; font-weight: 900; color: #89b4fa;")
        header.addWidget(self.title_lbl)
        header.addStretch()
        self.btn_menu = QPushButton("⋮")
        self.btn_menu.setFixedSize(35, 35)
        self.btn_menu.clicked.connect(self.show_options_menu)
        header.addWidget(self.btn_menu)
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.clicked.connect(self.close)
        header.addWidget(self.btn_close)
        main_layout.addLayout(header)

        # --- ACCESOS DIRECTOS ---
        quick_row = QHBoxLayout()
        self.btn_php_config = QPushButton(TRANSLATIONS[self.idioma]["opt_php"])
        self.btn_localhost_root = QPushButton(TRANSLATIONS[self.idioma]["opt_root"])
        self.btn_localhost_web = QPushButton("🌐 Localhost Web")
        for btn in (self.btn_php_config, self.btn_localhost_root, self.btn_localhost_web):
            btn.setStyleSheet("background-color: #45475a; color: #cdd6f4; border: 1px solid #585b70;")
        self.btn_php_config.clicked.connect(self.open_php_config)
        self.btn_localhost_root.clicked.connect(self.open_localhost_root)
        self.btn_localhost_web.clicked.connect(self.open_web_localhost)
        quick_row.addWidget(self.btn_php_config)
        quick_row.addWidget(self.btn_localhost_root)
        quick_row.addWidget(self.btn_localhost_web)
        quick_row.addStretch()
        main_layout.addLayout(quick_row)

        # --- MÉTRICAS ---
        metrics = QHBoxLayout()
        self.cpu_bar = QProgressBar()
        self.ram_bar = QProgressBar()
        metrics.addWidget(QLabel("CPU:"))
        metrics.addWidget(self.cpu_bar)
        metrics.addWidget(QLabel("RAM:"))
        metrics.addWidget(self.ram_bar)
        main_layout.addLayout(metrics)

        # --- SELECTORES PHP / PROYECTO ---
        sel_row = QHBoxLayout()
        sel_row.addWidget(QLabel(TRANSLATIONS[self.idioma]["php_unit"]))
        self.php_combo = QComboBox()
        self.php_combo.setMinimumWidth(150)
        sel_row.addWidget(self.php_combo, 1)
        self.btn_switch_php = QPushButton("Cambiar")
        self.btn_switch_php.clicked.connect(self.switch_php)
        sel_row.addWidget(self.btn_switch_php)
        self.btn_install_php = QPushButton("Instalar versión")
        self.btn_install_php.clicked.connect(self.install_php_dialog)
        sel_row.addWidget(self.btn_install_php)

        sel_row.addSpacing(20)
        sel_row.addWidget(QLabel(TRANSLATIONS[self.idioma]["project"]))
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(200)
        self.project_combo.currentTextChanged.connect(self.actualizar_icono_favorito)
        sel_row.addWidget(self.project_combo, 2)
        self.btn_fav = QPushButton("☆")
        self.btn_fav.setFixedSize(40, 35)
        self.btn_fav.setStyleSheet("font-size: 18px; color: #f9e2af;")
        self.btn_fav.clicked.connect(self.alternar_favorito)
        sel_row.addWidget(self.btn_fav)
        self.btn_open_project = QPushButton(TRANSLATIONS[self.idioma]["open_proj"])
        self.btn_open_project.clicked.connect(self.abrir_proyecto_seleccionado)
        sel_row.addWidget(self.btn_open_project)
        main_layout.addLayout(sel_row)

        # --- SERVICIOS (3 columnas) ---
        services_layout = QHBoxLayout()
        services_layout.addWidget(self._crear_panel_servicio("Apache", "apache", "httpd"))
        services_layout.addWidget(self._crear_panel_servicio("MySQL/MariaDB", "mysql", "mariadb"))
        services_layout.addWidget(self._crear_panel_servicio("PostgreSQL", "postgresql", "postgresql"))
        main_layout.addLayout(services_layout)

        # --- BOTONES POWER ---
        power_row = QHBoxLayout()
        self.btn_link_start = QPushButton(TRANSLATIONS[self.idioma]["link_start"])
        self.btn_link_start.setStyleSheet("background-color: #a6e3a1; color: #1e1e2e; font-size: 14px; padding: 12px;")
        self.btn_link_start.clicked.connect(self.link_start)
        self.btn_log_out = QPushButton(TRANSLATIONS[self.idioma]["log_out"])
        self.btn_log_out.setStyleSheet("background-color: #f38ba8; color: #1e1e2e; font-size: 14px; padding: 12px;")
        self.btn_log_out.clicked.connect(self.log_out)
        power_row.addWidget(self.btn_link_start)
        power_row.addWidget(self.btn_log_out)
        main_layout.addLayout(power_row)

        # --- HERRAMIENTAS (Grid) ---
        tools_group = QGroupBox(TRANSLATIONS[self.idioma]["maintenance"])
        tools_grid = QGridLayout()
        tools_grid.setSpacing(10)
        self.tool_btns = []
        for i, nombre in enumerate(TRANSLATIONS[self.idioma]["tools"]):
            btn = QPushButton(nombre)
            btn.setFixedSize(180, 35)
            if i == 0:
                btn.clicked.connect(self.reparar_apache)
            elif i == 1:
                btn.clicked.connect(self.optimizar_ram)
            elif i == 2:
                btn.clicked.connect(self.cambiar_php_dialogo)
            elif i == 3:
                btn.clicked.connect(self.abrir_mailpit)
            elif i == 4:
                btn.clicked.connect(self.limpiar_logs)
            elif i == 5:
                btn.clicked.connect(self.abrir_config_root)
            elif i == 6:
                btn.clicked.connect(self.toggle_logs)
            tools_grid.addWidget(btn, i // 3, i % 3)
            self.tool_btns.append(btn)
        tools_group.setLayout(tools_grid)
        main_layout.addWidget(tools_group)

        # --- MONITOR DE LOGS (botón toggle) ---
        self.btn_toggle_logs = QPushButton(TRANSLATIONS[self.idioma]["yui_btn"])
        self.btn_toggle_logs.clicked.connect(self.toggle_logs)
        main_layout.addWidget(self.btn_toggle_logs)
        main_layout.addWidget(self.log_view)

        self.refresh_services_status()
        self.refresh_php_combo()
        self.refresh_projects()

    def _crear_panel_servicio(self, nombre, key, unit):
        group = QGroupBox(nombre)
        layout = QVBoxLayout()
        status_lbl = QLabel("Estado: ...")
        version_lbl = QLabel("Versión: ...")
        layout.addWidget(status_lbl)
        layout.addWidget(version_lbl)
        btn_layout = QHBoxLayout()
        for texto, accion in [("Iniciar", "start"), ("Detener", "stop"), ("Reiniciar", "restart"), ("Reparar", "repair")]:
            btn = QPushButton(texto)
            btn.clicked.connect(lambda checked=False, a=accion, k=key: self.service_action(k, a))
            btn_layout.addWidget(btn)
        layout.addLayout(btn_layout)
        group.setLayout(layout)
        setattr(self, f"{key}_status_lbl", status_lbl)
        setattr(self, f"{key}_version_lbl", version_lbl)
        return group

    # ==================== ACCIONES SERVICIOS ====================
    def service_action(self, name, action):
        unit_map = {"apache": "httpd", "mysql": "mariadb", "postgresql": "postgresql"}
        unit = unit_map.get(name)
        if not unit:
            return
        if action in ("start", "stop", "restart"):
            res = self.run_sudo_command(["systemctl", action, unit])
            if res and res.returncode == 0:
                self.log(f"{name}: {action} correcto")
            else:
                self.log(f"{name}: error al {action}")
        elif action == "repair":
            if name == "apache":
                self.run_sudo_command(["httpd", "-t"])
            elif name == "mysql":
                self.run_sudo_command(["mysqlcheck", "--all-databases", "--auto-repair"])
            elif name == "postgresql":
                self.log("Reparación PostgreSQL no implementada.")
        QTimer.singleShot(1000, self.refresh_services_status)

    def refresh_services_status(self):
        def unit_status(u):
            try:
                res = subprocess.run(["systemctl", "is-active", u], capture_output=True, text=True)
                return res.stdout.strip()
            except:
                return "desconocido"

        for key, unit in [("apache", "httpd"), ("mysql", "mariadb"), ("postgresql", "postgresql")]:
            status_lbl = getattr(self, f"{key}_status_lbl", None)
            version_lbl = getattr(self, f"{key}_version_lbl", None)
            if status_lbl:
                status_lbl.setText(f"Estado: {unit_status(unit)}")
            if version_lbl:
                srv = self.app.get_service(key)
                version_lbl.setText(f"Versión: {srv.get_version() if srv.is_installed() else 'no'}")

    def link_start(self):
        for s in ["apache", "mysql", "postgresql"]:
            self.service_action(s, "start")
        self.log("Todos los servicios iniciados.")

    def log_out(self):
        for s in ["apache", "mysql", "postgresql"]:
            self.service_action(s, "stop")
        self.log("Todos los servicios detenidos.")

    # ==================== PHP ====================
    def refresh_php_combo(self):
        php = self.app.get_service("php")
        self.php_combo.clear()
        for v in php.get_available_versions():
            if php.is_version_installed(v):
                self.php_combo.addItem(v)
        self.php_combo.setToolTip(f"Actual: {php.get_version()}")

    def switch_php(self):
        version = self.php_combo.currentText()
        if not version:
            return
        php = self.app.get_service("php")
        class SwitchWorker(QThread):
            finished = Signal(bool, str)
            def __init__(self, mw, ver):
                super().__init__()
                self.mw = mw
                self.ver = ver
            def run(self):
                try:
                    if not self.mw.sudo_password and not self.mw.request_sudo_password():
                        self.finished.emit(False, "Autenticación cancelada")
                        return
                    pkg = php.AUR_PACKAGES.get(self.ver)
                    if not pkg:
                        self.finished.emit(False, "Versión no soportada")
                        return
                    if not php.pkg.is_installed(pkg):
                        self.mw.log(f"Instalando PHP {self.ver}...")
                        php.install_version(self.ver)
                    self.mw.run_sudo_command(["ln", "-sf", f"/usr/bin/php{self.ver.replace('.', '')}", "/usr/bin/php"])
                    src = f"/usr/lib/httpd/modules/libphp{self.ver.replace('.', '')}.so"
                    if os.path.exists(src):
                        self.mw.run_sudo_command(["cp", src, "/usr/lib/httpd/modules/libphp.so"])
                    self.mw.run_sudo_command(["systemctl", "restart", "httpd"])
                    self.finished.emit(True, f"PHP cambiado a {self.ver}")
                except Exception as e:
                    self.finished.emit(False, str(e))
        self.worker = SwitchWorker(self, version)
        self.worker.finished.connect(lambda ok, msg: self.log(msg))
        self.worker.start()

    def install_php_dialog(self):
        version, ok = QInputDialog.getItem(self, "Instalar PHP", "Versión:", ["7.4", "8.1", "8.2", "8.3"], 0, False)
        if ok and version:
            php = self.app.get_service("php")
            self.worker = ServiceWorker(php.install_version, version)
            self.worker.finished.connect(lambda ok, msg: self.log(f"Instalación PHP {version}: {msg}"))
            self.worker.start()
            QTimer.singleShot(3000, self.refresh_php_combo)

    # ==================== PROYECTOS ====================
    def refresh_projects(self):
        self.project_combo.clear()
        if os.path.exists(self.dir_proyectos):
            dirs = sorted([d for d in os.listdir(self.dir_proyectos) if os.path.isdir(os.path.join(self.dir_proyectos, d))])
            self.project_combo.addItems(dirs)
        else:
            self.project_combo.addItem("Directorio no encontrado")

    def actualizar_icono_favorito(self):
        proyecto = self.project_combo.currentText()
        self.btn_fav.setText("★" if proyecto in self.favoritos else "☆")

    def alternar_favorito(self):
        proyecto = self.project_combo.currentText()
        if not proyecto:
            return
        if proyecto in self.favoritos:
            self.favoritos.remove(proyecto)
        else:
            self.favoritos.append(proyecto)
        self.actualizar_icono_favorito()
        self.guardar_configuracion()

    def abrir_proyecto_seleccionado(self):
        proyecto = self.project_combo.currentText()
        if proyecto and os.path.isdir(os.path.join(self.dir_proyectos, proyecto)):
            subprocess.Popen(["xdg-open", os.path.join(self.dir_proyectos, proyecto)])

    # ==================== HERRAMIENTAS ====================
    def reparar_apache(self):
        self.service_action("apache", "repair")

    def optimizar_ram(self):
        self.run_sudo_command(["sync"])
        self.run_sudo_command(["sysctl", "-w", "vm.drop_caches=3"])
        self.log("RAM optimizada.")

    def abrir_mailpit(self):
        subprocess.Popen(["xdg-open", "http://localhost:8025"])

    def limpiar_logs(self):
        for path in ["/var/log/httpd/*", "/var/log/mysql/*"]:
            self.run_sudo_command(["rm", "-rf"] + glob.glob(path))
        self.log("Logs limpiados.")

    def abrir_config_root(self):
        subprocess.Popen(["xdg-open", self.dir_proyectos])

    def cambiar_php_dialogo(self):
        version, ok = QInputDialog.getText(self, "Cambiar PHP", "Versión (ej. 8.2):")
        if ok and version:
            php = self.app.get_service("php")
            self.worker = ServiceWorker(php.switch_version, version)
            self.worker.finished.connect(lambda ok, msg: self.log(msg))
            self.worker.start()

    # ==================== ACCESOS DIRECTOS ====================
    def open_php_config(self):
        subprocess.Popen(["xdg-open", "/etc/php/php.ini"])

    def open_localhost_root(self):
        subprocess.Popen(["xdg-open", self.dir_proyectos])

    def open_web_localhost(self):
        subprocess.Popen(["xdg-open", "http://localhost"])

    # ==================== DEPENDENCIAS ====================
    def check_environment_dependencies(self):
        self.log("Verificando dependencias del sistema...")
        missing_crit = [p for p in self.critical_deps if subprocess.run(["pacman", "-Qi", p], capture_output=True).returncode != 0]
        missing_recom = [p for p in self.recommended_deps if subprocess.run(["pacman", "-Qi", p], capture_output=True).returncode != 0]
        if missing_crit or missing_recom:
            diag = MissingDepsDialog(missing_crit, missing_recom, self)
            if diag.exec() == QDialog.Accepted:
                all_missing = missing_crit + missing_recom
                res = self.run_sudo_command(["pacman", "-S", "--noconfirm", "--needed"] + all_missing)
                if res and res.returncode == 0:
                    self.log("Dependencias instaladas correctamente.")
                else:
                    self.log("Error al instalar dependencias.")
        else:
            self.log("Todas las dependencias están satisfechas.")

    # ==================== CUENTA Y LICENCIA (MENÚ) ====================
    def show_options_menu(self):
        t = TRANSLATIONS[self.idioma]
        menu = QMenu(self)
        menu.addAction(t["opt_root"], self.open_localhost_root)
        menu.addAction(t["opt_php"], self.open_php_config)
        menu.addSeparator()
        menu.addAction(t["opt_clear"], self.limpiar_logs)
        menu.addAction(t["opt_repair_panel"], self.reparar_apache)
        menu.addAction(t["opt_update_panel"], self.check_environment_dependencies)
        menu.addSeparator()
        menu.addAction(t["opt_save_token"], self.login_github)
        menu.addAction(t["opt_about"], self.show_about)
        menu.addSeparator()
        menu.addAction(t["lang_menu"], self.toggle_language)
        menu.exec(self.btn_menu.mapToGlobal(self.btn_menu.rect().bottomLeft()))

    def login_github(self):
        class LoginThread(QThread):
            finished = Signal(object)
            def run(self):
                try:
                    session = start_flow()
                    self.finished.emit(session)
                except Exception as e:
                    self.finished.emit(e)
        self.login_thread = LoginThread()
        self.login_thread.finished.connect(self.handle_login_result)
        self.login_thread.start()

    def handle_login_result(self, result):
        if isinstance(result, Exception):
            QMessageBox.critical(self, "Error", str(result))
        else:
            save_session(result)
            self.app.session = result
            self.app.reload_feature_manager()
            self.log(f"Sesión iniciada como {result.github_user}")

    def install_license_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar licencia", "", "*.key")
        if file_path:
            dest = Path.home() / ".platformforge" / "licenses"
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy(file_path, dest)
            self.app.reload_feature_manager()
            self.log("Licencia instalada.")
            QMessageBox.information(self, "OK", "Licencia copiada.")

    def show_about(self):
        QMessageBox.information(self, "Acerca de", "PlatformForge v1.0\nGestor de servidores locales para Arch Linux.\nDesarrollado por Slashdog29.")

    def toggle_language(self):
        self.idioma = "EN" if self.idioma == "ES" else "ES"
        self.guardar_configuracion()
        self.update_ui_texts()

    def update_ui_texts(self):
        t = TRANSLATIONS[self.idioma]
        self.setWindowTitle(t["title"])
        self.title_lbl.setText(t["header_title"])
        self.btn_link_start.setText(t["link_start"])
        self.btn_log_out.setText(t["log_out"])
        self.btn_toggle_logs.setText(t["yui_btn"])
        self.btn_open_project.setText(t["open_proj"])
        # Actualizar botones de herramientas
        for i, btn in enumerate(self.tool_btns):
            if i < len(t["tools"]):
                btn.setText(t["tools"][i])
        # Actualizar menú de bandeja si existe
        if hasattr(self, 'tray_menu'):
            self.update_tray_menu()

    # ==================== MÉTRICAS ====================
    def refresh_stats(self):
        try:
            import psutil
            self.cpu_bar.setValue(int(psutil.cpu_percent()))
            self.ram_bar.setValue(int(psutil.virtual_memory().percent))
        except:
            self.cpu_bar.setValue(0)
            self.ram_bar.setValue(0)

    # ==================== LOGS ====================
    def toggle_logs(self):
        if self.log_view.isVisible():
            self.log_view.hide()
            self.btn_toggle_logs.setText(TRANSLATIONS[self.idioma]["yui_btn"])
        else:
            self.log_view.show()
            self.btn_toggle_logs.setText("Ocultar Monitor")

    def log(self, message):
        now = datetime.now().strftime("%H:%M:%S")
        self.log_view.append(f"[{now}] {message}")

    # ==================== BANDEJA DEL SISTEMA ====================
    def setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray_menu = QMenu()
        self.update_tray_menu()
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def update_tray_menu(self):
        t = TRANSLATIONS[self.idioma]
        self.tray_menu.clear()
        self.tray_menu.addAction(t["tray_toggle"], self.toggle_visibility)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(t["tray_start"], self.link_start)
        self.tray_menu.addAction(t["tray_stop"], self.log_out)
        self.tray_menu.addAction(t["tray_open"], self.open_localhost_root)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(t["tray_exit"], self.close)

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.showNormal()
            self.activateWindow()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_visibility()

    # ==================== VENTANA SIN BORDES ====================
    def mousePressEvent(self, event):
        self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        delta = event.globalPosition().toPoint() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPosition().toPoint()


# ------------------- LANZADOR -------------------
def launch_gui(app: App):
    qt_app = QApplication(sys.argv)
    qt_app.setStyleSheet(STYLE)
    window = MainWindow(app)
    window.show()
    sys.exit(qt_app.exec())