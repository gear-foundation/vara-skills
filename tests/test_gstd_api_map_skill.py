#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-skill.py"


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


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def main() -> int:
    skill_dir = ROOT / "skills" / "gear-gstd-api-map"
    require(skill_dir)
    require(skill_dir / "SKILL.md")
    require(skill_dir / "assets" / "pressure-scenarios.md")
    require(skill_dir / "references")
    require(skill_dir / "scripts")
    require(ROOT / "references" / "gear-gstd-api-and-syscalls.md")
    validate(skill_dir)

    skill = read("skills/gear-gstd-api-map/SKILL.md")
    skill_lower = skill.lower()
    assert "../../references/gear-gstd-api-and-syscalls.md" in skill
    assert "gstd" in skill and "gcore" in skill and "gsys" in skill
    assert "design" in skill_lower and "debug" in skill_lower
    assert "msg" in skill and "exec" in skill and "prog" in skill
    assert "intent" in skill_lower and "syscall" in skill_lower

    reference = read("references/gear-gstd-api-and-syscalls.md")
    reference_lower = reference.lower()
    assert "gstd" in reference and "gcore" in reference and "gsys" in reference
    assert "msg" in reference and "exec" in reference and "prog" in reference
    assert "gr_send" in reference
    assert "gr_reply" in reference
    assert "gr_reserve_gas" in reference
    assert "gr_wait" in reference
    assert "design first" in reference_lower or "design-first" in reference_lower
    assert "debugging second" in reference_lower or "debugging" in reference_lower

    planner = read("skills/gear-architecture-planner/SKILL.md")
    sails_architecture = read("skills/sails-architecture/SKILL.md")
    feature_workflow = read("skills/sails-feature-workflow/SKILL.md")
    assert "gear-gstd-api-map" in planner
    assert "gear-gstd-api-map" in sails_architecture
    assert "gear-gstd-api-map" in feature_workflow

    router = read("SKILL.md")
    assert "gear-gstd-api-map" not in router

    print("gstd api map skill ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
