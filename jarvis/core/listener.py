"""Optional push-to-talk speech recognition."""

from __future__ import annotations

import threading


class SpeechListener:
    def listen(self, language: str = "es-ES") -> str:
        try:
            import speech_recognition as sr
        except ImportError as error:
            raise RuntimeError(
                "Falta SpeechRecognition. Ejecuta 'pip install -r requirements.txt'."
            ) from error

        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=12)

        try:
            return recognizer.recognize_google(audio, language=language)
        except sr.UnknownValueError as error:
            raise RuntimeError("No pude entender lo que dijiste.") from error
        except sr.RequestError as error:
            raise RuntimeError("El reconocimiento necesita conexión a internet.") from error

    def listen_for_wake_word(
        self,
        on_command,
        on_state,
        stop_event: threading.Event,
        wake_word: str = "jarvis",
        language: str = "es-ES",
    ) -> None:
        try:
            import speech_recognition as sr
        except ImportError as error:
            on_state("Falta SpeechRecognition para activar por voz.")
            return

        recognizer = sr.Recognizer()
        recognizer.dynamic_energy_threshold = True
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                on_state(f"Di '{wake_word}' para activar")
                while not stop_event.is_set():
                    try:
                        audio = recognizer.listen(
                            source,
                            timeout=1,
                            phrase_time_limit=5,
                        )
                    except sr.WaitTimeoutError:
                        continue

                    try:
                        text = recognizer.recognize_google(
                            audio,
                            language=language,
                        ).strip()
                    except (sr.UnknownValueError, sr.RequestError):
                        continue

                    lowered = text.casefold()
                    if wake_word not in lowered:
                        continue
                    command = text[lowered.index(wake_word) + len(wake_word):].strip(" ,.!?")
                    on_state("Escuchando comando...")
                    if not command:
                        try:
                            command = self._listen_command(
                                recognizer,
                                source,
                                sr,
                                language,
                            )
                        except RuntimeError as error:
                            on_state(str(error))
                            continue
                    on_command(command)
                    on_state(f"Di '{wake_word}' para activar")
        except (OSError, RuntimeError) as error:
            on_state(f"Micrófono no disponible: {error}")

    @staticmethod
    def _listen_command(recognizer, source, sr, language: str) -> str:
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=12)
            return recognizer.recognize_google(audio, language=language).strip()
        except sr.WaitTimeoutError as error:
            raise RuntimeError("No escuché ningún comando.") from error
        except sr.UnknownValueError as error:
            raise RuntimeError("No pude entender el comando.") from error
        except sr.RequestError as error:
            raise RuntimeError("El reconocimiento necesita internet.") from error
