"""
PlatformForge GUI - Panel de control moderno y funcional.
"""
import sys
import subprocess
import os
import shutil
import json
import glob
from pathlib import Path
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QProgressBar, QTextEdit,
    QFrame, QGridLayout, QLineEdit, QFileDialog, QMessageBox,
    QGroupBox, QSystemTrayIcon, QMenu, QStyle, QDialog, QScrollArea,
    QInputDialog
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QIcon, QPalette, QColor

from core.app import App
from auth.github_oauth import start_flow
from auth.session_store import save_session

# ------------------- TRADUCCIONES -------------------
TRANSLATIONS = {
    "EN": {
        "title": "PlatformForge - Arch Admin",
        "header_title": "⚡ PLATFORM FORGE",
        "php_unit": "PHP Unit:",
        "project": "Project:",
        "maintenance": "System Maintenance",
        "open_proj": "🚀 Open Project",
        "link_start": "⚡ Link Start",
        "log_out": "🛑 Log Out",
        "yui_btn": "📄 Show Log Monitor",
        "lang_menu": "🇺🇸 Language",
        "opt_root": "📂 Root Folder",
        "opt_php": "⚙️ PHP Config",
        "opt_clear": "🧹 Clear Logs",
        "opt_repair_panel": "🛠️ Repair Apache",
        "opt_update_panel": "🔼 Update System",
        "opt_save_token": "🔐 GitHub Login",
        "opt_about": "ℹ️ About",
        "tools": ["Repair Apache", "Optimize RAM", "🐘 Change PHP", "📧 Mailpit", "🧹 Clear Logs", "⚙️ Config Root", "Hide Logs"],
        "tray_toggle": "Show/Hide Panel",
        "tray_start": "🚀 Link Start",
        "tray_stop": "💤 Log Out",
        "tray_open": "📂 Open Root",
        "tray_exit": "❌ Exit",
    },
    "ES": {
        "title": "PlatformForge - Administrador Arch",
        "header_title": "⚡ PLATFORM FORGE",
        "php_unit": "Unidad PHP:",
        "project": "Proyecto:",
        "maintenance": "Mantenimiento del Sistema",
        "open_proj": "🚀 Abrir Proyecto",
        "link_start": "⚡ Link Start",
        "log_out": "🛑 Log Out",
        "yui_btn": "📄 Mostrar Monitor de Logs",
        "lang_menu": "🇪🇸 Idioma",
        "opt_root": "📂 Carpeta Raíz",
        "opt_php": "⚙️ Configuración PHP",
        "opt_clear": "🧹 Limpiar Logs",
        "opt_repair_panel": "🛠️ Reparar Apache",
        "opt_update_panel": "🔼 Actualizar Sistema",
        "opt_save_token": "🔐 Iniciar sesión GitHub",
        "opt_about": "ℹ️ Acerca de",
        "tools": ["Reparar Apache", "Optimizar RAM", "🐘 Cambiar PHP", "📧 Mailpit", "🧹 Vaciar Logs", "⚙️ Config Raíz", "Ocultar Logs"],
        "tray_toggle": "Mostrar/Ocultar",
        "tray_start": "🚀 Link Start",
        "tray_stop": "💤 Log Out",
        "tray_open": "📂 Abrir Raíz",
        "tray_exit": "❌ Salir",
    }
}

# ------------------- ESTILO ÚNICO Y MODERNO -------------------
STYLE = """
QMainWindow {
    background-color: #0b0e14;
}
QWidget {
    color: #cfd8dc;
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 13px;
}
#Sidebar {
    background-color: #151921;
    border-right: 1px solid #252a33;
    min-width: 220px;
}
#MainContent {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0b0e14, stop:1 #1a1f29);
}
.ServiceCard {
    background: #151921;
    border: 1px solid #252a33;
    border-radius: 12px;
    padding: 15px;
}
.ServiceCard:hover {
    border-color: #00e5ff;
    background: #1c222d;
}
QPushButton {
    background: #252a33;
    color: #ffffff;
    border: none;
    padding: 10px 18px;
    border-radius: 8px;
    font-weight: bold;
}
QPushButton:hover {
    background: #353b45;
}
.PrimaryBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00e5ff, stop:1 #1200ff);
    color: white;
}
.PrimaryBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f2fe, stop:1 #4facfe);
}
.DangerBtn {
    background: #ff5252;
}

QComboBox {
    background: #151921;
    border: 1px solid #353b45;
    padding: 8px;
    border-radius: 6px;
}
QTextEdit {
    background: #05070a;
    color: #00ff41;
    border: 1px solid #252a33;
    font-family: "Fira Code", monospace;
    border-radius: 8px;
}
QProgressBar {
    background: #151921;
    border-radius: 10px;
    height: 10px;
    text-align: transparent;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00e5ff, stop:1 #ab47bc);
    border-radius: 10px;
}
"""

