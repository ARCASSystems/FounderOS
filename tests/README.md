# Tests

Local tests for repository scripts and hooks. No package install is required.

Run from the repo root:

```text
python -m unittest discover tests/
```

## Suites

- `tests/test_query.py` - exercises `scripts/query.py` against a synthetic corpus.
- `tests/test_post_tool_use_hook.py` - exercises the opt-in observation hook in bash and PowerShell temp repos.
- `tests/test_session_hooks.py` - parses SessionStart and Stop hooks without running a live Founder OS install.

Fixtures live under `tests/fixtures/` and contain public-safe sample data only. Tests must never read user data from the working Founder OS folder.

## How to add a new test

Create `tests/test_<thing>.py` and use stdlib `unittest`.
Use `tempfile.TemporaryDirectory` when a script writes files.
Keep fixtures small, public-safe, and under `tests/fixtures/<thing>/`.
Run everything with `python -m unittest discover tests/`.
