#!/bin/sh
# Build all SVGs, then export PNG presentations into ./output
set -e
cd "$(dirname "$0")/.."
node src/build.mjs
src/preview.sh tmp/loam-brand-sheet.svg output/loam-brand-sheet.png 1600 1600 1000
src/preview.sh output/loam-logo-light.svg output/loam-logo-light.png 1520 1520 600
src/preview.sh output/loam-app-icon.svg output/loam-app-icon.png 1024 1024 1024
