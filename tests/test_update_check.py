#!/usr/bin/env python3

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "bin" / "vara-skills-update-check"


def run_check(
    skills_dir: str,
    state_dir: str,
    remote_url: str = "",
    force: bool = False,
    update_check: str | None = None,
) -> subprocess.CompletedProcess[str]:
    env = {
        "PATH": os.environ["PATH"],
        "HOME": os.environ.get("HOME", "/tmp"),
        "VARA_SKILLS_DIR": skills_dir,
        "VARA_SKILLS_STATE_DIR": state_dir,
    }
    if remote_url:
        env["VARA_SKILLS_REMOTE_URL"] = remote_url
    if update_check is not None:
        env["VARA_SKILLS_UPDATE_CHECK"] = update_check
    cmd = [str(SCRIPT)]
    if force:
        cmd.append("--force")
    return subprocess.run(cmd, capture_output=True, text=True, env=env, check=False)


def test_script_exists_and_is_executable() -> None:
    assert SCRIPT.exists(), "bin/vara-skills-update-check must exist"
    assert os.access(SCRIPT, os.X_OK), "bin/vara-skills-update-check must be executable"


def test_no_version_file_silent_exit() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        result = run_check(skills_dir, state_dir)
        assert result.returncode == 0
        assert result.stdout.strip() == ""


def test_disabled_via_env() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        Path(skills_dir, "VERSION").write_text("1.0.0\n")
        result = run_check(skills_dir, state_dir, update_check="false")
        assert result.returncode == 0
        assert result.stdout.strip() == ""


def test_just_upgraded_marker() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        Path(skills_dir, "VERSION").write_text("2.0.0\n")
        Path(state_dir, "just-upgraded-from").write_text("1.0.0\n")
        result = run_check(skills_dir, state_dir)
        assert result.returncode == 0
        assert "JUST_UPGRADED 1.0.0 2.0.0" in result.stdout
        # Marker should be consumed
        assert not Path(state_dir, "just-upgraded-from").exists()
        # Cache should be written
        cache = Path(state_dir, "last-update-check").read_text()
        assert "UP_TO_DATE 2.0.0" in cache


def test_just_upgraded_marker_empty() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        Path(skills_dir, "VERSION").write_text("2.0.0\n")
        Path(state_dir, "just-upgraded-from").write_text("\n")
        result = run_check(skills_dir, state_dir)
        assert result.returncode == 0
        # Empty marker → no JUST_UPGRADED output
        assert "JUST_UPGRADED" not in result.stdout
        assert not Path(state_dir, "just-upgraded-from").exists()


def test_cache_up_to_date() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        Path(skills_dir, "VERSION").write_text("1.0.0\n")
        Path(state_dir, "last-update-check").write_text("UP_TO_DATE 1.0.0\n")
        # Use a bogus URL that would fail if actually fetched
        result = run_check(skills_dir, state_dir, remote_url="http://localhost:1/nope")
        assert result.returncode == 0
        assert result.stdout.strip() == ""


def test_cache_upgrade_available() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        Path(skills_dir, "VERSION").write_text("1.0.0\n")
        Path(state_dir, "last-update-check").write_text("UPGRADE_AVAILABLE 1.0.0 2.0.0\n")
        result = run_check(skills_dir, state_dir, remote_url="http://localhost:1/nope")
        assert result.returncode == 0
        assert "UPGRADE_AVAILABLE 1.0.0 2.0.0" in result.stdout


def test_snooze_active() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        Path(skills_dir, "VERSION").write_text("1.0.0\n")
        Path(state_dir, "last-update-check").write_text("UPGRADE_AVAILABLE 1.0.0 2.0.0\n")
        now = int(time.time())
        Path(state_dir, "update-snoozed").write_text(f"2.0.0 1 {now}\n")
        result = run_check(skills_dir, state_dir, remote_url="http://localhost:1/nope")
        assert result.returncode == 0
        assert result.stdout.strip() == ""  # snoozed


def test_snooze_expired() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        Path(skills_dir, "VERSION").write_text("1.0.0\n")
        Path(state_dir, "last-update-check").write_text("UPGRADE_AVAILABLE 1.0.0 2.0.0\n")
        old = int(time.time()) - 90000  # >24h ago
        Path(state_dir, "update-snoozed").write_text(f"2.0.0 1 {old}\n")
        result = run_check(skills_dir, state_dir, remote_url="http://localhost:1/nope")
        assert result.returncode == 0
        assert "UPGRADE_AVAILABLE 1.0.0 2.0.0" in result.stdout


