# PROJECT SPEC — skillcheck

| Field | Value |
|---|---|
| Name | `skillcheck` |
| Category | ai-skill |
| Target user | Authors of agent skill files (Claude Code and compatible runtimes) |
| Problem | Broken skill front matter silently degrades agent sessions: the skill never triggers or gives vague instructions. |
| Solution | A dependency-free linter for SKILL.md files with a scaffold command and a shipped lint-clean example skill. |
| Core workflow | init or write skill -> check locally -> gate in CI with --strict |
| Stack | Python >=3.10, click, rich |
| Test strategy | tests/test_s.py covers parsing edge cases, every rule (missing/invalid name, description limits, thin body, headings), the shipped example must pass, and CLI exit codes including scaffold round-trip. |
| Demo strategy | `logs/2026-10-24/run_demos.py` runs the real workflow and captures `results/demo-output.txt` with asserted exit codes |
| Safety | Read-only against files you name; skill content is never executed. No network access. |
| Definition of done | install + pytest + CLI smoke + demo transcript + secret scan all pass; docs (README, ARCHITECTURE, USAGE, CHANGELOG, CONTRIBUTING) present; pushed with green CI |

## Must-have features

- skillcheck check examples/log-triage/SKILL.md
- skillcheck init my-new-skill
- Exit-code contract (0/1/2) usable from CI
- `--json-out` machine-readable output

## Nice-to-have (deferred)

- See README Roadmap.
