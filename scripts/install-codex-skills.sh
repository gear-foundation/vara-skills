#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CODEX_HOME="${CODEX_HOME:-${HOME}/.codex}"
TARGET_DIR="${CODEX_HOME}/skills"
PACK_NAME="vara-skills"

mkdir -p "${TARGET_DIR}"

pack_target="${TARGET_DIR}/${PACK_NAME}"
ln -sfn "${REPO_ROOT}" "${pack_target}"
printf 'INSTALLED_PACK=%s\n' "${PACK_NAME}"
printf 'TARGET=%s\n' "${pack_target}"

find "${REPO_ROOT}/skills" -mindepth 1 -maxdepth 1 -type d | LC_ALL=C sort | while IFS= read -r skill_dir; do
  skill_name="$(basename "${skill_dir}")"
  target_path="${TARGET_DIR}/${skill_name}"
  ln -sfn "${skill_dir}" "${target_path}"
  printf 'INSTALLED_SKILL=%s\n' "${skill_name}"
  printf 'TARGET=%s\n' "${target_path}"
done
