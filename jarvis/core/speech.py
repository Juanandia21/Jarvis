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

    def available(self) -> bool:
        return self._engine is not None

    def voices(self) -> list[tuple[int, str]]:
        if self._engine is None:
            return []
        result = []
        for index, voice in enumerate(self._engine.getProperty("voices")):
            name = getattr(voice, "name", None) or getattr(voice, "id", "Voz")
            result.append((index + 1, str(name)))
        return result

    def select_voice(self, number: int) -> str | None:
        if self._engine is None:
            return None
        voices = self._engine.getProperty("voices")
        if number < 1 or number > len(voices):
            return None
        self._engine.setProperty("voice", voices[number - 1].id)
        return str(getattr(voices[number - 1], "name", voices[number - 1].id))
