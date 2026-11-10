"""Shared command results."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable


@dataclass(frozen=True)
class CommandResult:
    message: str
    success: bool = True
    speak: bool = True
    action: Callable[[], None] | None = None
