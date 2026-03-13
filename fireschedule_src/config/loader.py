import os
from pathlib import Path
from typing import Any

import yaml


class Config:
    _instance = None
    _config: dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self, config_path: str | None = None) -> dict[str, Any]:
        if config_path is None:
            config_path = os.environ.get(
                "FIRESCHEDULE_CONFIG",
                str(Path(__file__).parent.parent.parent / "config.yaml")
            )

        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, "r") as f:
                self._config = yaml.safe_load(f) or {}
        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    @property
    def categories(self) -> dict[str, Any]:
        return self._config.get("categories", {})

    @property
    def storage(self) -> dict[str, Any]:
        return self._config.get("storage", {})

    @property
    def reminders(self) -> dict[str, Any]:
        return self._config.get("reminders", {})

    @property
    def tui(self) -> dict[str, Any]:
        return self._config.get("tui", {})


config = Config()
