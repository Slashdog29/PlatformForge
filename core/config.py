"""
Gestión de configuración local en ~/.platformforge/config.json
"""
import json
from pathlib import Path
from typing import Any, Dict


class Config:
    CONFIG_DIR = Path.home() / ".platformforge"
    CONFIG_FILE = CONFIG_DIR / "config.json"

    DEFAULTS = {
        "db": {"default": "mysql"},
        "ports": {"apache": 80},
        "paths": {"data": str(CONFIG_DIR / "data")},
    }

    def __init__(self):
        self._data = self.DEFAULTS.copy()
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    loaded = json.load(f)
                    # Fusión superficial
                    for key, value in loaded.items():
                        if isinstance(value, dict) and isinstance(self._data.get(key), dict):
                            self._data[key].update(value)
                        else:
                            self._data[key] = value
            except (json.JSONDecodeError, OSError):
                pass  # ignorar errores de archivo corrupto y usar defaults

    def get(self, key: str, default=None) -> Any:
        """Obtiene un valor usando notación de puntos, ej. 'db.default'"""
        keys = key.split(".")
        d = self._data
        for k in keys:
            if isinstance(d, dict):
                d = d.get(k)
            else:
                return default
        return d if d is not None else default

    def set(self, key: str, value: Any):
        """Establece un valor con notación de puntos."""
        keys = key.split(".")
        d = self._data
        for k in keys[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        self._save()

    def _save(self):
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self._data, f, indent=2)