# ------------------- COMPONENTE: TARJETA DE SERVICIO -------------------
class ServiceCard(QFrame):
    def __init__(self, name, key, app, parent=None):
        super().__init__(parent)
        self.setObjectName(f"card_{key}")
        self.setProperty("class", "ServiceCard")
        self.key = key
        self.app = app
        self.service = app.get_service(key)
        
        layout = QVBoxLayout(self)
        
        self.title = QLabel(name.upper())
        self.title.setStyleSheet("font-weight: 900; color: #00e5ff; font-size: 14px;")
        layout.addWidget(self.title)

        self.status_dot = QLabel("● Desconocido")
        layout.addWidget(self.status_dot)

        self.version_lbl = QLabel("Versión: --")
        self.version_lbl.setStyleSheet("color: #78909c; font-size: 11px;")
        layout.addWidget(self.version_lbl)

        btn_row = QHBoxLayout()
        self.btn_toggle = QPushButton("Gestionar")
        self.btn_toggle.clicked.connect(self.on_manage_clicked)
        btn_row.addWidget(self.btn_toggle)
        layout.addLayout(btn_row)

    def update_info(self, status):
        color = "#00e676" if status == "active" else "#ff5252"
        self.status_dot.setText(f"● {status.upper()}")
        self.status_dot.setStyleSheet(f"color: {color}; font-weight: bold;")
        if self.service.is_installed():
            self.version_lbl.setText(f"Versión: {self.service.get_version()}")
        else:
            self.version_lbl.setText("Estado: No instalado")

    def on_manage_clicked(self):
        menu = QMenu(self)
        menu.setStyleSheet("QMenu { background-color: #151921; color: #cfd8dc; border: 1px solid #00e5ff; } QMenu::item:selected { background-color: #00e5ff; color: #0b0e14; }")
        acciones = [("▶ Iniciar", "start"), ("⏹ Detener", "stop"), ("🔄 Reiniciar", "restart"), ("🛠 Reparar", "repair")]
        for label, action_id in acciones:
            q_action = menu.addAction(label)
            # Conectamos dinámicamente a la acción en la ventana principal
            q_action.triggered.connect(lambda checked=False, a=action_id: self.parent().window().service_action(self.key, a))
        menu.exec(self.btn_toggle.mapToGlobal(self.btn_toggle.rect().bottomLeft()))

# ------------------- DIÁLOGO SUDO -------------------
class SudoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 200)
        
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 400, 200)
        self.container.setStyleSheet("background-color: #151921; border: 2px solid #ffaa00; border-radius: 15px;")
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Se requieren privilegios de administrador")
        title.setStyleSheet("font-size: 14px; font-weight: bold; color: #ffaa00; border: none;")
        title.setWordWrap(True)
        layout.addWidget(title)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Contraseña sudo")
        self.password_input.setStyleSheet("background: #0b0e14; border: 1px solid #ffaa00; padding: 10px; color: white;")
        layout.addWidget(self.password_input)
        
        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setStyleSheet("background: #353b45; color: white;")
        btn_cancel.clicked.connect(self.reject)
        
        btn_ok = QPushButton("Autorizar")
        btn_ok.setStyleSheet("background: #ffaa00; color: #0b0e14; font-weight: bold;")
        btn_ok.clicked.connect(self.accept)
        btn_ok.setDefault(True)
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)
        self.password_input.setFocus()
        self.oldPos = self.pos()

    def get_password(self):
        return self.password_input.text()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.oldPos)
            event.accept()

