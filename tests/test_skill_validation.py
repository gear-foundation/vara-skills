#!/usr/bin/env python3

from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate-skill.py"


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(path)],
        text=True,
        capture_output=True,
        check=False,
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    assert VALIDATOR.exists(), "missing expected path: scripts/validate-skill.py"

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        missing = tmp / "missing-skill"
        missing.mkdir()
        result = run_validator(missing)
        assert result.returncode != 0, "validator should reject missing SKILL.md"

        malformed = tmp / "malformed-skill"
        malformed.mkdir()
        write(malformed / "SKILL.md", "# no frontmatter\n")
        result = run_validator(malformed)
        assert result.returncode != 0, "validator should reject malformed frontmatter"

        valid = tmp / "valid-skill"
        (valid / "scripts").mkdir(parents=True)
        (valid / "references").mkdir()
        (valid / "assets").mkdir()
        write(
            valid / "SKILL.md",
            "---\nname: valid-skill\ndescription: Use when validating starter skills for Gear and Vara. Do not use this skill for production work.\n---\n\n# Valid Skill\n",
        )
        result = run_validator(valid)
        assert result.returncode == 0, result.stderr

    skill_dirs = sorted(path for path in (ROOT / "skills").iterdir() if (path / "SKILL.md").exists())
    assert skill_dirs, "expected at least one installable skill"
    for skill_dir in skill_dirs:
        result = run_validator(skill_dir)
        assert result.returncode == 0, f"{skill_dir.relative_to(ROOT)}: {result.stderr}"

    print("skill validation ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
