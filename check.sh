#!/bin/sh

echo "Running ruff format..."
uv tool run ruff format
echo

echo "Running ruff check with --fix..."
uv tool run ruff check --fix
echo

echo "Running pytest..."
uv run pytest