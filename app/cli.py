"""CLI entry point untuk batch transkrip lewat terminal."""

from __future__ import annotations

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="transkrip",
        description="Transkrip wawancara/sidang dari audio/video ke teks — CLI mode.",
    )
    parser.add_argument("input", nargs="+", help="File atau folder audio/video yang mau ditranskrip.")
    parser.add_argument("-o", "--output-dir", default="output", help="Folder output (default: output/).")
    parser.add_argument("-f", "--format", nargs="+", default=["txt"], help="Format export: txt md srt vtt json docx.")
    parser.add_argument("-l", "--language", default="id", help="Kode bahasa (default: id).")
    parser.add_argument("-m", "--model", default="base", help="Model size: tiny/base/small/medium/large-v3.")
    parser.add_argument("--no-cache", action="store_true", help="Skip Redis cache.")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    print(f"[CLI] Input: {args.input}")
    print(f"[CLI] Output dir: {args.output_dir}")
    print(f"[CLI] Format: {args.format}")
    print(f"[CLI] Language: {args.language}")
    print(f"[CLI] Model: {args.model}")

    # Pipeline akan diimplementasi di langkah berikutnya
    from app.core.pipeline import run_pipeline

    for path in args.input:
        run_pipeline(
            input_path=path,
            output_dir=args.output_dir,
            formats=args.format,
            language=args.language,
            model_size=args.model,
            use_cache=not args.no_cache,
        )


if __name__ == "__main__":
    main()
