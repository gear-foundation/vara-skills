#!/usr/bin/env python3

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


def require(path: Path) -> None:
    assert path.exists(), f"missing expected path: {path.relative_to(ROOT)}"


def main() -> int:
    require(ROOT / "AGENTS.md")
    require(ROOT / "README.md")
    require(ROOT / "Makefile")
    require(ROOT / "docs" / "plans" / "2026-03-11-core-skills-design.md")
    require(ROOT / "docs" / "plans" / "2026-03-11-core-skills.md")
    require(ROOT / "assets" / "spec-template.md")
    require(ROOT / "assets" / "architecture-template.md")
    require(ROOT / "assets" / "task-plan-template.md")
    require(ROOT / "assets" / "gtest-report-template.md")
    require(ROOT / "references" / "vara-domain-overview.md")
    require(ROOT / "references" / "sails-cheatsheet.md")
    require(ROOT / "references" / "gtest-cheatsheet.md")
    require(ROOT / "references" / "varaeth-extension-notes.md")
    require(ROOT / "scripts" / "install-codex-skills.sh")
    require(ROOT / "scripts" / "validate-repo.sh")
    require(ROOT / "tests")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Vara" in readme, "README.md should describe the Gear/Vara focus"
    print("repo layout ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
