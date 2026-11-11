"""Optional local conversation provider backed by Ollama."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from jarvis.core.memory import ConversationMemory


class ConversationService:
    def __init__(
        self,
        memory: ConversationMemory,
        model: str = "qwen2.5:3b",
        endpoint: str = "http://127.0.0.1:11434/api/chat",
    ) -> None:
        self.memory = memory
        self.model = model
        self.endpoint = endpoint

    def respond(self, text: str) -> str | None:
        self.memory.add("user", text)
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres Jarvis, un asistente personal para Windows. "
                        "Responde en español, de forma breve, natural y útil. "
                        "No afirmes haber ejecutado acciones que no ejecutaste."
                    ),
                },
                *[
                    {"role": role, "content": content}
                    for role, content in self.memory.recent()
                ],
            ],
            "stream": False,
            "options": {"temperature": 0.6},
        }
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                body = json.loads(response.read().decode("utf-8"))
            answer = body["message"]["content"].strip()
        except (
            urllib.error.URLError,
            TimeoutError,
            OSError,
            KeyError,
            TypeError,
            json.JSONDecodeError,
        ):
            return None

        if not answer:
            return None
        self.memory.add("assistant", answer)
        return answer
