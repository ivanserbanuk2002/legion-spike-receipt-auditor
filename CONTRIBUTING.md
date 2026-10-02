# Contributing

Use Python 3.12. Install with `python -m pip install .`.
Run `python -m unittest discover -s tests -v` before opening a pull request.
Include a tiny synthetic JSONL case for a parser or audit change.
Keep runtime dependencies at zero and summaries independent of RPC providers.
Keep new chain identity rules explicit; never guess a chain from a hash.
Use the bug template for reproducible failures. Redact account data and credentials.
Small bug fixes and clearer examples are welcome; discuss protocol decoding separately.
