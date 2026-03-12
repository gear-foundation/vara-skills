#!/usr/bin/env python3

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
LOCAL_PATTERNS = (
    "/" + "Users/",
    "~/" + ".codex/skills",
    ".." + "/gear-skills",
    "Documents" + "/projects/",
)


def require(path: Path) -> None:
    assert path.exists(), f"missing expected path: {path.relative_to(ROOT)}"


def sanitized_files() -> list[Path]:
    return [
        ROOT / "README.md",
        ROOT / "SKILL.md",
        ROOT / "openclaw-skill" / "README.md",
        ROOT / "openclaw-skill" / "SKILL.md",
        ROOT / "references" / "gear-gstd-api-and-syscalls.md",
        ROOT / "skills" / "gear-gstd-api-map" / "SKILL.md",
        ROOT / "skills" / "gear-gstd-api-map" / "assets" / "pressure-scenarios.md",
        ROOT / "tests" / "fixtures" / "gtest-workspace-error.log",
    ]


def main() -> int:
    require(ROOT / "AGENTS.md")
    require(ROOT / "README.md")
    require(ROOT / "SKILL.md")
    require(ROOT / "Makefile")
    require(ROOT / ".gitignore")
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
    require(ROOT / "references" / "gear-gstd-api-and-syscalls.md")
    require(ROOT / "references" / "gear-messaging-and-replies.md")
    require(ROOT / "references" / "gear-gas-reservations-and-waitlist.md")
    require(ROOT / "references" / "sails-program-and-service-architecture.md")
    require(ROOT / "references" / "sails-idl-client-pipeline.md")
    require(ROOT / "references" / "sails-gtest-and-local-validation.md")
    require(ROOT / "skills" / "gear-gstd-api-map" / "SKILL.md")
    require(ROOT / "skills" / "gear-message-execution" / "SKILL.md")
    require(ROOT / "scripts" / "install-codex-skills.sh")
    require(ROOT / "scripts" / "validate-repo.sh")
    require(ROOT / "tests" / "test_install_codex_skills.py")
    require(ROOT / "tests")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Sails" in readme, "README.md should describe the Sails-builder focus"
    assert "provisional" in readme.lower(), "README.md should describe the public pack as provisional"

    for path in sanitized_files():
        text = path.read_text(encoding="utf-8")
        for pattern in LOCAL_PATTERNS:
            assert pattern not in text, (
                f"{path.relative_to(ROOT)} should not contain machine-specific path pattern: {pattern}"
            )
    print("repo layout ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
