# Usage — skillcheck

## Install

```shell
pip install -e .
```

## Commands

```shell
skillcheck --help
```

## Examples

### Lint the example skill

```shell
skillcheck check examples/log-triage/SKILL.md
```

### Scaffold a new skill

```shell
skillcheck init my-new-skill
```

### Gate a skills directory in CI

```shell
skillcheck check .skills/ --strict --json-out
```

## Target runtime and skill format

Skills are Markdown files used by **Claude Code and compatible agent runtimes**:

```
---
name: kebab-case-name
description: One sentence on when the agent should use this skill (read on every listing).
version: 0.1.0
---

# skill-name
## When to use
...
## Instructions
...
## Examples
...
```

Front matter is a flat `key: value` block between `---` lines; values may be
single- or double-quoted. Nested YAML is rejected as malformed by design.
Recognized keys: `name`, `description`, `version`, `license`, `allowed-tools`,
`metadata` (others produce an `unknown-key` warning).

## Validation gates

- **install**: `pip install -e . (fresh venv)`
- **unit tests**: `pytest -q`
- **CLI smoke**: `skillcheck --help; skillcheck check examples/log-triage/SKILL.md`
- **demo run**: `logs/2026-10-24/run_demos.py -> results/demo-output.txt`
- **secret scan**: `no tokens/keys/.env in tree`

## Exit codes

- `0` — success / no findings at or above threshold
- `1` — findings present, or validation cases failed
- `2` — usage error, unreadable input, or rejected target
