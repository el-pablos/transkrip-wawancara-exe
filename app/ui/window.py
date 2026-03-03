"""Main window UI — GUI Voice To Text — modern responsive layout."""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.core.pipeline import run_pipeline
from app.ui.state import AppState
from app.ui.theme import apply_theme, toggle_theme
from app.ui.widgets import (
    ConfigPanel,
    FileDropZone,
    FileTable,
    LogPanel,
    PreviewPanel,
    ProgressPanel,
)

logger = logging.getLogger(__name__)


class TranscribeWorker(QObject):
    """Worker thread buat transkrip supaya UI tidak freeze."""

    progress = Signal(str, float)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, file_path: Path, state: AppState) -> None:
        super().__init__()
        self.file_path = file_path
        self.state = state

    @Slot()
    def run(self) -> None:
        try:
            result = run_pipeline(
                input_path=self.file_path,
                output_dir=self.state.output_dir,
                formats=self.state.formats,
                language=self.state.language,
                model_size=self.state.model_size,
                use_cache=self.state.use_cache,
                remove_filler=self.state.remove_filler,
                diarization_mode=self.state.diarization_mode,
                txt_include_timestamps=self.state.txt_include_timestamps,
                txt_include_speaker=self.state.txt_include_speaker,
                progress_callback=self._on_progress,
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def _on_progress(self, stage: str, progress: float) -> None:
        self.progress.emit(stage, progress)


class MainWindow(QMainWindow):
    """Window utama GUI Voice To Text — layout modern responsif."""

    def __init__(self) -> None:
        super().__init__()
        self.state = AppState()
        self._threads: list[QThread] = []

        self.setWindowTitle("GUI Voice To Text")
        self.setMinimumSize(900, 650)
        self.resize(1100, 720)

        self._setup_ui()
        self._setup_logging()

        # Apply tema default
        apply_theme("dark")

    # ──────────────────────────────────────────────────────────
    # UI Setup
    # ──────────────────────────────────────────────────────────
    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(8, 8, 8, 4)
        root_layout.setSpacing(6)

        # ── Top bar ──────────────────────────────
        top_bar = QHBoxLayout()
        title = QLabel("GUI Voice To Text")
        title.setObjectName("titleLabel")
        top_bar.addWidget(title)
        top_bar.addStretch()

        self.btn_theme = QPushButton("🌙 Tema")
        self.btn_theme.setFixedWidth(90)
        self.btn_theme.clicked.connect(self._toggle_theme)
        top_bar.addWidget(self.btn_theme)

        self.btn_open_output = QPushButton("📂 Buka Output")
        self.btn_open_output.clicked.connect(self._open_output_dir)
        top_bar.addWidget(self.btn_open_output)

        root_layout.addLayout(top_bar)

        # ── Splitter utama (kiri/kanan) ──────────
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ─── Left panel ─────────────────────────
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # Drop zone
        self.drop_zone = FileDropZone()
        self.drop_zone.files_dropped.connect(self._on_files_dropped)
        left_layout.addWidget(self.drop_zone)

        # Tombol file
        file_btn_row = QHBoxLayout()
        self.btn_add_files = QPushButton("➕ Tambah File")
        self.btn_add_files.clicked.connect(self._browse_files)
        file_btn_row.addWidget(self.btn_add_files)

        self.btn_add_folder = QPushButton("📁 Tambah Folder")
        self.btn_add_folder.clicked.connect(self._browse_folder)
        file_btn_row.addWidget(self.btn_add_folder)

        self.btn_remove_selected = QPushButton("✖ Hapus Pilihan")
        self.btn_remove_selected.clicked.connect(self._remove_selected)
        file_btn_row.addWidget(self.btn_remove_selected)

        self.btn_clear = QPushButton("🗑️ Clear All")
        self.btn_clear.clicked.connect(self._clear_files)
        file_btn_row.addWidget(self.btn_clear)
        left_layout.addLayout(file_btn_row)

        # File table
        self.file_table = FileTable()
        left_layout.addWidget(self.file_table)

        # Progress
        self.progress_panel = ProgressPanel()
        left_layout.addWidget(self.progress_panel)

        # Start button
        action_row = QHBoxLayout()
        self.btn_start = QPushButton("▶️ Mulai Transkrip")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.clicked.connect(self._start_transcribe)
        action_row.addWidget(self.btn_start)

        self.btn_output_dir = QPushButton("💾 Folder Output")
        self.btn_output_dir.clicked.connect(self._set_output_dir)
        action_row.addWidget(self.btn_output_dir)
        left_layout.addLayout(action_row)

        splitter.addWidget(left_widget)

        # ─── Right panel (tabs) ──────────────────
        self.tabs = QTabWidget()

        # Tab Pengaturan
        self.config_panel = ConfigPanel()
        self.tabs.addTab(self.config_panel, "⚙️ Pengaturan")

        # Tab Preview TXT
        self.preview_panel = PreviewPanel()
        self.preview_panel.btn_save.clicked.connect(self._save_preview_as)
        self.tabs.addTab(self.preview_panel, "📄 Preview TXT")

        # Tab Log
        self.log_panel = LogPanel()
        self.tabs.addTab(self.log_panel, "📋 Log")

        splitter.addWidget(self.tabs)
        splitter.setSizes([550, 450])

        root_layout.addWidget(splitter)

        # ── Status bar ───────────────────────────
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Siap — pilih file untuk mulai transkrip")

    def _setup_logging(self) -> None:
        """Setup logging ke file + UI panel."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        handler = logging.FileHandler(log_dir / "app.log", encoding="utf-8")
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

    # ──────────────────────────────────────────────────────────
    # File Management
    # ──────────────────────────────────────────────────────────
    def _on_files_dropped(self, files: list[Path]) -> None:
        for f in files:
            self.file_table.add_file(f)
        self.state.input_files.extend(files)
        self.log_panel.append_log(f"Ditambahkan {len(files)} file via drag & drop")
        self.status_bar.showMessage(f"{len(self.state.input_files)} file dalam antrian")

    def _browse_files(self) -> None:
        from app.core.ffmpeg import SUPPORTED_EXTENSIONS

        exts = " ".join(f"*{e}" for e in sorted(SUPPORTED_EXTENSIONS))
        files, _ = QFileDialog.getOpenFileNames(
            self, "Pilih File Audio/Video", "", f"Media Files ({exts});;All Files (*)"
        )
        if files:
            paths = [Path(f) for f in files]
            for p in paths:
                self.file_table.add_file(p)
            self.state.input_files.extend(paths)
            self.log_panel.append_log(f"Dipilih {len(paths)} file")
            self.status_bar.showMessage(f"{len(self.state.input_files)} file dalam antrian")

    def _browse_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Audio/Video")
        if folder:
            from app.core.ffmpeg import SUPPORTED_EXTENSIONS

            folder_path = Path(folder)
            files = [f for f in sorted(folder_path.iterdir()) if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS]
            for f in files:
                self.file_table.add_file(f)
            self.state.input_files.extend(files)
            self.log_panel.append_log(f"Folder: {len(files)} file ditemukan")
            self.status_bar.showMessage(f"{len(self.state.input_files)} file dalam antrian")

    def _remove_selected(self) -> None:
        rows = self.file_table.get_selected_rows()
        if not rows:
            return
        # Hapus dari state (reverse order)
        for row in sorted(rows, reverse=True):
            if row < len(self.state.input_files):
                self.state.input_files.pop(row)
        self.file_table.remove_rows(rows)
        self.status_bar.showMessage(f"{len(self.state.input_files)} file dalam antrian")

    def _clear_files(self) -> None:
        self.file_table.setRowCount(0)
        self.state.input_files.clear()
        self.progress_panel.reset()
        self.preview_panel.set_text("")
        self.log_panel.append_log("File list dibersihkan")
        self.status_bar.showMessage("Siap — pilih file untuk mulai transkrip")

    def _set_output_dir(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder Output")
        if folder:
            self.state.output_dir = Path(folder)
            self.log_panel.append_log(f"Output dir: {folder}")
            self.status_bar.showMessage(f"Output: {folder}")

    # ──────────────────────────────────────────────────────────
    # Transkrip
    # ──────────────────────────────────────────────────────────
    def _start_transcribe(self) -> None:
        if not self.state.input_files:
            QMessageBox.warning(self, "Peringatan", "Belum ada file yang dipilih!")
            return

        # Update state dari config panel
        self.state.formats = self.config_panel.get_formats()
        self.state.language = self.config_panel.get_language()
        self.state.model_size = self.config_panel.get_model()
        self.state.use_cache = self.config_panel.get_use_cache()
        self.state.remove_filler = self.config_panel.get_remove_filler()
        self.state.diarization_mode = self.config_panel.get_diarization_mode()
        self.state.txt_include_timestamps = self.config_panel.get_txt_include_timestamps()
        self.state.txt_include_speaker = self.config_panel.get_txt_include_speaker()

        if not self.state.formats:
            QMessageBox.warning(self, "Peringatan", "Pilih minimal satu format export!")
            return

        self._set_processing(True)
        self.state.results.clear()
        self._process_next_file(0)

    def _set_processing(self, active: bool) -> None:
        """Enable/disable tombol saat processing."""
        self.state.is_processing = active
        self.btn_start.setEnabled(not active)
        self.btn_add_files.setEnabled(not active)
        self.btn_add_folder.setEnabled(not active)
        self.btn_remove_selected.setEnabled(not active)
        self.btn_clear.setEnabled(not active)

    def _process_next_file(self, index: int) -> None:
        if index >= len(self.state.input_files):
            self._on_all_done()
            return

        file_path = self.state.input_files[index]
        self.file_table.update_status(index, "Processing...")
        self.log_panel.append_log(f"[{index + 1}/{len(self.state.input_files)}] {file_path.name}")

        thread = QThread()
        worker = TranscribeWorker(file_path, self.state)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.progress.connect(self.progress_panel.update_progress)
        worker.finished.connect(lambda r: self._on_file_done(r, index))
        worker.error.connect(lambda e: self._on_file_error(e, index))
        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)

        self._threads.append(thread)
        thread.start()

    def _on_file_done(self, result: dict, index: int) -> None:
        self.state.results.append(result)
        self.file_table.update_status(index, "✅ Selesai")

        # Update duration jika tersedia
        dur = result.get("duration", 0)
        if dur > 0:
            m, s = divmod(int(dur), 60)
            h, m = divmod(m, 60)
            dur_str = f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"
            self.file_table.update_duration(index, dur_str)

        # Update preview dengan TXT terakhir
        preview_text = result.get("preview_text", "")
        if preview_text:
            self.preview_panel.set_text(preview_text)
            self.tabs.setCurrentIndex(1)  # Beralih ke tab Preview

        self.log_panel.append_log(f"✅ Selesai: {result.get('input', 'unknown')}")
        self._process_next_file(index + 1)

    def _on_file_error(self, error: str, index: int) -> None:
        self.state.results.append({"error": error})
        self.file_table.update_status(index, "❌ Error")
        self.log_panel.append_log(f"❌ Error: {error}")
        self._process_next_file(index + 1)

    def _on_all_done(self) -> None:
        self._set_processing(False)
        self.progress_panel.update_progress("Semua selesai!", 1.0)

        success = sum(1 for r in self.state.results if "error" not in r)
        total = len(self.state.results)
        self.log_panel.append_log(f"Selesai semua! {success}/{total} berhasil.")
        self.status_bar.showMessage(f"Selesai — {success}/{total} file berhasil ditranskrip")

        QMessageBox.information(
            self,
            "Selesai",
            f"Transkrip selesai!\n{success}/{total} file berhasil.\nOutput di: {self.state.output_dir}",
        )

    # ──────────────────────────────────────────────────────────
    # Utility
    # ──────────────────────────────────────────────────────────
    def _toggle_theme(self) -> None:
        new_theme = toggle_theme()
        icon = "☀️" if new_theme == "light" else "🌙"
        self.btn_theme.setText(f"{icon} Tema")

    def _save_preview_as(self) -> None:
        text = self.preview_panel.get_text()
        if not text:
            QMessageBox.warning(self, "Peringatan", "Belum ada teks untuk disimpan!")
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Simpan TXT", "", "Text Files (*.txt);;All Files (*)"
        )
        if path:
            Path(path).write_text(text, encoding="utf-8")
            self.log_panel.append_log(f"Preview disimpan ke: {path}")

    def _open_output_dir(self) -> None:
        path = str(self.state.output_dir.resolve())
        if sys.platform == "win32":
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path])

    def _open_log_dir(self) -> None:
        path = str(Path("logs").resolve())
        if sys.platform == "win32":
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path])
