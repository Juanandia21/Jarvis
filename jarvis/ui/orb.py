"""Animated status orb for the Jarvis interface."""

from __future__ import annotations

import math


class StatusOrb:
    def __init__(self) -> None:
        from PySide6.QtCore import QTimer
        from PySide6.QtWidgets import QWidget

        class OrbWidget(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self.state = "idle"
                self.phase = 0.0
                self.setAttribute(Qt.WA_TranslucentBackground)
                self.setMinimumSize(360, 360)
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.animate)
                self.timer.start(30)

            def set_state(self, state: str) -> None:
                self.state = state
                self.update()

            def animate(self) -> None:
                self.phase = (self.phase + 0.12) % (math.pi * 2)
                self.update()

            def paintEvent(self, event) -> None:
                from PySide6.QtCore import QPointF
                from PySide6.QtGui import QColor, QPainter, QRadialGradient

                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                painter.fillRect(self.rect(), Qt.transparent)
                center = QPointF(self.width() / 2, self.height() / 2)
                colors = {
                    "idle": QColor("#3b82f6"),
                    "wake": QColor("#22d3ee"),
                    "listening": QColor("#a78bfa"),
                    "processing": QColor("#f59e0b"),
                    "speaking": QColor("#34d399"),
                    "error": QColor("#fb7185"),
                }
                color = colors.get(self.state, colors["idle"])
                pulse = 1 + 0.08 * math.sin(self.phase * 1.7)
                if self.state in {"listening", "speaking"}:
                    pulse += 0.08 * math.sin(self.phase * 3)
                radius = 44 * pulse
                for ring in range(3, 0, -1):
                    alpha = 20 + ring * 12
                    painter.setPen(QColor(color.red(), color.green(), color.blue(), alpha))
                    ring_radius = radius + ring * 17 + 5 * math.sin(self.phase + ring)
                    painter.drawEllipse(center, ring_radius, ring_radius)
                if self.state in {"listening", "speaking"}:
                    for wave in range(12):
                        angle = self.phase * 0.7 + wave * math.pi / 6
                        distance = radius + 30 + 7 * math.sin(self.phase * 2 + wave)
                        point = QPointF(
                            center.x() + math.cos(angle) * distance,
                            center.y() + math.sin(angle) * distance,
                        )
                        painter.setPen(
                            QColor(color.red(), color.green(), color.blue(), 120)
                        )
                        painter.drawEllipse(point, 3.5, 3.5)
                gradient = QRadialGradient(center, radius)
                gradient.setColorAt(0, QColor(255, 255, 255, 230))
                gradient.setColorAt(0.25, QColor(color.red(), color.green(), color.blue(), 240))
                gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 80))
                painter.setPen(Qt.NoPen)
                painter.setBrush(gradient)
                painter.drawEllipse(center, radius, radius)

        from PySide6.QtCore import Qt

        # Keep the widget class local so PySide6 remains an optional dependency.
        self.widget = OrbWidget()
