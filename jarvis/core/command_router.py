"""Deterministic command routing.

Natural-language AI can be added later, but known commands should remain
deterministic so they are fast, predictable, and cheap in resources.
"""

from __future__ import annotations

import re

from jarvis.actions.applications import ApplicationActions
from jarvis.actions.routines import RoutineActions
from jarvis.core.results import CommandResult


class CommandRouter:
    def __init__(
        self,
        applications: ApplicationActions,
        routines: RoutineActions,
    ) -> None:
        self.applications = applications
        self.routines = routines

    def handle(self, text: str) -> CommandResult:
        normalized = self._normalize(text)

        if normalized in {"modo gaming", "activa modo gaming", "activar modo gaming"}:
            return self.routines.run("gaming")

        match = re.fullmatch(r"(?:abre|abrir|inicia|iniciar)\s+(.+)", normalized)
        if match:
            return self.applications.open(match.group(1))

        return CommandResult(
            "Todavía no conozco ese comando. Prueba con 'abre Spotify' o 'modo gaming'.",
            success=False,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.casefold().strip().split())
