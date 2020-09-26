#!/usr/bin/env bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_PATH="$(realpath -s "$SCRIPT_PATH/..")"

python3 "$ROOT_PATH/setup.py" sdist bdist_wheel
