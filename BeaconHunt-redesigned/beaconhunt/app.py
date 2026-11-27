"""BeaconHunt GUI application entry point.

Run with:

    python -m beaconhunt.app
"""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from .ui import MainWindow, styles
from .ui.main_window import __version__


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("BeaconHunt")
    app.setOrganizationName("BeaconHunt")
    app.setStyleSheet(styles.QSS)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
