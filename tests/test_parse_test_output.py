#!/usr/bin/env python3

from pathlib import Path
import json
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "parse_test_output.py"
FIXTURE = ROOT / "tests" / "fixtures" / "gtest-failure.log"


def main() -> int:
    assert SCRIPT.exists(), "missing expected path: scripts/parse_test_output.py"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(FIXTURE)],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "failed", payload
    assert payload["failed_tests"] == ["tests::fails_on_missing_reply"], payload
    assert "expected reply event" in payload["summary"], payload
    print("gtest parser ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
