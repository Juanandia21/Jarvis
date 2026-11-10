"""Deterministic command routing.

Natural-language AI can be added later, but known commands should remain
deterministic so they are fast, predictable, and cheap in resources.
"""

from __future__ import annotations

import re

from jarvis.actions.applications import ApplicationActions
from jarvis.actions.routines import RoutineActions
from jarvis.core.results import CommandResult
from jarvis.core.speech import SpeechService


class CommandRouter:
    def __init__(
        self,
        applications: ApplicationActions,
        routines: RoutineActions,
        speech: SpeechService,
    ) -> None:
        self.applications = applications
        self.routines = routines
        self.speech = speech

    def handle(self, text: str) -> CommandResult:
        normalized = self._normalize(text)

        if normalized in {"modo gaming", "activa modo gaming", "activar modo gaming"}:
            return self.routines.run("gaming")

        if normalized in {"voces", "listar voces", "mostrar voces"}:
            voices = self.speech.voices()
            if not voices:
                return CommandResult(
                    "No hay voces locales disponibles. Instala una voz de Windows.",
                    success=False,
                )
            options = " | ".join(f"voz {number}: {name}" for number, name in voices)
            return CommandResult(options, speak=False)

        match = re.fullmatch(r"voz\s+(\d+)", normalized)
        if match:
            number = int(match.group(1))
            selected = self.speech.select_voice(number)
            if selected is None:
                return CommandResult(
                    "No existe esa voz. Escribe 'voces' para ver las disponibles.",
                    success=False,
                )
            return CommandResult(f"Voz {number} seleccionada: {selected}.")

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
