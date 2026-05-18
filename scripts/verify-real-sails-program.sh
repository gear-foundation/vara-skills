#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAILS_RS_PATH="${SAILS_RS_PATH:-"$ROOT/../sails/rs"}"

if [ ! -f "$SAILS_RS_PATH/Cargo.toml" ]; then
  echo "missing Sails workspace at $SAILS_RS_PATH" >&2
  echo "set SAILS_RS_PATH=/path/to/sails/rs if ../sails/rs is not available" >&2
  exit 1
fi

if ! cargo sails --help >/dev/null 2>&1; then
  echo "missing cargo-sails; install with: cargo install sails-cli" >&2
  exit 1
fi

if ! rustup target list --installed | grep -qx "wasm32v1-none"; then
  echo "missing Rust target wasm32v1-none; install with: rustup target add wasm32v1-none" >&2
  exit 1
fi

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

APP_DIR="$TMPDIR/real-check"
cargo sails new "$APP_DIR" --name real-check --sails-path "$SAILS_RS_PATH" --offline

cat > "$APP_DIR/tests/header_payload.rs" <<'RS'
use real_check_client::{RealCheckClientProgram, real_check::io::DoSomething};

#[test]
fn generated_service_call_uses_sails_header_v1() {
    let payload = DoSomething::encode_call(RealCheckClientProgram::ROUTE_ID_REAL_CHECK);

    assert!(payload.len() >= 16);
    assert_eq!(&payload[0..2], b"GM");
    assert_eq!(payload[2], 1);
    assert_eq!(payload[3], 0x10);
}
RS

export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-"$ROOT/target/verify-real-sails-program"}"

cargo build --manifest-path "$APP_DIR/Cargo.toml" --release --locked
cargo test --manifest-path "$APP_DIR/Cargo.toml" --workspace --locked

test -s "$APP_DIR/client/real_check_client.idl"
test -s "$APP_DIR/client/src/real_check_client.rs"
grep -q "ROUTE_ID_REAL_CHECK" "$APP_DIR/client/src/real_check_client.rs"
grep -q "io_struct_impl!(DoSomething" "$APP_DIR/client/src/real_check_client.rs"

echo "real Sails program verification ok"
