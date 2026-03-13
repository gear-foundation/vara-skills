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
    for field in ("name", "version", "description"):
        assert plugin.get(field), f"plugin.json missing field: {field}"
    assert plugin["name"] == "vara-skills", "plugin.json should publish the pack as vara-skills"
    assert re.match(r"^\d+\.\d+\.\d+$", str(plugin["version"])), "plugin version must use semver"
    for field in ("homepage", "repository"):
        value = plugin.get(field)
        if value is not None:
            assert_nonempty_string(value, f"plugin.json field should be a non-empty string when present: {field}")
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
    if owner.get("url") is not None:
        assert_nonempty_string(owner.get("url"), "marketplace owner URL should be a non-empty string when present")
    metadata = marketplace.get("metadata")
    assert isinstance(metadata, dict), "marketplace.json missing metadata block"
    assert metadata.get("version") == plugin["version"], "marketplace metadata version should match plugin version"
    assert metadata.get("description"), "marketplace metadata should describe the pack"
    plugins = marketplace.get("plugins")
    assert isinstance(plugins, list) and plugins, "marketplace.json must list at least one plugin"
    first_plugin = plugins[0]
    assert first_plugin.get("name") == "vara-skills", "marketplace should expose vara-skills"
    assert first_plugin.get("source") == ".", "marketplace should point local testing at the repo root"
    assert first_plugin.get("version") == plugin["version"], "marketplace plugin version should match plugin.json"
    assert first_plugin.get("description") == plugin["description"], "marketplace plugin description should match plugin.json"
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
