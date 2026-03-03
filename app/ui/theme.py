"""Sistem tema Light/Dark untuk GUI Voice To Text."""

from __future__ import annotations

from PySide6.QtWidgets import QApplication

# ─── Warna dasar ───────────────────────────────────────────────
_DARK_BG = "#1e1e2e"
_DARK_SURFACE = "#2a2a3c"
_DARK_BORDER = "#3a3a4c"
_DARK_TEXT = "#cdd6f4"
_DARK_ACCENT = "#89b4fa"
_DARK_ACCENT_HOVER = "#74a8fc"
_DARK_SUCCESS = "#a6e3a1"
_DARK_ERROR = "#f38ba8"

_LIGHT_BG = "#f5f5f5"
_LIGHT_SURFACE = "#ffffff"
_LIGHT_BORDER = "#d0d0d0"
_LIGHT_TEXT = "#1e1e2e"
_LIGHT_ACCENT = "#1a73e8"
_LIGHT_ACCENT_HOVER = "#1565c0"
_LIGHT_SUCCESS = "#2e7d32"
_LIGHT_ERROR = "#c62828"


def _build_qss(
    bg: str,
    surface: str,
    border: str,
    text: str,
    accent: str,
    accent_hover: str,
    success: str,
    error: str,
) -> str:
    return f"""
    /* ── Global ─────────────────────────── */
    QMainWindow, QWidget {{
        background-color: {bg};
        color: {text};
        font-family: "Segoe UI", "Noto Sans", sans-serif;
        font-size: 13px;
    }}

    /* ── Splitter ────────────────────────── */
    QSplitter::handle {{
        background-color: {border};
        width: 2px;
    }}

    /* ── GroupBox ─────────────────────────── */
    QGroupBox {{
        background-color: {surface};
        border: 1px solid {border};
        border-radius: 8px;
        margin-top: 12px;
        padding: 14px 10px 10px 10px;
        font-weight: bold;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 2px 10px;
        color: {accent};
    }}

    /* ── Buttons ──────────────────────────── */
    QPushButton {{
        background-color: {surface};
        color: {text};
        border: 1px solid {border};
        border-radius: 6px;
        padding: 6px 14px;
        font-size: 13px;
    }}
    QPushButton:hover {{
        background-color: {accent};
        color: white;
        border-color: {accent};
    }}
    QPushButton:pressed {{
        background-color: {accent_hover};
    }}
    QPushButton:disabled {{
        background-color: {border};
        color: #888;
    }}
    QPushButton#btnStart {{
        background-color: {success};
        color: white;
        font-size: 14px;
        font-weight: bold;
        padding: 8px 20px;
        border: none;
    }}
    QPushButton#btnStart:hover {{
        background-color: {accent_hover};
    }}
    QPushButton#btnStart:disabled {{
        background-color: {border};
        color: #888;
    }}

    /* ── Inputs ───────────────────────────── */
    QComboBox, QLineEdit, QSpinBox {{
        background-color: {surface};
        color: {text};
        border: 1px solid {border};
        border-radius: 4px;
        padding: 4px 8px;
    }}
    QComboBox:hover, QLineEdit:hover {{
        border-color: {accent};
    }}
    QComboBox QAbstractItemView {{
        background-color: {surface};
        color: {text};
        selection-background-color: {accent};
        selection-color: white;
    }}

    /* ── Checkbox ─────────────────────────── */
    QCheckBox {{
        spacing: 6px;
        color: {text};
    }}
    QCheckBox::indicator {{
        width: 16px;
        height: 16px;
        border-radius: 3px;
        border: 1px solid {border};
        background-color: {surface};
    }}
    QCheckBox::indicator:checked {{
        background-color: {accent};
        border-color: {accent};
    }}

    /* ── TabWidget ────────────────────────── */
    QTabWidget::pane {{
        border: 1px solid {border};
        border-radius: 6px;
        background-color: {surface};
    }}
    QTabBar::tab {{
        background-color: {bg};
        color: {text};
        border: 1px solid {border};
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        padding: 6px 16px;
        margin-right: 2px;
    }}
    QTabBar::tab:selected {{
        background-color: {surface};
        color: {accent};
        font-weight: bold;
    }}
    QTabBar::tab:hover {{
        background-color: {surface};
    }}

    /* ── Table / Tree ────────────────────── */
    QTableWidget, QTableView, QHeaderView {{
        background-color: {surface};
        color: {text};
        border: 1px solid {border};
        border-radius: 4px;
        gridline-color: {border};
    }}
    QHeaderView::section {{
        background-color: {bg};
        color: {text};
        border: 1px solid {border};
        padding: 4px 8px;
        font-weight: bold;
    }}
    QTableWidget::item:selected {{
        background-color: {accent};
        color: white;
    }}

    /* ── TextEdit / PlainText ────────────── */
    QTextEdit, QPlainTextEdit {{
        background-color: {surface};
        color: {text};
        border: 1px solid {border};
        border-radius: 6px;
        padding: 6px;
        font-family: "Cascadia Code", "Consolas", monospace;
        font-size: 12px;
    }}

    /* ── ProgressBar ─────────────────────── */
    QProgressBar {{
        border: 1px solid {border};
        border-radius: 6px;
        text-align: center;
        background-color: {surface};
        color: {text};
        height: 22px;
    }}
    QProgressBar::chunk {{
        background-color: {accent};
        border-radius: 5px;
    }}

    /* ── StatusBar ────────────────────────── */
    QStatusBar {{
        background-color: {surface};
        color: {text};
        border-top: 1px solid {border};
    }}

    /* ── ScrollBar ────────────────────────── */
    QScrollBar:vertical {{
        background-color: {bg};
        width: 10px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical {{
        background-color: {border};
        border-radius: 5px;
        min-height: 30px;
    }}
    QScrollBar::handle:vertical:hover {{
        background-color: {accent};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}

    /* ── Label ────────────────────────────── */
    QLabel {{
        color: {text};
    }}
    QLabel#titleLabel {{
        font-size: 18px;
        font-weight: bold;
        color: {accent};
    }}

    /* ── Drop zone ────────────────────────── */
    QFrame#dropZone {{
        border: 2px dashed {accent};
        border-radius: 10px;
        background-color: {surface};
    }}
    QFrame#dropZone:hover {{
        border-color: {accent_hover};
        background-color: {bg};
    }}
    """


