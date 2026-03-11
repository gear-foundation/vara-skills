#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-skill.py"
STARTER_SKILLS = {
    "idea-to-spec": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "gear-architecture-planner": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "task-decomposer": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "sails-rust-implementer": [
        "SKILL.md",
        "assets",
        "references",
        "scripts",
    ],
    "gtest-tdd-loop": [
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

    for skill_name, expected_paths in STARTER_SKILLS.items():
        skill_dir = ROOT / "skills" / skill_name
        require(skill_dir)
        for relative in expected_paths:
            require(skill_dir / relative)
        validate(skill_dir)

    idea = (ROOT / "skills" / "idea-to-spec" / "SKILL.md").read_text(encoding="utf-8")
    assert "../../assets/spec-template.md" in idea
    assert "../../references/vara-domain-overview.md" in idea
    assert "docs/plans/YYYY-MM-DD-<topic>-spec.md" in idea

    architecture = (
        ROOT / "skills" / "gear-architecture-planner" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "sails-program-architecture-patterns" in architecture
    assert "gear-messaging-model" in architecture
    assert "sails-idl-and-client-pipeline" in architecture
    assert "../../assets/architecture-template.md" in architecture

    task_decomposer = (
        ROOT / "skills" / "task-decomposer" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "../../assets/task-plan-template.md" in task_decomposer
    assert "spec" in task_decomposer and "architecture" in task_decomposer

    implementer = (
        ROOT / "skills" / "sails-rust-implementer" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "sails-idiomatic-dev" in implementer
    assert "gear-messaging-model" in implementer
    assert "gear-gas-and-value-accounting" in implementer

    gtest_loop = (
        ROOT / "skills" / "gtest-tdd-loop" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "gtest-core-workflows" in gtest_loop
    assert "gear-test-sails-program" in gtest_loop
    assert "../../assets/gtest-report-template.md" in gtest_loop
    assert "../../scripts/run_gtest.sh" in gtest_loop
    assert "../../scripts/parse_test_output.py" in gtest_loop

    print("starter skills ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
