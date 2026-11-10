"""Entry point for the new Jarvis application.

The original ``jarvis_mvp.py`` remains untouched as a historical MVP.
This application starts with a lightweight text console so the command
engine can be tested before adding wake-word and speech recognition.
"""

from jarvis.config import load_config
from jarvis.core.application import JarvisApplication


def main() -> None:
    config = load_config()
    application = JarvisApplication(config)
    application.run()


if __name__ == "__main__":
    main()
