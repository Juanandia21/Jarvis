"""Jarvis cinematic desktop window."""

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
            QFrame,
            QHBoxLayout,
            QLabel,
            QVBoxLayout,
        )

        class Window(QDialog):
            result_ready = Signal(str, bool)
            state_changed = Signal(str)

            def __init__(self) -> None:
                super().__init__()
                self.setWindowTitle("Jarvis")
                self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                self.setFixedSize(760, 760)
                self.setStyleSheet(
                    """
                    QDialog {
                        background: #070808;
                        color: #f7e4c4;
                        border: 1px solid #6d3217;
                        border-radius: 22px;
                    }
                    QFrame#header {
                        background: transparent;
                        border-bottom: 1px solid #3a1c10;
                    }
                    QLabel#brand {
                        color: #ff9a3c;
                        font-size: 15px;
                        font-weight: bold;
                        letter-spacing: 3px;
                    }
                    QLabel#status {
                        color: #b8794a;
                        font-size: 12px;
                    }
                    QLabel#hint {
                        color: #704833;
                        font-size: 11px;
                    }
                    """
                )
                self.stop_event = threading.Event()
                self.orb = StatusOrb().widget

                header = QFrame()
                header.setObjectName("header")
                header_layout = QHBoxLayout(header)
                header_layout.setContentsMargins(25, 16, 25, 13)
                brand = QLabel("JARVIS  //  CORE ONLINE")
                brand.setObjectName("brand")
                self.status = QLabel("STANDBY")
                self.status.setObjectName("status")
                self.status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                header_layout.addWidget(brand)
                header_layout.addStretch()
                header_layout.addWidget(self.status)

                hint = QLabel("LISTENING FOR WAKE WORD  •  DOUBLE-CLICK TO CLOSE")
                hint.setObjectName("hint")
                hint.setAlignment(Qt.AlignCenter)

                layout = QVBoxLayout(self)
                layout.setContentsMargins(0, 0, 0, 18)
                layout.addWidget(header)
                layout.addStretch()
                layout.addWidget(self.orb, alignment=Qt.AlignCenter)
                layout.addStretch()
                layout.addWidget(hint)
                self.result_ready.connect(self.show_result)
                self.state_changed.connect(self.set_state)
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

            def execute(self, text: str) -> None:
                self.set_state("PROCESSING")
                result = application.process_command(text)
                self.show_result(result.message, result.success)
                if result.speak:
                    self.set_state("SPEAKING")
                    Thread(
                        target=self._speak_result,
                        args=(result,),
                        daemon=True,
                    ).start()
                else:
                    application.complete_command(result)

            def _speak_result(self, result) -> None:
                application.speech.say(result.message)
                application.complete_command(result)
                self.state_changed.emit("STANDBY")

            def show_result(self, message: str, success: bool = True) -> None:
                if message.startswith("__COMMAND__"):
                    self.execute(message.removeprefix("__COMMAND__"))
                    return
                if not success:
                    self.set_state("ERROR")

            def set_state(self, state: str) -> None:
                self.status.setText(state.upper())
                lowered = state.casefold()
                if "escuch" in lowered or "listening" in lowered:
                    self.orb.set_state("listening")
                elif "proces" in lowered:
                    self.orb.set_state("processing")
                elif "habland" in lowered or "speaking" in lowered:
                    self.orb.set_state("speaking")
                elif "error" in lowered:
                    self.orb.set_state("error")
                elif "activar" in lowered or "wake" in lowered:
                    self.orb.set_state("wake")
                else:
                    self.orb.set_state("idle")

            def mouseDoubleClickEvent(self, event) -> None:
                self.close()

            def closeEvent(self, event) -> None:
                self.stop_event.set()
                event.accept()

        self._window = Window()

    def show(self) -> None:
        self._window.show()
