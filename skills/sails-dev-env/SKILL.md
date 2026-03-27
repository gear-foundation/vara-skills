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
4. Install the Sails Rust CLI with `cargo install sails-cli@1.0.0-beta.1 --locked@1.0.0-beta.1 --locked`, which provides `cargo-sails` and the standard greenfield bootstrap command `cargo sails new <project-name>`.
5. Install the latest official `gear` release binary from `https://get.gear.rs/` (see Commands below for platform-specific download).
6. Verify the toolchain with `rustup show`, `cargo sails --version`, and `gear --version`.
7. Route back into `../sails-new-app/SKILL.md`, `../ship-sails-app/SKILL.md`, `../sails-gtest/SKILL.md`, or `../sails-local-smoke/SKILL.md` depending on the builder's next task.

## Commands

### macOS or Linux

```bash
command -v rustup >/dev/null 2>&1 || curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
# After fresh install, restart the shell or source the env so cargo/rustc resolve:
. "${HOME}/.cargo/env"

rustup toolchain install stable
rustup toolchain install nightly
rustup default stable
rustup target add wasm32v1-none --toolchain stable
rustup target add wasm32v1-none --toolchain nightly
rustup target add wasm32-unknown-unknown --toolchain stable
rustup target add wasm32-unknown-unknown --toolchain nightly

cargo install sails-cli@1.0.0-beta.1 --locked

# Install gear binary from official releases (auto-detect architecture)
GEAR_VERSION="v1.10.0"
case "$(uname -s)-$(uname -m)" in
  Darwin-arm64)  GEAR_ARCH="aarch64-apple-darwin" ;;
  Darwin-x86_64) GEAR_ARCH="x86_64-apple-darwin" ;;
  Linux-x86_64)  GEAR_ARCH="x86_64-unknown-linux-gnu" ;;
  Linux-aarch64) GEAR_ARCH="aarch64-unknown-linux-gnu" ;;
  *) echo "Unsupported platform: $(uname -s)-$(uname -m)"; exit 1 ;;
esac
mkdir -p "${HOME}/.local/bin"
curl -sSf "https://get.gear.rs/gear-${GEAR_VERSION}-${GEAR_ARCH}.tar.xz" | tar -xJ -C "${HOME}/.local/bin"
export PATH="${HOME}/.local/bin:${PATH}"

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

cargo install sails-cli@1.0.0-beta.1 --locked

# Install gear binary from official releases
$GearVersion = "v1.10.0"
$GearDest = "$env:USERPROFILE\AppData\Local\Programs\gear\bin"
New-Item -ItemType Directory -Force -Path $GearDest | Out-Null
Invoke-WebRequest -Uri "https://get.gear.rs/gear-$GearVersion-x86_64-pc-windows-msvc.zip" -OutFile "$env:TEMP\gear.zip"
Expand-Archive -Path "$env:TEMP\gear.zip" -DestinationPath $GearDest -Force
$env:PATH = "$GearDest;$env:PATH"

rustup show
cargo sails --version
cargo sails --help
gear --version
```

## Guardrails

- Keep this skill self-contained. Do not depend on a sibling `gear` checkout or machine-local scripts outside this skill directory. The `gear` binary is downloaded directly from `https://get.gear.rs/` official releases. The `scripts/install-gear.sh` and `scripts/install-gear.ps1` helpers in this skill directory are available as an alternative when a more flexible install is needed (e.g., custom tags or targets).
- Prefer the latest official `gear` release binary over building the node from source unless the user asks for a specific tag or source build.
- Treat base package-manager bootstrap as outside scope. If host tools such as `curl`, `tar`, `xz`, or `winget` are missing, install them with the platform package manager, then continue.
- Do not assume `Node.js`, `npm`, or `sails-js-cli` are part of this skill. Install JS tooling separately only when the active workflow actually needs it.
- Do not pin an arbitrary nightly date unless the target repository already requires one through a toolchain file or a failing build.
