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

run isort --profile black "${workspace}"
run black "${workspace}"
