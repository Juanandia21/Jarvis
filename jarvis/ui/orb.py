"""Cinematic orange audio visualizer."""

from __future__ import annotations

import math


class StatusOrb:
    def __init__(self) -> None:
        from PySide6.QtCore import QTimer, Qt
        from PySide6.QtWidgets import QWidget

        class OrbWidget(QWidget):
            def __init__(self) -> None:
                super().__init__()
                self.state = "idle"
                self.phase = 0.0
                self.setAttribute(Qt.WA_TranslucentBackground)
                self.setMinimumSize(560, 500)
                self.timer = QTimer(self)
                self.timer.timeout.connect(self.animate)
                self.timer.start(24)

            def set_state(self, state: str) -> None:
                self.state = state
                self.update()

            def animate(self) -> None:
                self.phase = (self.phase + 0.095) % (math.pi * 2)
                self.update()

            def paintEvent(self, event) -> None:
                from PySide6.QtCore import QPointF
                from PySide6.QtGui import QColor, QPainter, QRadialGradient

                painter = QPainter(self)
                painter.setRenderHint(QPainter.Antialiasing)
                center = QPointF(self.width() / 2, self.height() / 2)
                colors = {
                    "idle": QColor("#b84b16"),
                    "wake": QColor("#f07b20"),
                    "listening": QColor("#ffad42"),
                    "processing": QColor("#dc641b"),
                    "speaking": QColor("#ff8c2b"),
                    "error": QColor("#b52d22"),
                }
                color = colors.get(self.state, colors["idle"])
                active = self.state in {"wake", "listening", "processing", "speaking"}
                energy = 1.0 if active else 0.45
                pulse = 1 + (0.055 + energy * 0.045) * math.sin(self.phase * 2.2)
                radius = 68 * pulse

                for ring in range(8, 0, -1):
                    ring_radius = radius + ring * 24 + 9 * math.sin(self.phase + ring)
                    alpha = 10 + (9 - ring) * 5
                    painter.setPen(QColor(color.red(), color.green(), color.blue(), alpha))
                    painter.drawEllipse(center, ring_radius, ring_radius)

                for index in range(64):
                    angle = self.phase * 0.22 + index * math.tau / 64
                    wave = (
                        math.sin(self.phase * 3.2 + index * 0.71)
                        + math.sin(self.phase * 1.4 - index * 0.29)
                    ) * (7 + energy * 13)
                    inner = radius + 92
                    outer = inner + 18 + wave
                    start = QPointF(
                        center.x() + math.cos(angle) * inner,
                        center.y() + math.sin(angle) * inner,
                    )
                    end = QPointF(
                        center.x() + math.cos(angle) * outer,
                        center.y() + math.sin(angle) * outer,
                    )
                    alpha = 75 if active else 36
                    painter.setPen(QColor(color.red(), color.green(), color.blue(), alpha))
                    painter.drawLine(start, end)

                for index in range(32):
                    angle = -self.phase * 0.45 + index * math.tau / 32
                    distance = radius + 38 + 12 * math.sin(self.phase * 2 + index)
                    point = QPointF(
                        center.x() + math.cos(angle) * distance,
                        center.y() + math.sin(angle) * distance,
                    )
                    painter.setPen(QColor(255, 190, 105, 150 if active else 70))
                    painter.drawEllipse(point, 2.5, 2.5)

                gradient = QRadialGradient(center, radius * 1.7)
                gradient.setColorAt(0, QColor(255, 245, 220, 245))
                gradient.setColorAt(0.16, QColor(255, 169, 71, 240))
                gradient.setColorAt(0.5, QColor(color.red(), color.green(), color.blue(), 220))
                gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 0))
                painter.setPen(Qt.NoPen)
                painter.setBrush(gradient)
                painter.drawEllipse(center, radius * 1.7, radius * 1.7)

                painter.setBrush(QColor(255, 218, 164, 230))
                painter.drawEllipse(center, radius * 0.34, radius * 0.34)

        self.widget = OrbWidget()
