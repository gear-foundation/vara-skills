#!/usr/bin/env python3

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]


def require(path: Path) -> None:
    assert path.exists(), f"missing expected path: {path.relative_to(ROOT)}"


def main() -> int:
    require(ROOT / "AGENTS.md")
    require(ROOT / "README.md")
    require(ROOT / "SKILL.md")
    require(ROOT / "Makefile")
    require(ROOT / "docs" / "plans" / "2026-03-11-core-skills-design.md")
    require(ROOT / "docs" / "plans" / "2026-03-11-core-skills.md")
    require(ROOT / "docs" / "plans" / "2026-03-11-redirect-validation.md")
    require(ROOT / "docs" / "plans" / "2026-03-11-vara-sails-builder-pack-design.md")
    require(ROOT / "docs" / "plans" / "2026-03-11-vara-sails-builder-pack.md")
    require(ROOT / "docs" / "plans" / "2026-03-11-self-contained-sails-gear-pack-design.md")
    require(ROOT / "docs" / "plans" / "2026-03-11-self-contained-sails-gear-pack.md")
    require(ROOT / "assets" / "spec-template.md")
    require(ROOT / "assets" / "architecture-template.md")
    require(ROOT / "assets" / "task-plan-template.md")
    require(ROOT / "assets" / "gtest-report-template.md")
    require(ROOT / ".claude-plugin" / "plugin.json")
    require(ROOT / ".claude-plugin" / "marketplace.json")
    require(ROOT / "openclaw-skill" / "SKILL.md")
    require(ROOT / "openclaw-skill" / "README.md")
    require(ROOT / "references" / "vara-domain-overview.md")
    require(ROOT / "references" / "sails-cheatsheet.md")
    require(ROOT / "references" / "gtest-cheatsheet.md")
    require(ROOT / "references" / "varaeth-extension-notes.md")
    require(ROOT / "references" / "gear-execution-model.md")
    require(ROOT / "references" / "gear-messaging-and-replies.md")
    require(ROOT / "references" / "gear-gas-reservations-and-waitlist.md")
    require(ROOT / "references" / "sails-program-and-service-architecture.md")
    require(ROOT / "references" / "sails-idl-client-pipeline.md")
    require(ROOT / "references" / "sails-gtest-and-local-validation.md")
    require(ROOT / "skills" / "gear-message-execution" / "SKILL.md")
    require(ROOT / "scripts" / "install-codex-skills.sh")
    require(ROOT / "scripts" / "validate-repo.sh")
    require(ROOT / "tests" / "test_install_codex_skills.py")
    require(ROOT / "tests")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Sails" in readme, "README.md should describe the Sails-builder focus"
    assert "provisional" in readme.lower(), "README.md should describe the public pack as provisional"
    print("repo layout ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
