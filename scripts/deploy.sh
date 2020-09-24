#!/usr/bin/env bash
python3 -m twine upload dist/*
rm dist/xappt*.tar.gz
rm dist/xappt*.whl
