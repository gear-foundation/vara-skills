---
name: vara-skills
description: Use when a builder needs the top-level router for the provisional standard Gear/Vara Sails skill pack across Codex, Claude, or OpenClaw. Do not use for Vara.eth or ethexe work, non-Sails programs, or broad protocol research.
---

## Preamble (run first)

```bash
_VS_DIR=""
for _d in \
  "${VARA_SKILLS_DIR:-}" \
  "$HOME/.claude/skills/vara-skills" \
  ".claude/skills/vara-skills" \
  "$HOME"/.claude/plugins/cache/vara-skills/vara-skills/*; do
  if [ -n "$_d" ] && [ -f "$_d/bin/vara-skills-update-check" ]; then
    _VS_DIR="$_d"; break
  fi
done
if [ -n "$_VS_DIR" ]; then
  export VARA_SKILLS_DIR="$_VS_DIR"
  _UPD=$("$_VS_DIR/bin/vara-skills-update-check" 2>/dev/null || true)
  [ -n "$_UPD" ] && echo "$_UPD" || true
fi
```

If output shows `UPGRADE_AVAILABLE <old> <new>`: read `skills/vara-skills-upgrade/SKILL.md` and follow the "Inline upgrade flow" (auto-upgrade if configured, otherwise ask user with 3 options, write snooze if declined). If `JUST_UPGRADED <from> <to>`: tell user "Running vara-skills v{to} (upgraded from v{from})!" and continue.

# Vara Skills

This repository is the portable router for the provisional `vara-skills` pack.

Use `skills/ship-sails-app/SKILL.md` first when the task is about standard greenfield or unreleased Gear/Vara Sails application work.

The repo is intended to be self-contained: use local `references/` handbook files before depending on sibling repositories or machine-local skill directories.

## What This Router Covers

- `Codex`: install the local skill directories with `bash scripts/install-codex-skills.sh`
- `Claude`: use the same repo content through plugin metadata
- `OpenClaw`: use the same markdown surface through the wrapper skill

## Route By Builder Intent

- Prepare or repair the local Rust or Gear toolchain first: `skills/sails-dev-env/SKILL.md`
- Start a new Sails workspace: `skills/sails-new-app/SKILL.md`
- Add or change a feature in an existing Sails repo: `skills/sails-feature-workflow/SKILL.md`
- Rework service or program boundaries: `skills/sails-architecture/SKILL.md`
- Debug message flow, replies, delays, or reservations: `skills/gear-message-execution/SKILL.md`
- Fix `build.rs`, IDL, or generated clients: `skills/sails-idl-client/SKILL.md`
- Write or debug `gtest`: `skills/sails-gtest/SKILL.md`
- Run typed local-node smoke after green `gtest`: `skills/sails-local-smoke/SKILL.md`
- Add a fungible token layer with awesome-sails: `skills/awesome-sails-vft/SKILL.md`
- Interact with Vara Network on-chain (deploy, call, transfer, monitor): `skills/vara-wallet/SKILL.md`
- Build or extend a React frontend for a Sails app: `skills/sails-frontend/SKILL.md`
- Evolve a released Sails contract, prepare a new deployed version, plan cutover, or design V1->V2 migration: `skills/sails-program-evolution/SKILL.md`
- Look up network endpoints, testnet/mainnet RPC, account format, or program lifecycle: `references/vara-network-endpoints.md`
- Look up bridge contract addresses or bridged token program IDs: `references/vara-eth-bridge-contracts.md`
- Understand Vara-Ethereum bridge flows, fee model, or integration patterns: `references/vara-eth-bridge-flows.md`

## Guardrails

- This catalog is still provisional and is expected to change as `vara-skills-evals` measures uplift.
- Stay on the standard Gear/Vara Sails path for v1.
- If the task is Vara.eth or ethexe-specific, stop and use a dedicated ethexe skill instead of this pack.
- Bridge reference knowledge (addresses, flows, fees) is in scope as a lookup resource. Full Vara.eth workflow routing is still deferred to dedicated ethexe skills.
