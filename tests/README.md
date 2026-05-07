# Tests

Local tests for repository scripts.

Run from the repo root:

```text
python -m unittest discover tests/
```

The query tests use a small synthetic corpus under `tests/fixtures/query-corpus/`. They do not read user data and do not require package installs.
