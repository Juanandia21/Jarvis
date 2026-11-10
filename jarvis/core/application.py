"""Application orchestration and the initial test console."""

from __future__ import annotations

from jarvis.config import JarvisConfig
from jarvis.core.command_router import CommandRouter
from jarvis.core.speech import SpeechService
from jarvis.actions.applications import ApplicationActions
from jarvis.actions.routines import RoutineActions
from jarvis.ui.status import StatusUI


class JarvisApplication:
    def __init__(self, config: JarvisConfig) -> None:
        self.ui = StatusUI()
        self.speech = SpeechService()
        self.actions = ApplicationActions(config.apps)
        self.routines = RoutineActions(config.routines, self.actions)
        self.router = CommandRouter(self.actions, self.routines)

    def run(self) -> None:
        self.ui.show("ready", "Jarvis listo. Escribe un comando o 'salir'.")
        self.speech.say("Jarvis listo.")

        while True:
            try:
                text = input("Tú > ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not text:
                continue
            if text.casefold() in {"salir", "exit", "quit"}:
                break

            self.ui.show("processing", "Procesando...")
            result = self.router.handle(text)
            self.ui.show("ready", result.message)
            self.speech.say(result.message)

        self.ui.show("stopped", "Jarvis apagado.")
