#!/bin/bash

# Execute script from project root
PROJ_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." &> /dev/null && pwd)"
SCRAPPER_DIR="$PROJ_ROOT_DIR/chuchu_scrapper"
pushd "$PROJ_ROOT_DIR" &> /dev/null

# Check if running in GitHub Actions
IS_GHA=false
if [ -n "$GITHUB_ACTIONS" ]; then
    IS_GHA=true
fi

# Function to run black
run_black_poetry() {
    if $IS_GHA; then
        echo "Running black in check mode..."
        poetry run python -m black --check "$SCRAPPER_DIR"
    else
        echo "Running black to format code..."
        poetry run python -m black "$SCRAPPER_DIR"
    fi
}

run_black() {
    if $IS_GHA; then
        echo "Running black in check mode..."
        python3 -m black --check "$SCRAPPER_DIR"
    else
        echo "Running black to format code..."
        python3 -m black "$SCRAPPER_DIR"
    fi
}

# Function to run isort
run_isort_poetry() {
    if $IS_GHA; then
        echo "Running isort in check mode..."
        poetry run python -m isort --check-only "$SCRAPPER_DIR"
    else
        echo "Running isort to format code..."
        poetry run python -m isort "$SCRAPPER_DIR"
    fi
}

run_isort() {
    if $IS_GHA; then
        echo "Running isort in check mode..."
        python3 -m isort --check-only "$SCRAPPER_DIR"
    else
        echo "Running isort to format code..."
        python3 -m isort "$SCRAPPER_DIR"
    fi
}

# Install dependencies & Lint
if [ -f "requirements-lint.txt" ]; then
    echo "Install lint requirements."
    pip install -r requirements-lint.txt --break-system-packages

    run_black
    run_isort
else
    poetry install

    run_black_poetry
    run_isort_poetry
fi

popd &> /dev/null




# if on GHA black, isort  should only check linting
# if you are on local it should lint the code

# make this script to lint on local but only check in CI
