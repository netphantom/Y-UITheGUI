"""Music generation engines.

The worker only knows the ``MusicEngine`` protocol (dependency inversion), so the real
YuE2 pipeline and the GPU-free mock are interchangeable via the ``YUI_ENGINE`` setting.
"""

import json
import math
import struct
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Protocol

from app.config import Settings


@dataclass(frozen=True)
class GenerationRequest:
    style: str
    lyrics: str
    cot: str
    seed: int
    cfg_scale: float | None = None
    abc: str | None = None

    def as_pipeline_kwargs(self) -> dict:
        """YuE2 rejects unknown keys, so optional fields are passed only when set."""
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass(frozen=True)
class GenerationResult:
    audio_file: Path
    score_abc: str | None
    truncated: bool


class MusicEngine(Protocol):
    name: str
    version: str | None

    def load(self) -> None:
        """Load weights into memory. Called once, off the event loop."""

    def generate(self, request: GenerationRequest, out_dir: Path) -> GenerationResult: ...


class YuE2Engine:
    name = "yue2"

    def __init__(self, settings: Settings):
        self._settings = settings
        self._pipe = None
        self.version: str | None = None

    def load(self) -> None:
        # Imported lazily: the package may have just been installed/updated by the updater.
        from importlib.metadata import version

        from yue2 import YuE2Pipeline

        self.version = version(self._settings.yue_package)
        self._pipe = YuE2Pipeline.from_pretrained(
            self._settings.model_id, device=self._settings.device
        )

    def generate(self, request: GenerationRequest, out_dir: Path) -> GenerationResult:
        song = self._pipe(**request.as_pipeline_kwargs())
        song.save_artifacts(str(out_dir))
        score_file = out_dir / "score.abc"
        return GenerationResult(
            audio_file=out_dir / "audio.flac",
            score_abc=score_file.read_text(encoding="utf-8") if score_file.exists() else None,
            truncated=bool(song.truncated),
        )


class MockEngine:
    """Writes a few seconds of a seed-dependent chord so the whole UI can be exercised."""

    name = "mock"
    version = "mock"
    SAMPLE_RATE = 22_050
    SECONDS = 4

    def __init__(self, _settings: Settings):
        pass

    def load(self) -> None:
        pass

    def generate(self, request: GenerationRequest, out_dir: Path) -> GenerationResult:
        out_dir.mkdir(parents=True, exist_ok=True)
        audio_file = out_dir / "audio.wav"
        root = 220 + request.seed % 220
        frequencies = (root, root * 5 / 4, root * 3 / 2)  # major triad
        with wave.open(str(audio_file), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(self.SAMPLE_RATE)
            frames = bytearray()
            for i in range(self.SAMPLE_RATE * self.SECONDS):
                t = i / self.SAMPLE_RATE
                sample = sum(math.sin(2 * math.pi * f * t) for f in frequencies) / 3
                fade = min(1.0, t * 4, (self.SECONDS - t) * 4)
                frames += struct.pack("<h", int(sample * fade * 12_000))
            wav.writeframes(bytes(frames))
        score = request.abc or "X:1\nT:Mock\nM:4/4\nL:1/4\nK:C\nC E G c | G E C2 |]\n"
        (out_dir / "request.json").write_text(json.dumps(asdict(request), indent=2))
        return GenerationResult(audio_file=audio_file, score_abc=score, truncated=False)


ENGINES: dict[str, type[MusicEngine]] = {"yue2": YuE2Engine, "mock": MockEngine}


def build_engine(settings: Settings) -> MusicEngine:
    return ENGINES[settings.engine](settings)
