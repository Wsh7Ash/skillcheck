#!/usr/bin/env python3
"""skillcheck — lint agent skill files (SKILL.md) before you ship them.

Workflows:
  skillcheck check PATH...   lint one or more skill files (or a directory)
  skillcheck init NAME       scaffold a new valid skill file

Target runtime: Claude Code-style Markdown skills with flat front matter
(see docs/ARCHITECTURE.md). Everything runs locally on your own files.
"""
from __future__ import annotations

import json
import pathlib
import sys

import click
from rich.console import Console
from rich.table import Table

from skillcheck.lint import load_and_lint

console = Console()

SEVERITY = {"error": 2, "warning": 1}


def _collect(paths: tuple[pathlib.Path, ...]) -> list[pathlib.Path]:
    files: list[pathlib.Path] = []
    for p in paths:
        if p.is_dir():
            files.extend(sorted(p.rglob("*.md")))
        else:
            files.append(p)
    return files


@click.group()
def main() -> None:
    """Lint skill files: front matter, description limits, body structure."""


@main.command("check")
@click.argument("paths", nargs=-1, required=True,
                type=click.Path(exists=True, path_type=pathlib.Path))
@click.option("--json-out", is_flag=True)
@click.option("--strict", is_flag=True, help="Treat warnings as failures.")
def check_cmd(paths: tuple[pathlib.Path, ...], json_out: bool, strict: bool) -> None:
    """Lint each skill file under PATHS; exit 1 when any error (or warning with --strict)."""
    files = _collect(paths)
    if not files:
        console.print("[red]error:[/red] no Markdown files found")
        sys.exit(2)

    reports = []
    for path in files:
        skill, findings = load_and_lint(path)
        reports.append({
            "file": str(path),
            "name": skill.metadata.get("name") if skill else None,
            "findings": [{"severity": f.severity, "code": f.code, "message": f.message}
                         for f in findings],
        })

    if json_out:
        click.echo(json.dumps(reports, indent=2))
    else:
        for report in reports:
            status = "OK" if not report["findings"] else "FINDINGS"
            console.print(f"[bold]{report['file']}[/bold] — {status}")
            table = Table(show_header=True, header_style="bold")
            table.add_column("severity")
            table.add_column("code")
            table.add_column("message")
            colors = {"error": "red", "warning": "yellow"}
            for f in report["findings"]:
                table.add_row(f"[{colors[f['severity']]}]{f['severity']}[/]",
                              f["code"], f["message"])
            if report["findings"]:
                console.print(table)

    def failed(report: dict) -> bool:
        severities = {f["severity"] for f in report["findings"]}
        if "error" in severities:
            return True
        return strict and "warning" in severities

    failures = sum(1 for r in reports if failed(r))
    if failures:
        if not json_out:
            console.print(f"[red]{failures}/{len(reports)} file(s) failed lint[/red]")
        sys.exit(1)
    if not json_out:
        console.print(f"[green]{len(reports)} file(s) passed[/green]")


@main.command("init")
@click.argument("name")
@click.option("--output", "output_dir", type=click.Path(file_okay=False,
               path_type=pathlib.Path), default=".", show_default=True)
def init_cmd(name: str, output_dir: pathlib.Path) -> None:
    """Scaffold NAME/SKILL.md with a valid front-matter skeleton."""
    if not name.replace("-", "").isalnum() or name != name.lower():
        console.print(f"[red]error:[/red] name must be lowercase kebab-case, got {name!r}")
        sys.exit(2)
    target_dir = output_dir / name
    target = target_dir / "SKILL.md"
    if target.exists():
        console.print(f"[red]error:[/red] {target} already exists")
        sys.exit(2)
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(
        f"---\n"
        f"name: {name}\n"
        f"description: One sentence explaining when an agent should use this skill.\n"
        f"version: 0.1.0\n"
        f"---\n\n"
        f"# {name}\n\n"
        f"## When to use\n\n"
        f"Describe the situations that should trigger this skill.\n\n"
        f"## Instructions\n\n"
        f"1. Step-by-step guidance the agent must follow.\n"
        f"2. Keep each instruction concrete and testable.\n\n"
        f"## Examples\n\n"
        f"Show one good input/output pair for the task.\n",
        encoding="utf-8",
    )
    console.print(f"[green]created[/green] {target}")


if __name__ == "__main__":
    main()