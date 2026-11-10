"""Safe launching of configured applications and URLs."""

from __future__ import annotations

import os
import subprocess
import webbrowser
from pathlib import Path

from jarvis.core.results import CommandResult


class ApplicationActions:
    def __init__(self, applications: dict[str, str]) -> None:
        self._applications = {
            self._normalize(name): command for name, command in applications.items()
        }

    def open(self, requested: str) -> CommandResult:
        name = self._normalize(requested)
        target = self._applications.get(name)
        if target is None:
            return CommandResult(
                f"No tengo configurada la aplicación '{requested}'.",
                success=False,
            )

        try:
            if target.startswith(("http://", "https://")):
                webbrowser.open(target)
            elif target == "discord:" and os.name == "nt":
                self._open_discord()
            elif os.name == "nt":
                os.startfile(target)  # type: ignore[attr-defined]
            else:
                subprocess.Popen([target])
        except OSError as error:
            return CommandResult(
                f"No pude abrir {requested}: {error}",
                success=False,
            )

        return CommandResult(f"Abriendo {requested}.")

    @staticmethod
    def _open_discord() -> None:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        updater = Path(local_app_data) / "Discord" / "Update.exe"
        if not updater.exists():
            raise OSError(
                "Discord de escritorio no está instalado o no se encontró Update.exe"
            )
        subprocess.Popen([str(updater), "--processStart", "Discord.exe"])

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(value.casefold().strip().split())
