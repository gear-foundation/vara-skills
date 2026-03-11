#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ $# -lt 1 ]]; then
  echo "usage: run_gtest.sh <workspace> [cargo args...]" >&2
  exit 1
fi

WORKSPACE="$(cd "$1" && pwd)"
shift || true

if [[ ! -d "${WORKSPACE}" ]]; then
  echo "workspace not found: ${WORKSPACE}" >&2
  exit 1
fi

if [[ $# -gt 0 ]]; then
  CMD=(cargo test "$@")
else
  CMD=(cargo test --test gtest)
fi

LOGFILE="$(mktemp)"
set +e
(
  cd "${WORKSPACE}"
  "${CMD[@]}" -- --nocapture
) 2>&1 | tee "${LOGFILE}"
STATUS=${PIPESTATUS[0]}
set -e

python3 "${ROOT}/scripts/parse_test_output.py" "${LOGFILE}"
rm -f "${LOGFILE}"
exit "${STATUS}"
