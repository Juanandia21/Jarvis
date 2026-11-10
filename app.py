"""Entry point for the new Jarvis application."""

import sys

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from jarvis.config import load_config
from jarvis.core.application import JarvisApplication


def main() -> None:
    config = load_config()
    application = JarvisApplication(config)
    if "--console" in sys.argv:
        application.run_console()
    else:
        try:
            from PySide6.QtWidgets import QApplication
        except ImportError:
            print("Falta PySide6. Usa 'pip install -r requirements.txt'.")
            print("Como alternativa: python app.py --console")
            raise SystemExit(1)
        qt_app = QApplication(sys.argv)
        application.run_ui()
        raise SystemExit(qt_app.exec())


if __name__ == "__main__":
    main()
