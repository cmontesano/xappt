#!/usr/bin/env bash

SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_PATH="$(realpath -s "$SCRIPT_PATH/../dist")"

python3 -m twine upload -r testpypi "$DIST_PATH/*"
