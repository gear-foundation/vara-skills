#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import json
import re
import sys


FAILED_TEST_RE = re.compile(r"^test\s+(\S+)\s+\.\.\.\s+FAILED$", re.MULTILINE)
PANIC_SUMMARY_RE = re.compile(r"panicked at .*:\n(?P<message>.+)", re.MULTILINE)
ERROR_SUMMARY_RE = re.compile(r"^error:\s+(?P<message>.+)$", re.MULTILINE)


def parse_log(text: str) -> dict[str, object]:
    failed_tests = FAILED_TEST_RE.findall(text)
    summary_match = PANIC_SUMMARY_RE.search(text)
    error_match = ERROR_SUMMARY_RE.search(text)
    if error_match:
        return {
            "status": "error",
            "failed_tests": [],
            "summary": error_match.group("message").strip(),
        }
    if failed_tests:
        summary = summary_match.group("message").strip() if summary_match else "gtest failed"
        return {
            "status": "failed",
            "failed_tests": failed_tests,
            "summary": summary,
        }
    return {
        "status": "passed",
        "failed_tests": [],
        "summary": "gtest passed",
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: parse_test_output.py <logfile>", file=sys.stderr)
        return 1
    path = Path(sys.argv[1]).resolve()
    if not path.exists():
        print(f"missing logfile: {path}", file=sys.stderr)
        return 1
    payload = parse_log(path.read_text(encoding="utf-8"))
    print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
