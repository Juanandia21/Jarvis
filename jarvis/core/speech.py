"""Speech output with natural Edge neural voices and a Windows fallback."""

from __future__ import annotations

import asyncio
import os
import subprocess
import tempfile
import threading


EDGE_VOICES = (
    ("es-ES-AlvaroNeural", "Álvaro - español de España"),
    ("es-ES-ElviraNeural", "Elvira - español de España"),
    ("es-MX-JorgeNeural", "Jorge - español de México"),
    ("es-MX-DaliaNeural", "Dalia - español de México"),
    ("es-AR-TomasNeural", "Tomás - español de Argentina"),
    ("es-AR-ElenaNeural", "Elena - español de Argentina"),
)


class SpeechService:
    def __init__(self) -> None:
        self._engine = None
        self._edge_tts = None
        self._pygame = None
        self._selected_edge_voice = EDGE_VOICES[0][0]
        self._selected_sapi_voice: str | None = None
        self._speak_lock = threading.Lock()

        try:
            import edge_tts

            self._edge_tts = edge_tts
        except ImportError:
            print("[VOZ] edge-tts no está instalado; se usará la voz de Windows.")

        try:
            import pyttsx3

            self._engine = pyttsx3.init()
        except (ImportError, RuntimeError) as error:
            print(f"[VOZ] pyttsx3 no disponible: {error}")

    def say(self, text: str) -> None:
        with self._speak_lock:
            if self._edge_tts is not None and self._say_with_edge(text):
                return
            if os.name == "nt" and self._say_with_sapi(text):
                return
            print("[VOZ] No se pudo reproducir el texto.")

    def available(self) -> bool:
        return self._edge_tts is not None or self._engine is not None

    def voices(self) -> list[tuple[int, str]]:
        return [
            (index, f"{name} [Edge neural]")
            for index, (_, name) in enumerate(EDGE_VOICES, start=1)
        ]

    def select_voice(self, number: int) -> str | None:
        if number < 1 or number > len(EDGE_VOICES):
            return None
        voice_id, name = EDGE_VOICES[number - 1]
        self._selected_edge_voice = voice_id
        return f"{name} (Edge neural)"

    def _say_with_edge(self, text: str) -> bool:
        path = ""
        try:
            import pygame

            if self._pygame is None:
                pygame.mixer.init()
                self._pygame = pygame

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as file:
                path = file.name

            asyncio.run(self._create_edge_audio(text, path))
            self._pygame.mixer.music.load(path)
            self._pygame.mixer.music.play()
            while self._pygame.mixer.music.get_busy():
                import time

                time.sleep(0.05)
            self._pygame.mixer.music.unload()
            return True
        except (ImportError, OSError, RuntimeError, asyncio.TimeoutError) as error:
            print(f"[VOZ] Edge TTS no disponible: {error}")
            return False
        finally:
            if path:
                try:
                    os.remove(path)
                except OSError:
                    pass

    async def _create_edge_audio(self, text: str, path: str) -> None:
        communicate = self._edge_tts.Communicate(
            text,
            voice=self._selected_edge_voice,
            rate="+5%",
        )
        await communicate.save(path)

    def _say_with_sapi(self, text: str) -> bool:
        voice = self._selected_sapi_voice or ""
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
