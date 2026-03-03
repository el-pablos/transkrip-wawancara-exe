"""State management untuk UI — centralized state biar gampang di-test."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AppState:
    """State aplikasi yang di-share antar widget."""

    # Input
    input_files: list[Path] = field(default_factory=list)
    output_dir: Path = field(default_factory=lambda: Path("output"))

    # Config
    language: str = "id"
    model_size: str = "base"
    formats: list[str] = field(default_factory=lambda: ["txt"])
    use_cache: bool = True
    remove_filler: bool = False
    diarization_mode: str = "none"  # none / heuristic

    # TXT options (default bersih)
    txt_include_timestamps: bool = False
    txt_include_speaker: bool = False

    # Progress
    is_processing: bool = False
    current_stage: str = ""
    progress: float = 0.0

    # Results
    results: list[dict] = field(default_factory=list)
    error_message: str = ""
