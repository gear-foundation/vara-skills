#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import json
import re
import sys


ROOT = Path(__file__).resolve().parents[1]


def require(path: Path) -> None:
    assert path.exists(), f"missing expected path: {path.relative_to(ROOT)}"


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_nonempty_string(value: object, label: str) -> None:
    assert isinstance(value, str) and value.strip(), label


def main() -> int:
    plugin_path = ROOT / ".claude-plugin" / "plugin.json"
    marketplace_path = ROOT / ".claude-plugin" / "marketplace.json"
    openclaw_skill_path = ROOT / "openclaw-skill" / "SKILL.md"
    openclaw_readme_path = ROOT / "openclaw-skill" / "README.md"

    require(plugin_path)
    require(marketplace_path)
    require(openclaw_skill_path)
    require(openclaw_readme_path)

    plugin = load_json(plugin_path)
    for field in ("name", "description"):
        assert plugin.get(field), f"plugin.json missing field: {field}"
    assert plugin["name"] == "vara-skills", "plugin.json should publish the pack as vara-skills"
    # Version is managed solely in marketplace.json for relative-path plugins
    # (per Claude Code docs: plugin.json version silently overrides marketplace version)
    assert "version" not in plugin, "plugin.json should not set version for relative-path plugins (set in marketplace.json only)"
    for field in ("homepage", "repository"):
        value = plugin.get(field)
        if value is not None:
            assert_nonempty_string(value, f"plugin.json field should be a non-empty string when present: {field}")
    assert_nonempty_string(plugin.get("license"), "plugin.json should include an SPDX license identifier")
    plugin_author = plugin.get("author")
    assert isinstance(plugin_author, dict), "plugin author should use object form"
    assert_nonempty_string(plugin_author.get("name"), "plugin author should include a non-empty name")
    keywords = plugin.get("keywords", [])
    assert isinstance(keywords, list), "plugin keywords must be an array"
    assert "vara" in keywords and "sails" in keywords, "plugin keywords should expose Vara and Sails"

    marketplace = load_json(marketplace_path)
    assert marketplace.get("name") == "vara-skills", "marketplace should publish a public vara-skills name"
    owner = marketplace.get("owner")
    assert isinstance(owner, dict), "marketplace owner should use the object form expected by Claude Code"
    assert_nonempty_string(owner.get("name"), "marketplace owner should include a non-empty name")
    # owner only supports name and email per Claude Code docs
    for key in owner:
        assert key in ("name", "email"), f"marketplace owner has unsupported field: {key}"
    metadata = marketplace.get("metadata")
    assert isinstance(metadata, dict), "marketplace.json missing metadata block"
    assert re.match(r"^\d+\.\d+\.\d+$", str(metadata.get("version", ""))), "marketplace metadata version must use semver"
    assert metadata.get("description"), "marketplace metadata should describe the pack"
    plugins = marketplace.get("plugins")
    assert isinstance(plugins, list) and plugins, "marketplace.json must list at least one plugin"
    first_plugin = plugins[0]
    assert first_plugin.get("name") == "vara-skills", "marketplace should expose vara-skills"
    assert first_plugin.get("source") == "./", "marketplace should point local testing at the repo root"
    assert re.match(r"^\d+\.\d+\.\d+$", str(first_plugin.get("version", ""))), "marketplace plugin version must use semver"
    assert first_plugin.get("version") == metadata.get("version"), "marketplace plugin version should match metadata version"
    assert first_plugin.get("description") == plugin["description"], "marketplace plugin description should match plugin.json"
    assert_nonempty_string(first_plugin.get("license"), "marketplace plugin entry should include an SPDX license identifier")
    author = first_plugin.get("author")
    assert isinstance(author, dict), "marketplace plugin author should use object form"
    assert_nonempty_string(author.get("name"), "marketplace plugin author should include a non-empty name")

    openclaw_skill = openclaw_skill_path.read_text(encoding="utf-8")
    assert "ship-sails-app" in openclaw_skill, "OpenClaw wrapper should route through ship-sails-app"
    assert "standard Gear/Vara Sails" in openclaw_skill, "OpenClaw wrapper should constrain scope"

    openclaw_readme = openclaw_readme_path.read_text(encoding="utf-8")
    assert "OpenClaw" in openclaw_readme
    assert "SKILL.md" in openclaw_readme

    print("packaging metadata ok")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(err, file=sys.stderr)
        raise SystemExit(1)
