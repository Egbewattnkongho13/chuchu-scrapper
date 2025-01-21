#!/bin/bash

# execute script from project root
ROOT_DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )/.." &> /dev/null && pwd)"
SCRAPPER_DIR="$ROOT_DIR/chuchu_scrapper"
pushd $ROOT_DIR &> /dev/null

# Install dependencies & Lint
if [ -f "requirements-lint.txt" ]; then
    echo "Install lint requirements."
    pip install -r requirements-lint.txt
    python -m black $SCRAPPER_DIR
    python -m isort $SCRAPPER_DIR
else
    poetry install
    poetry run black $SCRAPPER_DIR
    poetry run isort $SCRAPPER_DIR
fi