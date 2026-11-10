"""Optional text-to-speech service.

The first version remains usable without any audio dependency. When
``pyttsx3`` is installed on Windows, responses are spoken locally.
"""

from __future__ import annotations

import os
import subprocess


class SpeechService:
    def __init__(self) -> None:
        self._engine = None
        self._selected_voice: str | None = None
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
        except (ImportError, RuntimeError) as error:
            print(f"[VOZ] pyttsx3 no disponible: {error}")
            pass

    def say(self, text: str) -> None:
        if os.name == "nt" and self._say_with_sapi(text):
            return
        if self._engine is None:
            print("[VOZ] No hay un motor de voz disponible.")
            return
        try:
            if self._selected_voice:
                self._engine.setProperty("voice", self._selected_voice)
            self._engine.say(text)
            self._engine.runAndWait()
        except (RuntimeError, OSError) as error:
            print(f"[VOZ] No se pudo reproducir el texto: {error}")

    def available(self) -> bool:
        return self._engine is not None or os.name == "nt"

    def voices(self) -> list[tuple[int, str]]:
        if self._engine is not None:
            result = []
            for index, voice in enumerate(self._engine.getProperty("voices")):
                name = getattr(voice, "name", None) or getattr(voice, "id", "Voz")
                result.append((index + 1, str(name)))
            return result
        return []

    def select_voice(self, number: int) -> str | None:
        if self._engine is None:
            return None
        voices = self._engine.getProperty("voices")
        if number < 1 or number > len(voices):
            return None
        voice = voices[number - 1]
        self._selected_voice = str(getattr(voice, "name", voice.id))
        self._engine.setProperty("voice", voice.id)
        return self._selected_voice

    def _say_with_sapi(self, text: str) -> bool:
        """Use Windows SAPI directly, avoiding pyttsx3 event-loop issues."""
        voice = self._selected_voice or ""
        script = (
            "Add-Type -AssemblyName System.Speech; "
            "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$voice = '{voice.replace(chr(39), chr(39) * 2)}'; "
            "if ($voice) { $s.SelectVoice($voice) }; "
            f"$s.Speak('{text.replace(chr(39), chr(39) * 2)}');"
        )
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as error:
            print(f"[VOZ] No se pudo iniciar SAPI: {error}")
            return False
        if result.returncode != 0:
            print(f"[VOZ] SAPI devolvió un error: {result.stderr.strip()}")
            return False
        return True
