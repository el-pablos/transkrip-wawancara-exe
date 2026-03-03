"""Chunking module — potong file audio panjang jadi bagian-bagian kecil.

Dipakai supaya file 1-3 jam tetap aman, RAM tidak jebol, dan progress lebih granular.
"""

from __future__ import annotations

import logging
import subprocess
import tempfile
from pathlib import Path

from app.core.ffmpeg import find_ffmpeg

logger = logging.getLogger(__name__)

# Default: 10 menit per chunk
DEFAULT_CHUNK_SECONDS = 600

# Threshold: file > 20 menit di-chunk
CHUNK_THRESHOLD_SECONDS = 1200
CHUNK_THRESHOLD_SIZE_MB = 200


def should_chunk(duration: float, file_size_bytes: int = 0) -> bool:
    """Tentukan apakah file perlu di-chunk.

    Args:
        duration: Durasi file dalam detik.
        file_size_bytes: Ukuran file dalam bytes (opsional).

    Returns:
        True jika file sebaiknya di-chunk.
    """
    if duration > CHUNK_THRESHOLD_SECONDS:
        return True
    if file_size_bytes > CHUNK_THRESHOLD_SIZE_MB * 1024 * 1024:
        return True
    return False


def iterate_audio_chunks(
    input_path: str | Path,
    chunk_seconds: int = DEFAULT_CHUNK_SECONDS,
    total_duration: float = 0.0,
    sample_rate: int = 16000,
    channels: int = 1,
) -> list[Path]:
    """Potong file audio jadi beberapa chunk WAV.

    Gunakan ffmpeg -ss dan -t untuk extract potongan langsung ke WAV temp.

    Args:
        input_path: Path ke file audio (sudah WAV atau belum).
        chunk_seconds: Durasi tiap chunk dalam detik.
        total_duration: Durasi total file. Jika 0, akan diprobe.
        sample_rate: Sample rate output.
        channels: Jumlah channel output.

    Returns:
        List path ke file WAV chunk di temp directory.

    Raises:
        FileNotFoundError: Jika ffmpeg tidak ditemukan.
        RuntimeError: Jika chunk extraction gagal.
    """
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        raise FileNotFoundError("ffmpeg tidak ditemukan untuk chunking.")

    input_path = Path(input_path)

    if total_duration <= 0:
        from app.core.ffmpeg import probe_duration
        try:
            total_duration = probe_duration(input_path)
        except Exception:
            # Fallback: anggap 1 jam
            total_duration = 3600.0

    chunks: list[Path] = []
    temp_dir = Path(tempfile.mkdtemp(prefix="transkrip_chunks_"))
    offset = 0.0
    chunk_index = 0

    while offset < total_duration:
        chunk_path = temp_dir / f"chunk_{chunk_index:04d}.wav"

        cmd = [
            ffmpeg,
            "-y",
            "-ss", str(offset),
            "-i", str(input_path),
            "-t", str(chunk_seconds),
            "-ar", str(sample_rate),
            "-ac", str(channels),
            "-c:a", "pcm_s16le",
            str(chunk_path),
        ]

        # Timeout per chunk: worst case 3x durasi chunk + buffer
        timeout = max(300, chunk_seconds * 3 + 120)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if result.returncode != 0:
            logger.warning("Chunk %d extraction warning: %s", chunk_index, result.stderr[:200])
            # Cek apakah file terbuat walau return code error (bisa terjadi di akhir file)
            if not chunk_path.exists() or chunk_path.stat().st_size == 0:
                break
        
        if chunk_path.exists() and chunk_path.stat().st_size > 0:
            chunks.append(chunk_path)
            logger.info("Chunk %d: offset=%.1fs, path=%s", chunk_index, offset, chunk_path)

        offset += chunk_seconds
        chunk_index += 1

    logger.info("Total %d chunk dari file %s (durasi=%.1fs)", len(chunks), input_path.name, total_duration)
    return chunks


def cleanup_chunks(chunks: list[Path]) -> None:
    """Hapus file chunk temp dan folder-nya.

    Args:
        chunks: List path ke chunk files.
    """
    for chunk in chunks:
        try:
            chunk.unlink(missing_ok=True)
        except Exception:
            pass

    # Hapus temp dir kalau kosong
    if chunks:
        try:
            chunks[0].parent.rmdir()
        except Exception:
            pass
