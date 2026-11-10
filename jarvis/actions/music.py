"""Music search actions."""

from __future__ import annotations

import os
import urllib.parse
import webbrowser

from jarvis.core.results import CommandResult


class MusicActions:
    def play(
        self,
        query: str,
        service: str = "spotify",
        deferred: bool = False,
    ) -> CommandResult:
        query = query.strip(" .,!?:;\"'")
        if not query:
            return CommandResult("Decime qué canción querés reproducir.", success=False)

        encoded = urllib.parse.quote(query)
        if service == "spotify":
            target = f"spotify:search:{encoded}"
            def open_search() -> None:
                if self._play_spotify(query):
                    return
                try:
                    if os.name == "nt":
                        os.startfile(target)  # type: ignore[attr-defined]
                    else:
                        webbrowser.open(target)
                except OSError:
                    webbrowser.open(f"https://open.spotify.com/search/{encoded}")

            return CommandResult(
                f"Reproduciendo {query} en Spotify.",
                action=open_search if deferred else None,
            )

        if service in {"youtube", "youtube music", "youtube_music"}:
            return CommandResult(
                f"Buscando {query} en YouTube Music.",
                action=lambda: webbrowser.open(
                    f"https://music.youtube.com/search?q={encoded}"
                ) if deferred else None,
            )

        return CommandResult(
            f"No tengo configurado el servicio musical '{service}'.",
            success=False,
        )

    @staticmethod
    def _play_spotify(query: str) -> bool:
        client_id = os.environ.get("SPOTIFY_CLIENT_ID")
        client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
        if not client_id or not client_secret:
            return False
        try:
            import spotipy
            from spotipy.oauth2 import SpotifyOAuth

            spotify = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=os.environ.get(
                        "SPOTIFY_REDIRECT_URI",
                        "http://127.0.0.1:8888/callback",
                    ),
                    scope="user-read-playback-state,user-modify-playback-state",
                    cache_path=os.path.expanduser("~/.jarvis_spotify_cache"),
                )
            )
            tracks = spotify.search(q=query, type="track", limit=1)["tracks"]["items"]
            if not tracks:
                return False
            devices = spotify.devices()["devices"]
            active = next((device for device in devices if device["is_active"]), None)
            if active is None and not devices:
                return False
            device_id = active["id"] if active else devices[0]["id"]
            spotify.start_playback(device_id=device_id, uris=[tracks[0]["uri"]])
            return True
        except (ImportError, OSError, KeyError, TypeError, ValueError) as error:
            print(f"[MUSICA] Spotify API no disponible: {error}")
            return False
