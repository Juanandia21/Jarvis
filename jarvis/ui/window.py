"""Initial visual interface for Jarvis."""

from __future__ import annotations

from threading import Thread

from jarvis.core.application import JarvisApplication
from jarvis.core.listener import SpeechListener


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
            listening_changed = Signal(bool)

            def __init__(self) -> None:
                super().__init__()
                self.setWindowTitle("Jarvis")
                self.setMinimumSize(620, 480)
                self.setStyleSheet(
                    """
                    QDialog { background: #10151f; color: #e7eef8; }
                    QLabel#title { font-size: 28px; font-weight: bold; color: #78c7ff; }
                    QLabel#state { color: #9fb3c8; }
                    QPlainTextEdit, QLineEdit {
                        background: #182232; color: #e7eef8;
                        border: 1px solid #2c405b; border-radius: 6px;
                        padding: 8px;
                    }
                    QPushButton {
                        background: #246da8; color: white; border: 0;
                        border-radius: 6px; padding: 10px 16px;
                    }
                    QPushButton:hover { background: #3189ce; }
                    """
                )

                title = QLabel("JARVIS")
                title.setObjectName("title")
                title.setAlignment(Qt.AlignCenter)
                self.state = QLabel("Listo")
                self.state.setObjectName("state")
                self.state.setAlignment(Qt.AlignCenter)
                self.history = QPlainTextEdit()
                self.history.setReadOnly(True)
                self.input = QLineEdit()
                self.input.setPlaceholderText("Escribe un comando...")
                send = QPushButton("Enviar")
                listen = QPushButton("Escuchar")
                send.clicked.connect(self.submit_text)
                self.input.returnPressed.connect(self.submit_text)
                listen.clicked.connect(self.listen)
                self.listen_button = listen

                buttons = QHBoxLayout()
                buttons.addWidget(self.input)
                buttons.addWidget(send)
                buttons.addWidget(listen)
                layout = QVBoxLayout(self)
                layout.addWidget(title)
                layout.addWidget(self.state)
                layout.addWidget(self.history)
                layout.addLayout(buttons)
                self.result_ready.connect(self.show_result)
                self.listening_changed.connect(self.set_listening)

            def submit_text(self) -> None:
                text = self.input.text().strip()
                if text:
                    self.input.clear()
                    self.execute(text)

            def execute(self, text: str) -> None:
                self.history.appendPlainText(f"Tú: {text}")
                result = application.process_command(text)
                self.show_result(result.message, result.success)
                if result.speak:
                    Thread(
                        target=application.speech.say,
                        args=(result.message,),
                        daemon=True,
                    ).start()

            def listen(self) -> None:
                self.listen_button.setEnabled(False)
                self.listening_changed.emit(True)
                Thread(target=self._listen_worker, daemon=True).start()

            def _listen_worker(self) -> None:
                try:
                    text = SpeechListener().listen()
                    self.result_ready.emit(f"__COMMAND__{text}", True)
                except RuntimeError as error:
                    self.result_ready.emit(str(error), False)
                finally:
                    self.listening_changed.emit(False)

            def show_result(self, message: str, success: bool = True) -> None:
                if message.startswith("__COMMAND__"):
                    self.execute(message.removeprefix("__COMMAND__"))
                    return
                prefix = "Jarvis" if success else "Error"
                self.history.appendPlainText(f"{prefix}: {message}")
                self.state.setText("Listo" if success else message)

            def set_listening(self, listening: bool) -> None:
                self.listen_button.setEnabled(not listening)
                self.state.setText("Escuchando..." if listening else "Listo")

        self._window = Window()

    def show(self) -> None:
        self._window.show()

    def exec(self) -> int:
        from PySide6.QtWidgets import QApplication

        return QApplication.instance().exec()
