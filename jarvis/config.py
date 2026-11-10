"""Configuration loading for Jarvis."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = ROOT_DIR / "config" / "jarvis.json"


@dataclass(frozen=True)
class JarvisConfig:
    data: dict[str, Any]

    @property
    def apps(self) -> dict[str, str]:
        return self.data.get("applications", {})

    @property
    def routines(self) -> dict[str, list[dict[str, Any]]]:
        return self.data.get("routines", {})


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> JarvisConfig:
    if not path.exists():
        raise FileNotFoundError(f"Jarvis config not found: {path}")
    with path.open("r", encoding="utf-8") as file:
        return JarvisConfig(json.load(file))
