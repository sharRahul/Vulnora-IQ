# VulnoraIQ assistant model

"Ask VulnoraIQ" and the AI finding explanations are powered by a small,
self-contained language model that runs **inside VulnoraIQ** — not through
Ollama or any external API. It is an optional helper agent: it summarises
findings, explains AI/LLM vulnerabilities, and suggests mitigations. It never
applies changes to a target; it provides guidance for a human reviewer.

The model is **optional**. If it is not installed, the assistant degrades
gracefully to deterministic templated guidance, and nothing else breaks.

## How it works

- Runs a small instruction-tuned **GGUF** model in-process via
  [`llama-cpp-python`](https://github.com/abetlen/llama-cpp-python) on **CPU or
  GPU**.
- Weights are **downloaded once on first use** and cached under
  `~/.cache/vulnoraiq/models/`, so the repository stays small and the assistant
  works offline afterwards.
- Answers are **grounded** in VulnoraIQ's bundled OWASP LLM Top-10 notes (a
  dependency-free keyword retriever) plus the selected finding's evidence.
- Tools (skills): **knowledge base** (bundled docs), **web_fetch** (a single,
  SSRF-guarded, size-capped HTTP GET so it can look something up when it does not
  know), and **read_docs** (read-only, allowlisted to the docs folder).

## Install

```bash
pip install -e .[assistant]      # adds llama-cpp-python
```

The default model (`Qwen/Qwen2.5-0.5B-Instruct-GGUF`, ~0.4 GB) downloads on first
use. No model file is committed to the repository.

### CPU vs GPU and wheel compatibility

`llama-cpp-python` is a compiled package, so the wheel must match your hardware:

- **GPU (recommended if you have one):** install a CUDA/Metal build, e.g.
  `pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124`
  then set `VULNORAIQ_ASSISTANT_GPU_LAYERS=-1` (the default `auto` already tries
  GPU first and falls back to CPU).
- **CPU:** `pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu`.
- **Older CPUs without AVX2** (symptom: `Windows Error 0xc000001d` /
  `Illegal instruction` on load): the generic prebuilt wheels assume AVX2. Build
  for your CPU instead: `CMAKE_ARGS="-DLLAMA_AVX2=OFF" pip install llama-cpp-python --no-binary :all:`
  (requires a C/C++ toolchain), or use the GPU wheel above.

When the runtime or weights are unavailable, VulnoraIQ logs the reason and uses
templated guidance — the WebUI keeps working.

## Configuration (environment)

| Variable | Purpose | Default |
| --- | --- | --- |
| `VULNORAIQ_ASSISTANT_MODEL_PATH` | Use a specific local `.gguf` (e.g. one you fine-tuned) | unset |
| `VULNORAIQ_ASSISTANT_MODEL_DIR` | Cache directory for downloaded weights | `~/.cache/vulnoraiq/models` |
| `VULNORAIQ_ASSISTANT_MODEL_REPO` / `_FILE` | Default HuggingFace repo / GGUF filename | Qwen2.5-0.5B-Instruct |
| `VULNORAIQ_ASSISTANT_MODEL_URL` | Direct download URL override | derived from repo/file |
| `VULNORAIQ_ASSISTANT_AUTODOWNLOAD` | Allow first-run download | `true` |
| `VULNORAIQ_ASSISTANT_GPU_LAYERS` | `auto`, `0` (CPU), or a layer count / `-1` (all GPU) | `auto` |
| `VULNORAIQ_ASSISTANT_CTX` | Context window | `4096` |
| `VULNORAIQ_ASSISTANT_READ_ROOT` | Allowlisted root for the `read_docs` tool | `docs/` |

## Training your own model (16 GB GPU)

You can fine-tune a small base model on cyber/AI-security material and drop the
result in as a GGUF — no change to VulnoraIQ code:

1. Pick a small base that fits LoRA/QLoRA training on 16 GB (e.g. Qwen2.5-0.5B/1.5B,
   Llama-3.2-1B/3B, Gemma-2-2B).
2. Fine-tune with QLoRA (e.g. `unsloth` or `transformers` + `peft` + `bitsandbytes`)
   on your AI-security dataset; 4-bit QLoRA keeps a 1–3B model within 16 GB.
3. Merge the adapter and convert to GGUF with `llama.cpp`'s `convert_hf_to_gguf.py`,
   then quantize (e.g. `q4_k_m`).
4. Point VulnoraIQ at it: `VULNORAIQ_ASSISTANT_MODEL_PATH=/path/to/your-model.gguf`.

The assistant keeps the same tools (knowledge base, `web_fetch`, `read_docs`), so
a model that does not know an answer can still fetch a reference URL the user
provides. Custom training is a follow-up to this foundation, not a prerequisite.
