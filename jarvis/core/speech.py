"""Optional text-to-speech service.

The first version remains usable without any audio dependency. When
``pyttsx3`` is installed on Windows, responses are spoken locally.
"""

from __future__ import annotations


class SpeechService:
    def __init__(self) -> None:
        self._engine = None
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
        except (ImportError, RuntimeError):
            pass

    def say(self, text: str) -> None:
        if self._engine is None:
            return
        self._engine.say(text)
        self._engine.runAndWait()
