# PlatformForge ⚙️

[![Status](https://img.shields.io/badge/Status-Development-orange?style=flat-for-the-badge)](https://github.com/Slashdog29/PlatformForge)
[![Architecture](https://img.shields.io/badge/Architecture-Modular-blue?style=flat-for-the-badge)](https://github.com/Slashdog29/PlatformForge)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OS](https://img.shields.io/badge/OS-Arch_Linux_Based-1793d1?style=flat-for-the-badge&logo=arch-linux)](https://archlinux.org/)

Gestor de Servidores Locales para Arch Linux
Un gestor de servidores locales modular y extensible, inspirado en XAMPP pero optimizado para el ecosistema Arch Linux.

**PlatformForge** es una plataforma profesional diseñada para la gestión integral de entornos de desarrollo local, optimizada exclusivamente para **Arch Linux y distribuciones basadas en él** (como CachyOS, EndeavourOS, Manjaro, etc.). Su objetivo es centralizar la administración de servicios, versiones y configuraciones técnicas bajo una arquitectura altamente modular, ordenada y escalable.
## Características

## 🎯 Propósito
PlatformForge surge como la solución definitiva para crear, mantener y ajustar *stacks* de desarrollo local en ecosistemas Arch sin depender de procesos manuales dispersos. La plataforma permite controlar componentes como Apache, PHP, bases de datos y otras tecnologías desde un entorno unificado, priorizando la automatización, la flexibilidad y la estandarización de los flujos de trabajo.
- Gestión nativa vía `systemd`.
- Instalación automática con `pacman` y soporte AUR.
- Cambio de versiones de PHP al vuelo.
- Soporte para Apache, MariaDB, PostgreSQL, Node.js y Python.
- Sistema de licencias Pro mediante firmas Ed25519.

## 🧱 Arquitectura del Proyecto
El sistema ha sido diseñado bajo una **arquitectura modular** que permite integrar nuevas tecnologías sin comprometer el núcleo. La estructura está organizada para garantizar eficiencia en sistemas Arch:
## Instalación

* **`core/`**: Orquestador principal encargado de la gestión de configuración y el control de características.
* **`services/`**: Implementaciones técnicas (Apache, PHP, MySQL, etc.). Cada servicio hereda de una clase abstracta `ServiceManager` para una extensión sencilla.
* **`auth/`**: Gestión de autenticación OAuth 2.0 y almacenamiento seguro de sesiones.
* **`licensing/`**: Sistema de verificación de licencias offline mediante criptografía asimétrica (Ed25519).
* **`ui/`**: Interfaz desacoplada (CLI basada en `typer`, con soporte para TUI/GUI).
* **`utils/`**: Utilerías especializadas para la gestión nativa de `systemd`, redes y paquetes (`pacman`/AUR).
```bash
git clone https://github.com/Slashdog29/PlatformForge.git
cd PlatformForge
pip install -r requirements.txt
python main.py --help
```

## ✨ Características Clave
* **Ecosistema Arch-First:** Integración profunda con el gestor de paquetes de Arch y servicios de `systemd`.
* **Gestión Centralizada:** Unifica el control de servicios, versiones y entornos en una sola interfaz.
* **Diseño Modular:** Escalabilidad total para integrar nuevos servicios o tecnologías.
* **Automatización:** Reducción drástica de tareas repetitivas en la configuración de entornos.
* **Experiencia Profesional:** Orientado a desarrolladores que buscan precisión, orden y eficiencia en su sistema local.
## Uso

## 🚀 Instalación
PlatformForge está diseñado para ejecutarse en entornos **Arch Linux y sus derivados**.

1. Clona el repositorio:
   ```bash
   git clone [https://github.com/Slashdog29/PlatformForge.git](https://github.com/Slashdog29/PlatformForge.git)
   cd PlatformForge
- `platformforge status`
- `platformforge start apache`
- `platformforge php-switch 8.2`
- `platformforge login`
