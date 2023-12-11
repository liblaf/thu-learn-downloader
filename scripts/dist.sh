#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

OS=$1
ARCH=$2
PYTHON_VERSION=$3
exeExt=$4

rm --force --recursive --verbose dist
if python -m nuitka --standalone --onefile \
  --output-filename="tld-$OS-$ARCH-py$PYTHON_VERSION$exeExt" \
  --output-dir="dist" --remove-output main.py; then
  exit 0
else
  status=$?
fi

rm --force --recursive --verbose dist
if pyinstaller --distpath="dist" --onefile \
  --name="tld-$OS-$ARCH-py$PYTHON_VERSION" main.py; then
  exit 0
else
  status=$?
fi

exit $status
