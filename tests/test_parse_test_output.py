#!/usr/bin/env python3

from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "parse_test_output.py"
FIXTURE = ROOT / "tests" / "fixtures" / "gtest-failure.log"
ERROR_FIXTURE = ROOT / "tests" / "fixtures" / "gtest-workspace-error.log"


def run_fixture(path: Path) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def main() -> int:
    assert SCRIPT.exists(), "missing expected path: scripts/parse_test_output.py"
    payload = run_fixture(FIXTURE)
    assert payload["status"] == "failed", payload
    assert payload["failed_tests"] == ["tests::fails_on_missing_reply"], payload
    assert "expected reply event" in payload["summary"], payload

    error_payload = run_fixture(ERROR_FIXTURE)
    assert error_payload["status"] == "error", error_payload
    assert error_payload["failed_tests"] == [], error_payload
    assert "failed to load manifest" in error_payload["summary"], error_payload
    print("gtest parser ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
