"""Configurable multi-step routines."""

from __future__ import annotations

from typing import Any

from jarvis.actions.applications import ApplicationActions
from jarvis.core.results import CommandResult


class RoutineActions:
    def __init__(
        self,
        routines: dict[str, list[dict[str, Any]]],
        applications: ApplicationActions,
    ) -> None:
        self._routines = routines
        self._applications = applications

    def run(self, name: str) -> CommandResult:
        steps = self._routines.get(name)
        if steps is None:
            return CommandResult(f"No existe la rutina '{name}'.", success=False)

        completed = 0
        for step in steps:
            if step.get("action") != "open":
                return CommandResult(
                    f"La rutina '{name}' contiene una acción no soportada.",
                    success=False,
                )
            result = self._applications.open(str(step.get("target", "")))
            if not result.success:
                return CommandResult(
                    f"La rutina '{name}' se detuvo: {result.message}",
                    success=False,
                )
            completed += 1

        return CommandResult(f"Rutina {name} activada ({completed} acciones).")
