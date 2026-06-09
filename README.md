# LocalServ - Gestor de Servidores Locales para Arch Linux

Un gestor de servidores locales modular y extensible, inspirado en XAMPP pero optimizado para el ecosistema Arch Linux.

## Características

- Gestión nativa vía `systemd`.
- Instalación automática con `pacman` y soporte AUR.
- Cambio de versiones de PHP al vuelo.
- Soporte para Apache, MariaDB, PostgreSQL, Node.js y Python.
- Sistema de licencias Pro mediante firmas Ed25519.

## Instalación

```bash
git clone https://github.com/Slashdog29/PlatformForge.git
cd PlatformForge
pip install -r requirements.txt
python main.py --help
```

## Uso

- `platformforge status`
- `platformforge start apache`
- `platformforge php-switch 8.2`
- `platformforge login`
