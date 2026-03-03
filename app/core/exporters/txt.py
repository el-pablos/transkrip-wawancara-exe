"""Exporter TXT — teks polos dari hasil transkrip (default bersih tanpa timestamp/speaker)."""

from __future__ import annotations

from pathlib import Path

from app.core.engines.base import TranscriptResult


def export_txt(
    result: TranscriptResult,
    output_path: str | Path,
    include_timestamps: bool = False,
    include_speaker: bool = False,
) -> Path:
    """Export transkrip ke file .txt.

    Default: teks bersih tanpa timestamp dan speaker.
    Opsi advanced bisa diaktifkan via parameter.

    Args:
        result: Hasil transkrip.
        output_path: Path file output.
        include_timestamps: Sertakan timestamp [MM:SS].
        include_speaker: Sertakan label speaker [S1].

    Returns:
        Path ke file yang dibuat.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    for seg in result.segments:
        parts: list[str] = []
        if include_timestamps:
            ts = _format_ts(seg.start)
            parts.append(f"[{ts}]")
        if include_speaker and seg.speaker:
            parts.append(f"[{seg.speaker}]")
        parts.append(seg.text)
        lines.append(" ".join(parts))

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path


def _format_ts(seconds: float) -> str:
    """Format detik ke MM:SS."""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"