# ------------------- DIÁLOGO DEPENDENCIAS -------------------
class MissingDepsDialog(QDialog):
    def __init__(self, missing_crit, missing_recom, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 350)
        
        self.container = QFrame(self)
        self.container.setGeometry(0, 0, 500, 350)
        self.container.setStyleSheet("background-color: #151921; border: 2px solid #00e5ff; border-radius: 15px;")
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Verificación de dependencias")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #00e5ff; border: none;")
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        content = QWidget()
        content_layout = QVBoxLayout(content)
        
        if missing_crit:
            lbl = QLabel("⚠️ Críticos:")
            lbl.setStyleSheet("color: #ff5252; font-weight: bold; border: none;")
            content_layout.addWidget(lbl)
            for pkg in missing_crit:
                p_lbl = QLabel(f"  • {pkg}")
                p_lbl.setStyleSheet("color: #cfd8dc; border: none;")
                content_layout.addWidget(p_lbl)
                
        if missing_recom:
            lbl = QLabel("ℹ️ Recomendados:")
            lbl.setStyleSheet("color: #4facfe; font-weight: bold; border: none;")
            content_layout.addWidget(lbl)
            for pkg in missing_recom:
                p_lbl = QLabel(f"  • {pkg}")
                p_lbl.setStyleSheet("color: #cfd8dc; border: none;")
                content_layout.addWidget(p_lbl)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        layout.addStretch()
        btn_layout = QHBoxLayout()
        btn_ignore = QPushButton("Ignorar")
        btn_ignore.setStyleSheet("background: #353b45; color: white;")
        btn_ignore.clicked.connect(self.reject)
        
        btn_install = QPushButton("Instalar Todo")
        btn_install.setStyleSheet("background: #00e5ff; color: #0b0e14; font-weight: bold;")
        btn_install.clicked.connect(self.accept)
        
        btn_layout.addWidget(btn_ignore)
        btn_layout.addWidget(btn_install)
        layout.addLayout(btn_layout)
        self.oldPos = self.pos()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.oldPos)
            event.accept()

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
        self.worker = None
        self.sudo_password = None
        self.idioma = "ES"
        self.favoritos = []
        self.dir_proyectos = "/srv/http" if Path("/etc/arch-release").exists() else "/var/www/html"
        self.ruta_config = Path.home() / ".platformforge" / "config_gui.json"
        
        # Corrección de dependencias: se añaden paquetes faltantes detectados
        self.critical_deps = ["php", "apache", "mariadb", "php-apache", "postgresql", "python-psutil"]
        self.recommended_deps = ["nodejs", "npm", "python-pip", "git"]
        self.setWindowTitle("PlatformForge Professional")
        self.setMinimumSize(1200, 850)
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.cargar_configuracion()

        # Scroll principal
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget(objectName="MainContainer")
        self.scroll.setWidget(self.container)
        self.setCentralWidget(self.scroll)

        # Monitor de logs (oculto por defecto)
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumHeight(160)
        self.log_view.hide()

        self.init_ui()

        # Métricas
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.refresh_stats)
        self.stats_timer.start(2000)

        # Bandeja
        self.setup_tray()

        # Verificar dependencias después de cargar la UI
        QTimer.singleShot(600, self.check_environment_dependencies)
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
                self.log("Autenticación sudo exitosa.")
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
        root_layout = QHBoxLayout(self.container)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- SIDEBAR ---
        sidebar = QWidget(objectName="Sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        
        # --- ENCABEZADO ---
        header = QHBoxLayout()
        self.title_lbl = QLabel(TRANSLATIONS[self.idioma]["header_title"])
        self.title_lbl.setStyleSheet("font-size: 26px; font-weight: 900; color: #ffaa00; letter-spacing: 2px;")
        header.addWidget(self.title_lbl)
        header.addStretch()
        self.btn_menu = QPushButton("⋮")
        self.btn_menu.setFixedSize(35, 35)
        self.btn_menu.setStyleSheet("font-size: 18px; background: transparent; border: none; color: #e0e0f2;")
        self.btn_menu.clicked.connect(self.show_options_menu)
        header.addWidget(self.btn_menu)
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.setStyleSheet("font-size: 16px; background: transparent; border: none; color: #ff6666;")
        self.btn_close.clicked.connect(self.close)
        header.addWidget(self.btn_close)
        sidebar_layout.addLayout(header)
        sidebar_layout.addSpacing(40)

        # Navegación
        for label in ["DASHBOARD", "SERVICES", "PROJECTS", "LOGS"]:
            btn_nav = QPushButton(label)
            btn_nav.setStyleSheet("text-align: left; padding: 12px; background: transparent; color: #90a4ae;")
            sidebar_layout.addWidget(btn_nav)
        
        sidebar_layout.addStretch()
        
        # Métricas en Sidebar
        self.cpu_bar = QProgressBar()
        self.ram_bar = QProgressBar()
        sidebar_layout.addWidget(QLabel("SYSTEM LOAD"))
        sidebar_layout.addWidget(self.cpu_bar)
        sidebar_layout.addWidget(self.ram_bar)
        
        self.btn_log_out = QPushButton(TRANSLATIONS[self.idioma]["log_out"])
        self.btn_log_out.setProperty("class", "DangerBtn")
        self.btn_log_out.clicked.connect(self.log_out)
        sidebar_layout.addWidget(self.btn_log_out)

        root_layout.addWidget(sidebar)

        # --- CONTENIDO PRINCIPAL ---
        main_area = QWidget(objectName="MainContent")
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        root_layout.addWidget(main_area)

        # --- ACCESOS DIRECTOS RÁPIDOS ---
        quick_row = QHBoxLayout()
        self.btn_php_config = QPushButton(TRANSLATIONS[self.idioma]["opt_php"])
        self.btn_localhost_root = QPushButton(TRANSLATIONS[self.idioma]["opt_root"])
        self.btn_localhost_web = QPushButton("🌐 Localhost Web")
        for btn in (self.btn_php_config, self.btn_localhost_root, self.btn_localhost_web):
            btn.setStyleSheet("background: rgba(255,255,255,0.05); border: 1px solid #4a4a8a; padding: 6px 12px;")
        self.btn_php_config.clicked.connect(self.open_php_config)
        self.btn_localhost_root.clicked.connect(self.open_localhost_root)
        self.btn_localhost_web.clicked.connect(self.open_web_localhost)
        quick_row.addWidget(self.btn_php_config)
        quick_row.addWidget(self.btn_localhost_root)
        quick_row.addWidget(self.btn_localhost_web)
        quick_row.addStretch()
        main_layout.addLayout(quick_row)

        # --- SELECTORES PHP / PROYECTO ---
        sel_row = QHBoxLayout()
        sel_row.addWidget(QLabel(TRANSLATIONS[self.idioma]["php_unit"]))
        self.php_combo = QComboBox()
        self.php_combo.setMinimumWidth(140)
        sel_row.addWidget(self.php_combo, 1)
        self.btn_switch_php = QPushButton("Cambiar")
        self.btn_switch_php.clicked.connect(self.switch_php)
        sel_row.addWidget(self.btn_switch_php)
        self.btn_install_php = QPushButton("Instalar")
        self.btn_install_php.clicked.connect(self.install_php_dialog)
        sel_row.addWidget(self.btn_install_php)

        sel_row.addSpacing(25)
        sel_row.addWidget(QLabel(TRANSLATIONS[self.idioma]["project"]))
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(180)
        self.project_combo.currentTextChanged.connect(self.actualizar_icono_favorito)
        sel_row.addWidget(self.project_combo, 2)
        self.btn_fav = QPushButton("☆")
        self.btn_fav.setFixedSize(40, 35)
        self.btn_fav.setStyleSheet("font-size: 20px; color: #ffcc00; background: transparent; border: none;")
        self.btn_fav.clicked.connect(self.alternar_favorito)
        sel_row.addWidget(self.btn_fav)
        self.btn_open_project = QPushButton(TRANSLATIONS[self.idioma]["open_proj"])
        self.btn_open_project.setStyleSheet("background: #ffaa00; color: #000; font-weight: bold;")
        self.btn_open_project.clicked.connect(self.abrir_proyecto_seleccionado)
        sel_row.addWidget(self.btn_open_project)
        main_layout.addLayout(sel_row)

        # --- PANELES DE SERVICIOS (3 columnas) ---
        services_layout = QGridLayout()
        self.cards = {
            "apache": ServiceCard("Apache Server", "apache", self.app),
            "mysql": ServiceCard("MariaDB / MySQL", "mysql", self.app),
            "postgresql": ServiceCard("PostgreSQL", "postgresql", self.app)
        }
        for i, card in enumerate(self.cards.values()):
            services_layout.addWidget(card, 0, i)
        main_layout.addLayout(services_layout)

        # --- BOTONES DE ACCIÓN GLOBAL ---
        power_row = QHBoxLayout()
        self.btn_link_start = QPushButton(TRANSLATIONS[self.idioma]["link_start"])
        self.btn_link_start.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #006644, stop:1 #00aa44); color: #fff; font-size: 14px; padding: 12px; border-radius: 8px;")
        self.btn_link_start.clicked.connect(self.link_start)
        power_row.addWidget(self.btn_link_start)
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

        # --- MONITOR DE LOGS (toggle) ---
        self.btn_toggle_logs = QPushButton(TRANSLATIONS[self.idioma]["yui_btn"])
        self.btn_toggle_logs.clicked.connect(self.toggle_logs)
        main_layout.addWidget(self.btn_toggle_logs)
        main_layout.addWidget(self.log_view)

        # Refrescar datos iniciales
        self.refresh_services_status()
        self.refresh_php_combo()
        self.refresh_projects()

    def _crear_panel_servicio(self, nombre, key, unit):
        group = QGroupBox(nombre)
        group.setStyleSheet("QGroupBox { font-size: 14px; }")
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
        # Verificar privilegios antes de cualquier acción de servicio
        if not self.sudo_password and not self.request_sudo_password():
            self.log(f"Acción {action} cancelada: se requiere autenticación sudo.")
            return

        try:
            srv = self.app.get_service(name)
            func = getattr(srv, action, None)
            if func:
                success = func()
                res_str = "exitoso" if success else "fallido o requiere atención"
                self.log(f"{name.upper()}: {action} {res_str}")
            else:
                self.log(f"Acción '{action}' no soportada para el servicio {name}")
        except Exception as e:
            self.log(f"Error ejecutando {action} en {name}: {str(e)}")

        QTimer.singleShot(1000, self.refresh_services_status)

    def refresh_services_status(self):
        def unit_status(u):
            try:
                res = subprocess.run(["systemctl", "is-active", u], capture_output=True, text=True)
                return res.stdout.strip()
            except:
                return "inactive"
        
        for key, unit in [("apache", "httpd"), ("mysql", "mariadb"), ("postgresql", "postgresql")]:
            self.cards[key].update_info(unit_status(unit))

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
            self.worker.finished.connect(lambda ok, msg: self.log(f"PHP {version}: {msg}"))
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

    # ==================== MENÚ SUPERIOR (⋮) ====================
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
        menu.addAction("📦 Instalar licencia Pro", self.install_license_dialog)
        menu.addSeparator()
        menu.addAction(t["lang_menu"], self.toggle_language)
        menu.addAction(t["opt_about"], self.show_about)
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
            QMessageBox.information(self, "GitHub", f"Bienvenido, {result.github_user}")

    def install_license_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleccionar licencia", "", "*.key")
        if file_path:
            dest = Path.home() / ".platformforge" / "licenses"
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy(file_path, dest)
            self.app.reload_feature_manager()
            self.log("Licencia instalada.")
            QMessageBox.information(self, "Licencia", "Archivo copiado. Si es válido, las funciones Pro se activarán.")

    def show_about(self):
        QMessageBox.about(self, "Acerca de",
            "PlatformForge v1.0\n\n"
            "Gestor de servidores locales para Arch Linux.\n"
            "Desarrollado por Slashdog29\n"
            "Repositorio: github.com/Slashdog29/PlatformForge"
        )

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
        self.btn_php_config.setText(t["opt_php"])
        self.btn_localhost_root.setText(t["opt_root"])
        for i, btn in enumerate(self.tool_btns):
            if i < len(t["tools"]):
                btn.setText(t["tools"][i])
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