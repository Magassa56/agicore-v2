# Cowork AGIcore Runtime Import Status

Branch: feature/import-cowork-runtime

Imported from Claude Cowork local output into GitHub repo.

## Test result

Command:

py -m pytest -q

Result:

508 passed
15 failed
7 warnings

## Status

This branch is a WIP import checkpoint.
Do not merge into main until the failing tests are fixed.

## Main failure groups

- EMA strategy does not emit expected BUY signals
- Signal loop runtime does not emit expected events
- runtime_duration_ms returns 0.0 in some agents
- print() found in src/agicore/cli/main.py
- SQLite runtime tests fail with no such table: tasks
- Some replay / PnL expectations differ from current runtime behavior
