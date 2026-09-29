"""The model: local Gemma 4 E2B through MLX. It only sees the messages we pass in.

Weights are resolved from the local Hugging Face cache with `local_files_only=True`
at a pinned revision, so a missing download fails fast with instructions instead of
silently reaching for the network.
"""
from __future__ import annotations

import sys
import time
import warnings
from dataclasses import asdict, dataclass
from typing import Callable

from . import config

# Raised by the audio branch of Gemma's multimodal processor at load time; harmless.
warnings.filterwarnings("ignore", message=".*mel filter.*")


class ModelUnavailable(RuntimeError):
    pass


@dataclass
class GenStats:
    prompt_tokens: int = 0
    generated_tokens: int = 0
    prompt_tps: float = 0.0
    generation_tps: float = 0.0
    peak_memory_gb: float = 0.0
    seconds: float = 0.0
    finish_reason: str | None = None

    def to_dict(self) -> dict:
        return {k: (round(v, 3) if isinstance(v, float) else v) for k, v in asdict(self).items()}

    def short(self) -> str:
        return (f"{self.prompt_tokens} prompt tok · {self.generated_tokens} new tok · "
                f"{self.generation_tps:.0f} tok/s · {self.seconds:.1f}s · "
                f"peak {self.peak_memory_gb:.2f} GB")


class LocalGemma:
    def __init__(self) -> None:
        self.model = self.processor = None
        self.load_seconds = 0.0
        self.path = None

    @staticmethod
    def identity() -> dict:
        import mlx.core as mx
        import mlx_vlm
        return {
            "model": config.GEMMA_ID,
            "revision": config.GEMMA_REVISION,
            "label": config.GEMMA_LABEL,
            "quantization": "4-bit affine, group size 64 (MLX)",
            "runtime": f"mlx {mx.__version__} + mlx-vlm {mlx_vlm.__version__}",
            "execution": "local",
        }

    def load(self) -> "LocalGemma":
        if self.model is not None:
            return self
        from huggingface_hub import snapshot_download
        try:
            self.path = snapshot_download(config.GEMMA_ID, revision=config.GEMMA_REVISION,
                                          local_files_only=True)
        except Exception as e:  # LocalEntryNotFoundError and friends
            raise ModelUnavailable(
                f"Local model {config.GEMMA_ID} (revision {config.GEMMA_REVISION[:7]}) is not "
                "in the Hugging Face cache.\n  While online, download it once with:\n"
                f"    .venv/bin/hf download {config.GEMMA_ID} --revision {config.GEMMA_REVISION}\n"
                f"  ({type(e).__name__})") from e
        from mlx_vlm import load
        t0 = time.perf_counter()
        try:
            self.model, self.processor = load(self.path)
        except Exception as e:
            raise ModelUnavailable(f"Found {config.GEMMA_ID} but could not load it: {e}") from e
        self.load_seconds = time.perf_counter() - t0
        import mlx.core as mx
        mx.set_cache_limit(1 << 30)  # keep at most 1 GB of freed GPU buffers around
        return self

    def generate(self, messages: list[dict], max_tokens: int, temperature: float,
                 on_text: Callable[[str], None] | None = None) -> tuple[str, GenStats]:
        """Render the chat template, generate, and optionally stream pieces to on_text."""
        import mlx.core as mx
        from mlx_vlm import apply_chat_template, stream_generate
        self.load()
        prompt = apply_chat_template(self.processor, self.model.config, messages, num_images=0)
        pieces, last = [], None
        t0 = time.perf_counter()
        try:
            for result in stream_generate(self.model, self.processor, prompt,
                                          max_tokens=max_tokens, temperature=temperature):
                if result.text:
                    pieces.append(result.text)
                    if on_text:
                        on_text(result.text)
                last = result
        except KeyboardInterrupt:
            print("\n[generation interrupted]", file=sys.stderr)
        stats = GenStats(seconds=time.perf_counter() - t0,
                         peak_memory_gb=mx.get_peak_memory() / 1e9)
        mx.clear_cache()
        if last is not None:
            stats.prompt_tokens = last.prompt_tokens
            stats.generated_tokens = last.generation_tokens
            stats.prompt_tps = last.prompt_tps
            stats.generation_tps = last.generation_tps
            stats.finish_reason = last.finish_reason
        return "".join(pieces).strip(), stats
