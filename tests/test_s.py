"""Tests for front-matter parsing, lint rules, and CLI exit codes."""
import json
from pathlib import Path

from click.testing import CliRunner

from skillcheck.cli import main
from skillcheck.lint import SkillFormatError, lint, load, parse

VALID = """---
name: my-skill
description: Does a thing well.
---

# my-skill

## When to use

Use this whenever the thing needs doing in a repository under review.

## Instructions

1. First concrete instruction for the agent.
2. Second concrete instruction, testable and short.
"""

EXAMPLE = Path(__file__).resolve().parent.parent / "examples" / "log-triage" / "SKILL.md"


def test_parse_extracts_metadata_and_headings():
    skill = parse(VALID, Path("SKILL.md"))
    assert skill.metadata["name"] == "my-skill"
    assert skill.metadata["description"] == "Does a thing well."
    assert "When to use" in skill.body_headings
    assert "Instructions" in skill.body_headings
    assert skill.body.strip().startswith("# my-skill")


def test_parse_rejects_missing_front_matter():
    try:
        parse("# no front matter\n", Path("SKILL.md"))
        raise AssertionError("expected SkillFormatError")
    except SkillFormatError:
        pass


def test_parse_rejects_unclosed_front_matter():
    try:
        parse("---\nname: x\nno closing delimiter\n", Path("SKILL.md"))
        raise AssertionError("expected SkillFormatError")
    except SkillFormatError:
        pass


def test_valid_skill_has_no_errors():
    skill = parse(VALID, Path("SKILL.md"))
    findings = lint(skill)
    assert not [f for f in findings if f.severity == "error"]


def test_missing_name_and_description_are_errors():
    skill = parse("---\nname: x\n---\n\n# x\n\nbody text\n", Path("SKILL.md"))
    codes = {f.code for f in lint(skill)}
    assert "missing-description" in codes


def test_bad_name_format_is_error():
    skill = parse('---\nname: "My Skill!"\ndescription: ok\n---\n\n# x\n' + "body " * 30,
                  Path("SKILL.md"))
    assert "bad-name" in {f.code for f in lint(skill)}


def test_overlong_description_is_error():
    skill = parse(f"---\nname: a-skill\ndescription: {'x' * 1100}\n---\n\n"
                  f"# x\n\nbody text\n", Path("SKILL.md"))
    assert "description-too-long" in {f.code for f in lint(skill)}


def test_thin_body_and_no_headings_warn():
    skill = parse("---\nname: a-skill\ndescription: ok\n---\n\nshort body\n",
                  Path("SKILL.md"))
    codes = {f.code for f in lint(skill)}
    assert "thin-body" in codes
    assert "no-headings" in codes


def test_shipped_example_skill_passes():
    skill = load(EXAMPLE)
    errors = [f for f in lint(skill) if f.severity == "error"]
    assert errors == [], [f.message for f in errors]
    assert skill.metadata["name"] == "log-triage"


def test_cli_check_pass_and_fail():
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text(VALID, encoding="utf-8")
        ok = runner.invoke(main, ["check", "SKILL.md"])
        assert ok.exit_code == 0, ok.output

        Path("bad/SKILL.md").parent.mkdir()
        Path("bad/SKILL.md").write_text("---\nname: Bad Name\ntitle: x\n---\n\nbody\n",
                                        encoding="utf-8")
        bad = runner.invoke(main, ["check", "bad"])
        assert bad.exit_code == 1, bad.output
        assert "missing-description" in bad.output

        as_json = runner.invoke(main, ["check", "SKILL.md", "--json-out"])
        assert as_json.exit_code == 0, as_json.output
        data = json.loads(as_json.output)
        assert data[0]["name"] == "my-skill"


def test_cli_check_directory_finds_multiple():
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("one/SKILL.md").parent.mkdir()
        Path("one/SKILL.md").write_text(VALID, encoding="utf-8")
        Path("two/SKILL.md").parent.mkdir()
        Path("two/SKILL.md").write_text(VALID, encoding="utf-8")
        result = runner.invoke(main, ["check", "."])
        assert result.exit_code == 0, result.output
        assert "2 file(s) passed" in result.output


def test_cli_init_scaffold_is_valid():
    runner = CliRunner()
    with runner.isolated_filesystem():
        created = runner.invoke(main, ["init", "new-skill"])
        assert created.exit_code == 0, created.output
        checked = runner.invoke(main, ["check", "new-skill/SKILL.md"])
        assert checked.exit_code == 0, checked.output

        duplicate = runner.invoke(main, ["init", "new-skill"])
        assert duplicate.exit_code == 2, duplicate.output

        bad_name = runner.invoke(main, ["init", "Bad Name"])
        assert bad_name.exit_code == 2, bad_name.output


def test_cli_check_format_error_is_reported_not_raised():
    runner = CliRunner()
    with runner.isolated_filesystem():
        Path("SKILL.md").write_text("not a skill file", encoding="utf-8")
        result = runner.invoke(main, ["check", "SKILL.md"])
        assert result.exit_code == 1, result.output
        assert "format" in result.output