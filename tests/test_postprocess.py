"""Test postprocess — cleanup dan segmentasi."""

from __future__ import annotations

import pytest

from app.core.engines.base import Segment, TranscriptResult
from app.core.postprocess.cleanup import cleanup_text, normalize_whitespace, remove_fillers, remove_noise_tokens
from app.core.postprocess.segmentation import heuristic_diarization, segments_merged, segments_per_sentence


class TestNormalizeWhitespace:
    def test_multiple_spaces(self) -> None:
        assert normalize_whitespace("hello   world") == "hello world"

    def test_newlines_and_tabs(self) -> None:
        assert normalize_whitespace("hello\n\tworld") == "hello world"

    def test_trim(self) -> None:
        assert normalize_whitespace("  hello  ") == "hello"


class TestRemoveNoiseTokens:
    def test_bracket_noise(self) -> None:
        assert remove_noise_tokens("hello [Music] world") == "hello world"

    def test_paren_noise(self) -> None:
        assert remove_noise_tokens("(applause) thanks") == "thanks"

    def test_asterisk_noise(self) -> None:
        assert remove_noise_tokens("*music* begin") == "begin"

    def test_clean_text(self) -> None:
        assert remove_noise_tokens("clean text here") == "clean text here"


class TestRemoveFillers:
    def test_remove_eee(self) -> None:
        result = remove_fillers("jadi eee begini")
        assert "eee" not in result

    def test_remove_anu(self) -> None:
        result = remove_fillers("terus anu itu dia")
        assert "anu" not in result

    def test_clean_text_unchanged(self) -> None:
        assert remove_fillers("kalimat bersih") == "kalimat bersih"


class TestCleanupText:
    def test_basic_cleanup(self) -> None:
        text = "hello  [Music]  world"
        assert cleanup_text(text) == "hello world"

    def test_with_filler_removal(self) -> None:
        text = "eee jadi anu begitu"
        result = cleanup_text(text, remove_filler=True)
        assert "eee" not in result
        assert "anu" not in result

    def test_without_filler_removal(self) -> None:
        text = "eee jadi begitu"
        result = cleanup_text(text, remove_filler=False)
        assert "eee" in result


@pytest.fixture()
def sample_result() -> TranscriptResult:
    return TranscriptResult(
        segments=[
            Segment(start=0.0, end=1.0, text="Halo"),
            Segment(start=1.2, end=2.0, text="apa kabar"),
            Segment(start=5.0, end=6.0, text="baik terima kasih"),
            Segment(start=6.5, end=7.0, text="sama-sama"),
        ],
        language="id",
        duration=7.0,
        engine_name="test",
        model_name="tiny",
    )


class TestSegmentsPerSentence:
    def test_returns_all(self, sample_result: TranscriptResult) -> None:
        segs = segments_per_sentence(sample_result)
        assert len(segs) == 4


class TestSegmentsMerged:
    def test_merge_close_segments(self, sample_result: TranscriptResult) -> None:
        merged = segments_merged(sample_result, gap_threshold=1.0)
        # 0-1 dan 1.2-2 harusnya digabung (gap 0.2 < 1.0)
        # 5-6 dan 6.5-7 harusnya digabung (gap 0.5 < 1.0)
        assert len(merged) < 4

    def test_no_merge_with_small_threshold(self, sample_result: TranscriptResult) -> None:
        merged = segments_merged(sample_result, gap_threshold=0.1)
        # Gap 0.2 > 0.1, jadi tidak ada yang digabung
        assert len(merged) == 4

    def test_empty_result(self) -> None:
        empty = TranscriptResult()
        assert segments_merged(empty) == []


class TestHeuristicDiarization:
    def test_assigns_speakers(self, sample_result: TranscriptResult) -> None:
        result = heuristic_diarization(sample_result, silence_gap=2.0)
        assert all(seg.speaker for seg in result.segments)

    def test_gap_creates_new_speaker(self, sample_result: TranscriptResult) -> None:
        # Gap antara seg 2 (end=2.0) dan seg 3 (start=5.0) = 3.0 > 2.0
        result = heuristic_diarization(sample_result, silence_gap=2.0)
        speakers = [seg.speaker for seg in result.segments]
        assert speakers[0] == speakers[1]  # dekat
        assert speakers[1] != speakers[2]  # gap besar

    def test_empty_result(self) -> None:
        empty = TranscriptResult()
        result = heuristic_diarization(empty)
        assert len(result.segments) == 0

    def test_metadata_has_diarization(self, sample_result: TranscriptResult) -> None:
        result = heuristic_diarization(sample_result)
        assert result.metadata.get("diarization") == "heuristic"
