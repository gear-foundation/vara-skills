#!/usr/bin/env python3

from pathlib import Path
import os
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install-codex-skills.sh"
PACK_NAME = "vara-skills"
EXPECTED_SKILLS = tuple(
    sorted(path.name for path in (ROOT / "skills").iterdir() if path.is_dir())
)


def main() -> int:
    assert SCRIPT.exists(), "missing expected path: scripts/install-codex-skills.sh"
    with tempfile.TemporaryDirectory() as tmpdir:
        env = os.environ.copy()
        env["CODEX_HOME"] = tmpdir
        result = subprocess.run(
            ["bash", str(SCRIPT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            env=env,
        )
        assert result.returncode == 0, result.stderr
        target = Path(tmpdir) / "skills"
        pack_link = target / PACK_NAME
        assert pack_link.is_symlink(), f"missing symlink for {PACK_NAME}"
        assert pack_link.resolve() == ROOT.resolve(), (
            f"wrong target for {PACK_NAME}: {pack_link.resolve()}"
        )
        assert (pack_link / "SKILL.md").exists(), "root pack should expose SKILL.md"
        assert (pack_link / "assets").is_dir(), "root pack should expose assets/"
        assert (pack_link / "references").is_dir(), "root pack should expose references/"
        for skill in EXPECTED_SKILLS:
            link = target / skill
            assert link.is_symlink(), f"missing symlink for {skill}"
            assert link.resolve() == (ROOT / "skills" / skill).resolve(), (
                f"wrong target for {skill}: {link.resolve()}"
            )
    print("install script ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
