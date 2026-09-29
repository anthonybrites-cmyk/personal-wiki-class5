"""Personal wiki harness: CLI modes, retrieval, prompts, and local Gemma calls."""
import os

# Pin the Hugging Face client to the local cache before anything imports it, so no
# code path in this package can reach the network for weights or tokenizers.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
