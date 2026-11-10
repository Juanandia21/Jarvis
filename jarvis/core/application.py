"""Application orchestration and the initial test console."""

from __future__ import annotations

from jarvis.config import JarvisConfig
from jarvis.core.command_router import CommandRouter
from jarvis.core.speech import SpeechService
from jarvis.actions.applications import ApplicationActions
from jarvis.actions.routines import RoutineActions
from jarvis.actions.music import MusicActions
from jarvis.ui.status import StatusUI


class JarvisApplication:
    def __init__(self, config: JarvisConfig) -> None:
        self.ui = StatusUI()
        self.speech = SpeechService()
        self.actions = ApplicationActions(config.apps)
        self.routines = RoutineActions(config.routines, self.actions)
        self.music = MusicActions()
        self.router = CommandRouter(self.actions, self.routines, self.speech, self.music)
        self.window = None

    def process_command(self, text: str):
        return self.router.handle(text)

    def run_console(self) -> None:
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
            result = self.process_command(text)
            self.ui.show("ready", result.message)
            if result.speak:
                self.speech.say(result.message)

        self.ui.show("stopped", "Jarvis apagado.")

    def run_ui(self) -> None:
        from jarvis.ui.window import JarvisWindow

        self.window = JarvisWindow(self)
        self.window.show()