def test_snooze_new_version_ignores_snooze() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        Path(skills_dir, "VERSION").write_text("1.0.0\n")
        Path(state_dir, "last-update-check").write_text("UPGRADE_AVAILABLE 1.0.0 3.0.0\n")
        now = int(time.time())
        # Snoozed for 2.0.0 but 3.0.0 is available now
        Path(state_dir, "update-snoozed").write_text(f"2.0.0 1 {now}\n")
        result = run_check(skills_dir, state_dir, remote_url="http://localhost:1/nope")
        assert result.returncode == 0
        assert "UPGRADE_AVAILABLE 1.0.0 3.0.0" in result.stdout


def test_force_clears_cache_and_snooze() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        Path(skills_dir, "VERSION").write_text("1.0.0\n")
        Path(state_dir, "last-update-check").write_text("UP_TO_DATE 1.0.0\n")
        now = int(time.time())
        Path(state_dir, "update-snoozed").write_text(f"2.0.0 1 {now}\n")
        # Force should clear cache and snooze, then hit network (which fails → UP_TO_DATE)
        result = run_check(skills_dir, state_dir, remote_url="http://localhost:1/nope", force=True)
        assert result.returncode == 0
        assert not Path(state_dir, "update-snoozed").exists()
        # Cache gets rewritten as UP_TO_DATE since network fails
        cache = Path(state_dir, "last-update-check").read_text()
        assert "UP_TO_DATE" in cache


def test_network_failure_graceful() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        Path(skills_dir, "VERSION").write_text("1.0.0\n")
        # No cache, bogus URL → should fail gracefully
        result = run_check(skills_dir, state_dir, remote_url="http://localhost:1/nope")
        assert result.returncode == 0
        assert result.stdout.strip() == ""
        cache = Path(state_dir, "last-update-check").read_text()
        assert "UP_TO_DATE 1.0.0" in cache


def test_corrupt_snooze_file() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        Path(skills_dir, "VERSION").write_text("1.0.0\n")
        Path(state_dir, "last-update-check").write_text("UPGRADE_AVAILABLE 1.0.0 2.0.0\n")
        Path(state_dir, "update-snoozed").write_text("garbage\n")
        result = run_check(skills_dir, state_dir, remote_url="http://localhost:1/nope")
        assert result.returncode == 0
        assert "UPGRADE_AVAILABLE 1.0.0 2.0.0" in result.stdout


def test_corrupt_cache_file() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        Path(skills_dir, "VERSION").write_text("1.0.0\n")
        Path(state_dir, "last-update-check").write_text("BOGUS DATA\n")
        # Corrupt cache → TTL=0 → re-fetch (fails → UP_TO_DATE)
        result = run_check(skills_dir, state_dir, remote_url="http://localhost:1/nope")
        assert result.returncode == 0
        assert result.stdout.strip() == ""


def test_cache_version_mismatch_refetches() -> None:
    with tempfile.TemporaryDirectory() as skills_dir, tempfile.TemporaryDirectory() as state_dir:
        Path(skills_dir, "VERSION").write_text("2.0.0\n")
        # Cache says 1.0.0 is up to date, but local is now 2.0.0 → refetch
        Path(state_dir, "last-update-check").write_text("UP_TO_DATE 1.0.0\n")
        result = run_check(skills_dir, state_dir, remote_url="http://localhost:1/nope")
        assert result.returncode == 0
        # Network fails → UP_TO_DATE for 2.0.0
        cache = Path(state_dir, "last-update-check").read_text()
        assert "UP_TO_DATE 2.0.0" in cache


def main() -> int:
    tests = [
        test_script_exists_and_is_executable,
        test_no_version_file_silent_exit,
        test_disabled_via_env,
        test_just_upgraded_marker,
        test_just_upgraded_marker_empty,
        test_cache_up_to_date,
        test_cache_upgrade_available,
        test_snooze_active,
        test_snooze_expired,
        test_snooze_new_version_ignores_snooze,
        test_force_clears_cache_and_snooze,
        test_network_failure_graceful,
        test_corrupt_snooze_file,
        test_corrupt_cache_file,
        test_cache_version_mismatch_refetches,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"  ok: {test.__name__}")
        except Exception as err:
            print(f"FAIL: {test.__name__}: {err}", file=sys.stderr)
            failed += 1
    if failed:
        print(f"\n{failed}/{len(tests)} tests failed", file=sys.stderr)
        return 1
    print(f"\nupdate check ok ({len(tests)} tests)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
