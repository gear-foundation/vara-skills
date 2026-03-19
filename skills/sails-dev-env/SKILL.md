---
name: sails-dev-env
description: Use when a builder needs to prepare or repair a local macOS, Linux, or Windows machine for standard Gear/Vara Sails Rust development before building, testing, or running a local node. Do not use for live-network deployment, app-specific feature work, or Vara.eth/ethexe-only setup.
---

# Sails Dev Env

## Goal

Get the machine to a verified baseline for standard Sails Rust work: `rustup`, Rust toolchains, Wasm targets, `cargo-sails`, and the latest official `gear` binary.

## Sequence

1. Detect whether the builder is on `macOS`, `Linux`, or `Windows`.
2. If `rustup` is missing, install it with the official bootstrap for that platform.
3. Install or update the `stable` and `nightly` toolchains, then add `wasm32v1-none` and `wasm32-unknown-unknown`.
4. Install the Sails Rust CLI with `cargo install sails-cli`, which provides `cargo-sails` and the standard greenfield bootstrap command `cargo sails program <project-name>`.
5. Install the latest official `gear` release binary with the local helper in `./scripts/install-gear.sh` on `macOS` or `Linux`, or `./scripts/install-gear.ps1` on `Windows`.
6. Verify the toolchain with `rustup show`, `cargo sails --version`, and `gear --version`.
7. Route back into `../sails-new-app/SKILL.md`, `../ship-sails-app/SKILL.md`, `../sails-gtest/SKILL.md`, or `../sails-local-smoke/SKILL.md` depending on the builder's next task.

## Commands

### macOS or Linux

```bash
command -v rustup >/dev/null 2>&1 || curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
. "${HOME}/.cargo/env"

rustup toolchain install stable
rustup toolchain install nightly
rustup default stable
rustup target add wasm32v1-none --toolchain stable
rustup target add wasm32v1-none --toolchain nightly
rustup target add wasm32-unknown-unknown --toolchain stable
rustup target add wasm32-unknown-unknown --toolchain nightly

cargo install sails-cli
bash ./scripts/install-gear.sh --to "${HOME}/.local/bin"

rustup show
cargo sails --version
cargo sails --help
gear --version
```

### Windows

```powershell
if (-not (Get-Command rustup -ErrorAction SilentlyContinue)) {
  winget install Rustlang.Rustup
}

rustup toolchain install stable
rustup toolchain install nightly
rustup default stable
rustup target add wasm32v1-none --toolchain stable
rustup target add wasm32v1-none --toolchain nightly
rustup target add wasm32-unknown-unknown --toolchain stable
rustup target add wasm32-unknown-unknown --toolchain nightly

cargo install sails-cli
powershell -ExecutionPolicy Bypass -File .\scripts\install-gear.ps1 -Destination "$env:USERPROFILE\AppData\Local\Programs\gear\bin"

rustup show
cargo sails --version
cargo sails --help
gear --version
```

## Guardrails

- Keep this skill self-contained. Do not depend on a sibling `gear` checkout or machine-local scripts outside this skill directory.
- Prefer the latest official `gear` release binary over building the node from source unless the user asks for a specific tag or source build.
- Treat base package-manager bootstrap as outside scope. If host tools such as `curl`, `tar`, `xz`, or `winget` are missing, install them with the platform package manager, then continue.
- Do not assume `Node.js`, `npm`, or `sails-js-cli` are part of this skill. Install JS tooling separately only when the active workflow actually needs it.
- Do not pin an arbitrary nightly date unless the target repository already requires one through a toolchain file or a failing build.
