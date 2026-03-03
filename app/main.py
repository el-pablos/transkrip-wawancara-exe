"""Entry point untuk UI desktop GUI Voice To Text."""

import sys


def main() -> None:
    """Launch PySide6 UI dengan tema modern."""
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    # High DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("GUI Voice To Text")

    from app.ui.theme import apply_theme
    from app.ui.window import MainWindow

    window = MainWindow()
    apply_theme("dark")
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
