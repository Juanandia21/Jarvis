"""Optional push-to-talk speech recognition."""

from __future__ import annotations


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
