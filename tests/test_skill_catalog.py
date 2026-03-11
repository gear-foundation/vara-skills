#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-skill.py"
STARTER_SKILLS = {
    "ship-sails-app": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-new-app": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-feature-workflow": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-architecture": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-idl-client": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-gtest": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-local-smoke": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
}


def require(path: Path) -> None:
    assert path.exists(), f"missing expected path: {path.relative_to(ROOT)}"


def validate(skill_dir: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR), str(skill_dir)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def main() -> int:
    require(VALIDATOR)
    require(ROOT / "SKILL.md")

    for skill_name, expected_paths in STARTER_SKILLS.items():
        skill_dir = ROOT / "skills" / skill_name
        require(skill_dir)
        for relative in expected_paths:
            require(skill_dir / relative)
        validate(skill_dir)

    router = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    assert "ship-sails-app" in router
    assert "Codex" in router and "Claude" in router and "OpenClaw" in router

    new_app = (ROOT / "skills" / "sails-new-app" / "SKILL.md").read_text(encoding="utf-8")
    assert "Sails" in new_app

    feature = (
        ROOT / "skills" / "sails-feature-workflow" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "gtest" in feature.lower()

    architecture = (
        ROOT / "skills" / "sails-architecture" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "sails-program-architecture-patterns" in architecture

    idl_client = (
        ROOT / "skills" / "sails-idl-client" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "sails-idl-and-client-pipeline" in idl_client

    gtest_loop = (ROOT / "skills" / "sails-gtest" / "SKILL.md").read_text(encoding="utf-8")
    assert "gtest-core-workflows" in gtest_loop

    smoke = (ROOT / "skills" / "sails-local-smoke" / "SKILL.md").read_text(encoding="utf-8")
    assert "gear-run-local-node" in smoke or "sails-live-node-smoke" in smoke

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "gpt-5.4" in readme, "README.md should name the first evaluation target"
    assert "ship-sails-app" in readme and "sails-local-smoke" in readme
    assert "sails-new-app" in readme and "sails-feature-workflow" in readme
    assert "provisional" in readme.lower(), "README.md should keep the catalog provisional"
    assert "12" in readme and "knowledge" in readme and "codegen" in readme
    assert "2026-03-11-gpt54-suite-report.md" in readme
    assert "sails-default-path" in readme and "no-low-level-bypass" in readme
    assert "artifact" in readme.lower()

    print("starter skills ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
