#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-${HOME}/.codex}"
TARGET_DIR="${CODEX_HOME}/skills"

mkdir -p "${TARGET_DIR}"

for skill_dir in "${REPO_ROOT}"/skills/*; do
  [[ -d "${skill_dir}" ]] || continue
  skill_name="$(basename "${skill_dir}")"
  target_path="${TARGET_DIR}/${skill_name}"
  ln -sfn "${skill_dir}" "${target_path}"
  printf 'INSTALLED_SKILL=%s\n' "${skill_name}"
  printf 'TARGET=%s\n' "${target_path}"
done
