---
name: vara-skills-upgrade
description: Use when asked to upgrade or update vara-skills to the latest version, or to check what version is installed. Do not use for Vara app development tasks.
---

# Vara Skills Upgrade

## Role

Upgrade the vara-skills pack to the latest version. Invoked automatically by the preamble when `UPGRADE_AVAILABLE` is detected, or manually via `/vara-skills-upgrade`.

## Standalone Usage

Run the update check with force (busts cache and snooze):

```bash
VARA_SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../.." && pwd)"
_UPD=$("$VARA_SKILLS_DIR/bin/vara-skills-update-check" --force 2>/dev/null || true)
[ -n "$_UPD" ] && echo "$_UPD" || echo "vara-skills is up to date ($(cat "$VARA_SKILLS_DIR/VERSION" 2>/dev/null || echo unknown))"
```

Then follow the routing below based on output.

## Inline Upgrade Flow

This section is called by the preamble when the update check outputs `UPGRADE_AVAILABLE <old> <new>`.

### Step 1: Check auto-upgrade

```bash
_AUTO="${VARA_SKILLS_AUTO_UPGRADE:-}"
```

If `_AUTO` is `true` or `1`, skip to Step 3 (upgrade silently).

### Step 2: Ask the user

Use AskUserQuestion:

> vara-skills **v{new}** is available (you have v{old}).
>
> A) Upgrade now
> B) Not now (snooze)
> C) Never ask again

**If A (Upgrade now):** proceed to Step 3.

**If B (Not now):** Write snooze state and continue with the original skill.

```bash
# Read current snooze level (default to 0 if no file)
_SNOOZE_LEVEL=0
_SNOOZE_FILE="${VARA_SKILLS_STATE_DIR:-$HOME/.vara-skills}/update-snoozed"
if [ -f "$_SNOOZE_FILE" ]; then
  _SNOOZE_LEVEL=$(awk '{print $2}' "$_SNOOZE_FILE" 2>/dev/null || echo 0)
fi
_SNOOZE_LEVEL=$(( _SNOOZE_LEVEL + 1 ))
mkdir -p "${VARA_SKILLS_STATE_DIR:-$HOME/.vara-skills}"
echo "{new} $_SNOOZE_LEVEL $(date +%s)" > "$_SNOOZE_FILE"
```

Tell the user the snooze duration (level 1: 24h, level 2: 48h, level 3+: 7 days) and continue.

**If C (Never ask again):** Tell the user to add `export VARA_SKILLS_UPDATE_CHECK=false` to their shell profile (e.g. `~/.bashrc`, `~/.zshrc`, or `~/.config/fish/config.fish`). Continue with the original skill.

### Step 3: Perform upgrade

Detect the install type:

```bash
VARA_SKILLS_DIR="${VARA_SKILLS_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../.." && pwd)}"
[ -d "$VARA_SKILLS_DIR/.git" ] && echo "INSTALL_TYPE: git" || echo "INSTALL_TYPE: non-git"
```

**If git install:**

```bash
cd "$VARA_SKILLS_DIR"
git fetch origin
git reset --hard origin/main
```

**If non-git install:** Tell the user: "This is not a git install. Update vara-skills through the Claude Code plugin system: `/plugin marketplace update vara-skills`."

### Step 4: Post-upgrade

After a successful git upgrade:

```bash
STATE_DIR="${VARA_SKILLS_STATE_DIR:-$HOME/.vara-skills}"
mkdir -p "$STATE_DIR"
echo "{old}" > "$STATE_DIR/just-upgraded-from"
rm -f "$STATE_DIR/last-update-check" "$STATE_DIR/update-snoozed"
```

Show the user what changed:

```bash
git log --oneline "{old_tag}..HEAD" 2>/dev/null | head -20
```

If the tag lookup fails, just show: "Upgraded vara-skills from v{old} to v{new}."

Then continue with the original skill that triggered the preamble.
