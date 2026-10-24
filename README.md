# skillcheck

**Lint agent skill files (SKILL.md) before they ship — front matter, description limits, body structure.**

`skillcheck` validates the reusable skill files that coding agents (Claude Code and
compatible runtimes) load as instructions: correct front matter, a `name` that is
kebab-case, a `description` that fits in the listing budget, and a body structured
with headings an agent can follow. It ships as a CLI you can run locally or in CI.

## Problem

A skill with a missing `description`, a 4 KB one-line blob, or an empty body silently
degrades every agent session that loads it — the agent either never triggers the skill
or follows vague instructions. Nobody notices until output quality drops. Linting the
file at authoring time catches it in seconds.

## Features

- **`check PATH...`** — lint one file or recursively lint every `*.md` in a directory;
  exits 1 on any error (or any warning with `--strict`).
- **`init NAME`** — scaffold a valid `NAME/SKILL.md` skeleton that passes `check`.
- Rules: required `name`/`description`, kebab-case name, description ≤ 1024 chars,
  non-empty body, heading structure, unknown-key warnings.
- `--json-out` for CI; format errors are reported as findings, never stack traces.
- Ships a real example skill (`examples/log-triage/`) that passes its own linter.

## Example output

```
$ skillcheck check examples/log-triage/SKILL.md
examples/log-triage/SKILL.md — OK
1 file(s) passed

$ skillcheck check broken/SKILL.md
broken/SKILL.md — FINDINGS
+----------+----------------------+---------------------------------+
| severity | code                 | message                         |
|----------+----------------------+---------------------------------+
| error    | bad-name             | 'name' must be lowercase ...    |
| error    | missing-description  | front matter has no 'description' |
+----------+----------------------+---------------------------------+
```

Full transcripts: [`results/demo-output.txt`](results/demo-output.txt).

## Architecture summary

- `src/skillcheck/lint.py` — front-matter parser (deliberately dependency-free: flat
  `key: value` pairs, quoted or bare) plus pure lint rules returning `Finding` objects.
- `src/skillcheck/cli.py` — Click commands, directory recursion, exit-code policy.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Requirements

- Python ≥ 3.10
- `click`, `rich` (installed automatically)

## Installation

```shell
pip install -e .
```

## Quick start

```shell
skillcheck check examples/log-triage/SKILL.md
skillcheck init my-new-skill          # then edit and re-check
```

## Usage examples

```shell
# lint a whole skills directory in CI
skillcheck check .skills/ --strict --json-out
```

Target runtime: **Claude Code-style Markdown skills** — a `---` delimited front-matter
block with flat scalars, then Markdown body. The linter documents this grammar in
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md); skills in other formats may need
adaptation.

## Configuration

No config file. Rules are fixed and documented; flags are `--json-out` and `--strict`.

## Testing

```shell
pip install -e . pytest
pytest -q          # 13 tests: parser edge cases, each lint rule, CLI exit codes,
                   # the shipped example skill must pass
```

## Project structure

```
skillcheck/
├─ src/skillcheck/{__init__,cli,lint}.py
├─ tests/test_s.py
├─ examples/log-triage/SKILL.md      # example skill, lint-clean
├─ docs/{ARCHITECTURE,USAGE,PROJECT_SPEC}.md
├─ results/demo-output.txt
├─ RESULTS.md
└─ .github/workflows/ci.yml
```

## Limitations

- Front matter is parsed as flat `key: value` pairs — nested YAML structures are
  rejected as malformed rather than parsed. This is deliberate (dependency-free,
  auditable) and covers the skill format in practice.
- No `allowed-tools` semantic validation beyond "unknown key" warnings.
- Heuristic warnings (`thin-body`, `no-headings`) are advisory, not errors.

## Roadmap

- Optional nested-YAML mode behind a flag.
- Cross-file checks: duplicate names across a skill directory.
- `--fix` mode for trivial issues (missing version, trailing whitespace).

## Security notes

Skill files are instructions an agent will execute — review them like code. `skillcheck`
only *reads* files you point it at and never executes skill content. See
[SECURITY.md](SECURITY.md).

## License

MIT — see [LICENSE](LICENSE).