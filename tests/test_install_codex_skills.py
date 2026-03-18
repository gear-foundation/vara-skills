#!/usr/bin/env python3

from pathlib import Path
import os
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "install-codex-skills.sh"
EXPECTED_SKILLS = (
    "gear-architecture-planner",
    "gear-gstd-api-map",
    "gear-message-execution",
    "gtest-tdd-loop",
    "idea-to-spec",
    "sails-dev-env",
    "sails-frontend",
    "sails-architecture",
    "sails-feature-workflow",
    "sails-gtest",
    "sails-idl-client",
    "sails-local-smoke",
    "sails-new-app",
    "sails-rust-implementer",
    "ship-sails-app",
    "task-decomposer",
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
