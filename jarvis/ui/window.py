"""Minimal visual interface with wake-word activation."""

from __future__ import annotations

import threading
from threading import Thread

from jarvis.core.application import JarvisApplication
from jarvis.core.listener import SpeechListener
from jarvis.ui.orb import StatusOrb


class JarvisWindow:
    def __init__(self, application: JarvisApplication) -> None:
        from PySide6.QtCore import Qt, Signal
        from PySide6.QtWidgets import (
            QDialog,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QPushButton,
            QPlainTextEdit,
            QVBoxLayout,
        )

        class Window(QDialog):
            result_ready = Signal(str, bool)
            state_changed = Signal(str)

            def __init__(self) -> None:
                super().__init__()
                self.setWindowTitle("Jarvis")
                self.setMinimumSize(640, 620)
                self.setStyleSheet(
                    """
                    QDialog { background: #0b1120; color: #e7eef8; }
                    QLabel#title { font-size: 30px; font-weight: bold; color: #dbeafe; }
                    QLabel#state { color: #93c5fd; font-size: 14px; }
                    QPlainTextEdit, QLineEdit {
                        background: #111c31; color: #e7eef8;
                        border: 1px solid #263d60; border-radius: 10px;
                        padding: 9px;
                    }
                    QPushButton {
                        background: #1d4ed8; color: white; border: 0;
                        border-radius: 8px; padding: 10px 16px;
                    }
                    QPushButton:hover { background: #2563eb; }
                    QPushButton:checked { background: #0e7490; }
                    """
                )
                self.stop_event = threading.Event()
                self.orb = StatusOrb().widget
                self.state = QLabel("Di 'Jarvis' para activar")
                self.state.setObjectName("state")
                self.state.setAlignment(Qt.AlignCenter)
                title = QLabel("JARVIS")
                title.setObjectName("title")
                title.setAlignment(Qt.AlignCenter)
                self.history = QPlainTextEdit()
                self.history.setReadOnly(True)
                self.input = QLineEdit()
                self.input.setPlaceholderText("Escribe un comando...")
                send = QPushButton("Enviar")
                listen = QPushButton("Escuchar")
                listen.setCheckable(True)
                self.listen_button = listen
                send.clicked.connect(self.submit_text)
                self.input.returnPressed.connect(self.submit_text)
                listen.clicked.connect(self.listen)
                self.result_ready.connect(self.show_result)
                self.state_changed.connect(self.set_state)

                buttons = QHBoxLayout()
                buttons.addWidget(self.input)
                buttons.addWidget(send)
                buttons.addWidget(listen)
                layout = QVBoxLayout(self)
                layout.addWidget(title)
                layout.addWidget(self.orb)
                layout.addWidget(self.state)
                layout.addWidget(self.history)
                layout.addLayout(buttons)
                self.start_wake_listener()

            def start_wake_listener(self) -> None:
                Thread(
                    target=SpeechListener().listen_for_wake_word,
                    args=(self._voice_command, self._voice_state, self.stop_event),
                    daemon=True,
                ).start()

            def _voice_command(self, text: str) -> None:
                self.result_ready.emit(f"__COMMAND__{text}", True)

            def _voice_state(self, state: str) -> None:
                self.state_changed.emit(state)

            def submit_text(self) -> None:
                text = self.input.text().strip()
                if text:
                    self.input.clear()
                    self.execute(text)

            def execute(self, text: str) -> None:
                self.history.appendPlainText(f"Tú: {text}")
                self.set_state("Procesando...")
                result = application.process_command(text)
                self.show_result(result.message, result.success)
                if result.speak:
                    self.set_state("Hablando...")
                    Thread(
                        target=self._speak_result,
                        args=(result.message,),
                        daemon=True,
                    ).start()

            def _speak_result(self, message: str) -> None:
                application.speech.say(message)
                self.state_changed.emit("Di 'Jarvis' para activar")

            def listen(self) -> None:
                if self.listen_button.isChecked():
                    self.set_state("Escuchando...")
                    Thread(target=self._listen_worker, daemon=True).start()
                else:
                    self.set_state("Di 'Jarvis' para activar")

            def _listen_worker(self) -> None:
                try:
                    text = SpeechListener().listen()
                    self.result_ready.emit(f"__COMMAND__{text}", True)
                except RuntimeError as error:
                    self.result_ready.emit(str(error), False)
                finally:
                    self.listen_button.setChecked(False)

            def show_result(self, message: str, success: bool = True) -> None:
                if message.startswith("__COMMAND__"):
                    self.execute(message.removeprefix("__COMMAND__"))
                    return
                prefix = "Jarvis" if success else "Error"
                self.history.appendPlainText(f"{prefix}: {message}")
                if not success:
                    self.set_state(message)

            def set_state(self, state: str) -> None:
                self.state.setText(state)
                lowered = state.casefold()
                if "escuch" in lowered:
                    self.orb.set_state("listening")
                elif "proces" in lowered:
                    self.orb.set_state("processing")
                elif "habland" in lowered:
                    self.orb.set_state("speaking")
                elif "error" in lowered or "no pude" in lowered:
                    self.orb.set_state("error")
                elif "activar" in lowered:
                    self.orb.set_state("wake")
                else:
                    self.orb.set_state("idle")

            def closeEvent(self, event) -> None:
                self.stop_event.set()
                event.accept()

        self._window = Window()

    def show(self) -> None:
        self._window.show()
