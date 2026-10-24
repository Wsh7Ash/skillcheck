"""Front-matter parsing and lint rules for agent SKILL.md files.

Target runtime: Markdown skill files as used by Claude Code and
compatible agents — a `---` delimited YAML-ish front-matter block
(flat `key: value` pairs) followed by a Markdown body.

Only flat scalar pairs are parsed deliberately: skill front matter in
the wild is flat, and avoiding a YAML dependency keeps the linter
auditable. Values may be single- or double-quoted.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME = 64
MAX_DESCRIPTION = 1024  # matches common skill/agent description limits
KNOWN_KEYS = {"name", "description", "version", "license", "allowed-tools", "metadata"}


class SkillFormatError(ValueError):
    """Raised when a file is not structurally a skill file."""


@dataclass
class SkillFile:
    path: Path
    metadata: dict[str, str]
    body: str
    body_headings: list[str]


def load(path: Path) -> SkillFile:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise SkillFormatError(f"cannot read {path}: {exc}") from exc
    return parse(text, path)


def parse(text: str, path: Path) -> SkillFile:
    if not text.startswith("---"):
        raise SkillFormatError("file must start with '---' front-matter delimiter")
    lines = text.splitlines()
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise SkillFormatError("front matter is not closed by a '---' line")

    metadata: dict[str, str] = {}
    for lineno, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise SkillFormatError(f"line {lineno}: expected 'key: value'")
        key, _, value = line.partition(":")
        key = key.strip()
        if not key or " " in key:
            raise SkillFormatError(f"line {lineno}: invalid key {key!r}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        metadata[key] = value

    body = "\n".join(lines[end + 1:])
    headings = re.findall(r"^#{1,6}\s+(.+)$", body, flags=re.MULTILINE)
    return SkillFile(path=path, metadata=metadata, body=body,
                     body_headings=[h.strip() for h in headings])


@dataclass
class Finding:
    severity: str  # "error" | "warning"
    code: str
    message: str


def lint(skill: SkillFile) -> list[Finding]:
    """Apply lint rules; return findings (empty list == pass)."""
    findings: list[Finding] = []

    def error(code: str, message: str) -> None:
        findings.append(Finding("error", code, message))

    def warning(code: str, message: str) -> None:
        findings.append(Finding("warning", code, message))

    meta = skill.metadata

    if "name" not in meta:
        error("missing-name", "front matter has no 'name'")
    else:
        name = meta["name"]
        if not NAME_RE.match(name):
            error("bad-name",
                  f"'name' must be lowercase kebab-case, got {name!r}")
        elif len(name) > MAX_NAME:
            error("name-too-long", f"'name' exceeds {MAX_NAME} characters")

    if "description" not in meta:
        error("missing-description", "front matter has no 'description'")
    else:
        desc = meta["description"]
        if not desc.strip():
            error("empty-description", "'description' is empty")
        elif len(desc) > MAX_DESCRIPTION:
            error("description-too-long",
                  f"'description' is {len(desc)} chars (max {MAX_DESCRIPTION}): "
                  f"descriptions are read on every skill listing")

    for key in meta:
        if key not in KNOWN_KEYS:
            warning("unknown-key", f"unknown front-matter key {key!r}")

    if not skill.body.strip():
        error("empty-body", "skill has no body after front matter")
    elif len(skill.body.strip()) < 80:
        warning("thin-body",
                f"body is only {len(skill.body.strip())} characters — "
                f"instructions are unlikely to be useful")

    if skill.body.strip() and not skill.body_headings:
        warning("no-headings", "body has no Markdown headings to structure instructions")

    return findings


def load_and_lint(path: Path) -> tuple[SkillFile | None, list[Finding]]:
    """Convenience: parse then lint; format failures become a single error finding."""
    try:
        skill = load(path)
    except SkillFormatError as exc:
        return None, [Finding("error", "format", str(exc))]
    return skill, lint(skill)