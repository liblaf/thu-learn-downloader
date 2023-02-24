#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

function run() {
  if command -v gum > /dev/null 2>&1; then
    prefix="$(gum style --background=14 --padding="0 1" RUN)"
    message="$(gum style --foreground=14 "${*}")"
    gum join --horizontal "${prefix}" " " "${message}"
  fi
  "${@}"
}

workspace="$(git rev-parse --show-toplevel || pwd)"
cd "${workspace}"
name="$(poetry version | awk '{ print $1 }')"

run poetry install --with dev
run poetry run pyinstaller --onefile --name "${name}" "${workspace}/entry_point.py"
