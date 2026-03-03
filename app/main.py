"""Entry point untuk UI desktop Transkrip Wawancara."""

import sys


def main() -> None:
    """Launch PySide6 UI."""
    from PySide6.QtWidgets import QApplication

    from app.ui.window import MainWindow

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
