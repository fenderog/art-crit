#!/bin/bash
set -e

echo "=== Building Morphic Brand Identity Assets ==="
python3 src/build_assets.py
python3 src/animate_logo.py
echo "=== Build Complete ==="
