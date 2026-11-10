"""Music search actions."""

from __future__ import annotations

import os
import urllib.parse
import webbrowser

from jarvis.core.results import CommandResult


class MusicActions:
    def play(self, query: str, service: str = "spotify") -> CommandResult:
        query = query.strip(" .,!?:;\"'")
        if not query:
            return CommandResult("Decime qué canción querés reproducir.", success=False)

        encoded = urllib.parse.quote(query)
        if service == "spotify":
            target = f"spotify:search:{encoded}"
            try:
                if os.name == "nt":
                    os.startfile(target)  # type: ignore[attr-defined]
                else:
                    webbrowser.open(target)
            except OSError:
                webbrowser.open(f"https://open.spotify.com/search/{encoded}")
            return CommandResult(f"Buscando {query} en Spotify.")

        if service in {"youtube", "youtube music", "youtube_music"}:
            webbrowser.open(
                f"https://music.youtube.com/search?q={encoded}"
            )
            return CommandResult(f"Buscando {query} en YouTube Music.")

        return CommandResult(
            f"No tengo configurado el servicio musical '{service}'.",
            success=False,
        )
