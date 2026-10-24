# Architecture — skillcheck

## Overview

`skillcheck` (ai-skill) is a single-package Python CLI: a `src/skillcheck/` package
with a pure logic module and a Click command layer, console-script entry point
`skillcheck = skillcheck.cli:main`, and no runtime services.

### `src/skillcheck/lint.py`

Front-matter parser (flat key: value pairs between --- delimiters, quoted or bare values) and pure lint rules returning Finding(severity, code, message). Format failures become a single 'format' error finding.

### `src/skillcheck/cli.py`

Click group: `check` (file or directory recursion, exit 0 pass / 1 fail / 2 usage, --strict promotes warnings, --json-out) and `init` (writes a valid NAME/SKILL.md skeleton).


## Design decisions

- **Logic/rendering separation.** Every decision (parse, match, lint, plan, score)
  lives in a pure module with no console output, so tests assert on data rather than
  on terminal formatting.
- **Exit codes as the CI contract.** 0 = clean/success, 1 = findings or failed
  validation, 2 = usage or read error. `--json-out` switches stdout to machine-readable
  JSON without changing exit codes.
- **Small dependency surface.** Only `click` (CLI) and `rich` (tables); everything
  else is the Python standard library. Fewer dependencies, fewer surprises.

## Data flow

```
input (token / file / URL + flags)
   -> Click command validates arguments
   -> pure module computes findings/verdicts/summary
   -> renderer prints table or JSON
   -> process exits 0 / 1 / 2
```

## Testing strategy

tests/test_s.py covers parsing edge cases, every rule (missing/invalid name, description limits, thin body, headings), the shipped example must pass, and CLI exit codes including scaffold round-trip.
