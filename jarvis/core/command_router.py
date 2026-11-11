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
from jarvis.actions.music import MusicActions
from jarvis.core.conversation import ConversationService


class CommandRouter:
    def __init__(
        self,
        applications: ApplicationActions,
        routines: RoutineActions,
        speech: SpeechService,
        music: MusicActions,
        conversation: ConversationService,
    ) -> None:
        self.applications = applications
        self.routines = routines
        self.speech = speech
        self.music = music
        self.conversation = conversation

    def handle(self, text: str) -> CommandResult:
        normalized = self._normalize(text)

        if normalized in {"modo gaming", "activa modo gaming", "activar modo gaming"}:
            return self.routines.run("gaming")

        match = re.fullmatch(
            r"(?:cierra|cerrar|cierra la|apaga|termina)\s+(.+)",
            normalized,
        )
        if match:
            requested = match.group(1).strip()
            return CommandResult(
                f"Cerrando {requested}.",
                action=lambda: self.applications.close(requested),
            )

        match = re.fullmatch(
            r"(?:pon|pone|ponga|reproduce|reproducí|reproducir|escucha|escuchar)"
            r"\s+(.+?)(?:\s+en\s+(spotify|youtube music|youtube))?$",
            normalized,
        )
        if match:
            query = match.group(1)
            service = (match.group(2) or "spotify").replace(" ", "_")
            return self.music.play(
                query,
                service,
                deferred=True,
            )

        if normalized in {"voces", "listar voces", "mostrar voces"}:
            voices = self.speech.voices()
            if not voices:
                return CommandResult(
                    "Edge TTS no está instalado. Ejecuta 'pip install -r requirements.txt'.",
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

        match = re.fullmatch(r"(?:probar|test)\s+voz\s+(\d+)", normalized)
        if match:
            number = int(match.group(1))
            selected = self.speech.select_voice(number)
            if selected is None:
                return CommandResult(
                    "No existe esa voz. Escribe 'voces' para ver las disponibles.",
                    success=False,
                )
            return CommandResult(
                f"Esta es la voz {number}, {selected}. Así sonaría Jarvis con Edge neural.",
            )

        if normalized in {"probar voces", "test voces"}:
            voices = self.speech.voices()
            if not voices:
                return CommandResult(
                    "No hay voces locales disponibles.",
                    success=False,
                )
            return CommandResult(
                "Prueba de voces iniciada. Usa 'probar voz 1' para escuchar una voz.",
                speak=True,
            )

        if normalized in {
            "borra la conversación",
            "borrar conversación",
            "olvida esta conversación",
            "limpia el chat",
        }:
            self.conversation.memory.clear()
            return CommandResult("Conversación borrada.")

        match = re.fullmatch(
            r"(?:por favor\s+)?(?:abre|abrí|abrir|inicia|iniciar)\s+(.+?)(?:\s+por favor)?",
            normalized,
        )
        if match:
            requested = match.group(1)
            return CommandResult(
                f"Abriendo {requested}.",
                action=lambda: self.applications.open(requested),
            )

        answer = self.conversation.respond(text)
        if answer is not None:
            return CommandResult(answer)
        return CommandResult(
            "Todavía no tengo activado el motor conversacional local. "
            "Instala Ollama y carga el modelo configurado para poder conversar.",
            success=False,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        normalized = " ".join(text.casefold().strip().split())
        return normalized.replace("abrí ", "abre ").replace("reproducí ", "reproduce ")
