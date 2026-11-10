"""Minimal status output, ready to be replaced by a visual UI."""

from __future__ import annotations


class StatusUI:
    _labels = {
        "ready": "[LISTO]",
        "processing": "[PROCESANDO]",
        "stopped": "[APAGADO]",
    }

    def show(self, state: str, message: str) -> None:
        print(f"{self._labels.get(state, '[JARVIS]')} {message}")
