# pAgeNt Decisions

Decisions that are settled, newest first.
Questions still open live under "Open design decisions" in `docs/architecture.md`.

## 2026-09-10 - Agent memory is stored in MongoDB

MongoDB is the storage backend for pAgeNt's memory, chosen because conversation turns and memory records are JSON-like documents that need no up-front schema.
This is the first persistence layer to be built; it settles *where* memory lives, not *what* gets sent to the model each turn (D5 in `docs/architecture.md` still owns that).

## 2026-09-01 - Default model is `qwen3.5:9b`

`qwen3.5:9b` is the default local model, selected on tool-calling reliability, consistency, and latency; `qwen3:14b` stays available as an opt-in escalation for tasks that need multi-step tool use.
This settles D3 in `docs/architecture.md` - see `benchmarks/tool-calling/analysis.ipynb` (issue #6) for the numbers and the known gaps, and set it via `OLLAMA_MODEL`.