DARK_QSS = _build_qss(
    _DARK_BG, _DARK_SURFACE, _DARK_BORDER, _DARK_TEXT,
    _DARK_ACCENT, _DARK_ACCENT_HOVER, _DARK_SUCCESS, _DARK_ERROR,
)

LIGHT_QSS = _build_qss(
    _LIGHT_BG, _LIGHT_SURFACE, _LIGHT_BORDER, _LIGHT_TEXT,
    _LIGHT_ACCENT, _LIGHT_ACCENT_HOVER, _LIGHT_SUCCESS, _LIGHT_ERROR,
)


_current_theme: str = "dark"


def get_current_theme() -> str:
    """Dapatkan nama tema aktif."""
    return _current_theme


def apply_theme(theme_name: str = "dark") -> None:
    """Terapkan tema ke QApplication.

    Args:
        theme_name: 'dark' atau 'light'.
    """
    global _current_theme
    app = QApplication.instance()
    if app is None:
        return

    qss = DARK_QSS if theme_name == "dark" else LIGHT_QSS
    app.setStyleSheet(qss)
    _current_theme = theme_name


def toggle_theme() -> str:
    """Toggle antara dark dan light, return nama tema baru."""
    new_theme = "light" if _current_theme == "dark" else "dark"
    apply_theme(new_theme)
    return new_theme
