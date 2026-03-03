"""Test engine interface dan availability check."""

from __future__ import annotations

from app.core.engines.base import Segment, TranscriptResult, get_available_engines


class TestSegment:
    def test_create_segment(self) -> None:
        seg = Segment(start=0.0, end=1.5, text="Hello")
        assert seg.start == 0.0
        assert seg.end == 1.5
        assert seg.text == "Hello"
        assert seg.speaker == ""

    def test_segment_with_speaker(self) -> None:
        seg = Segment(start=0.0, end=1.0, text="Test", speaker="Narasumber 1")
        assert seg.speaker == "Narasumber 1"


class TestTranscriptResult:
    def test_full_text(self) -> None:
        result = TranscriptResult(
            segments=[
                Segment(start=0, end=1, text="Halo"),
                Segment(start=1, end=2, text="dunia"),
            ]
        )
        assert result.full_text == "Halo dunia"

    def test_to_dict_roundtrip(self) -> None:
        original = TranscriptResult(
            segments=[Segment(start=0.0, end=1.0, text="Test", speaker="S1", confidence=0.9)],
            language="id",
            duration=1.0,
            engine_name="test",
            model_name="tiny",
            metadata={"key": "value"},
        )
        d = original.to_dict()
        restored = TranscriptResult.from_dict(d)
        assert len(restored.segments) == 1
        assert restored.segments[0].text == "Test"
        assert restored.language == "id"
        assert restored.metadata == {"key": "value"}

    def test_empty_result(self) -> None:
        result = TranscriptResult()
        assert result.full_text == ""
        assert result.to_dict()["segments"] == []


class TestGetAvailableEngines:
    def test_returns_list(self) -> None:
        engines = get_available_engines()
        assert isinstance(engines, list)
