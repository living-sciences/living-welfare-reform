#!/bin/bash
# Extract one country's EUROMOD model to container-local scratch.
# Usage: extract_country.sh <CC> <zip> <dest_root_parent>
# Produces $DEST/EUROMOD_RELEASES_<ver>/...  and prints the model root path.
set -e
CC=$1
ZIP=${2:-/workspace/eval/followup_staging/shared-data/euromod/EUROMOD_RELEASES_J2.54+.zip}
DEST=${3:-/tmp/em_$CC}
VER=$(unzip -Z1 "$ZIP" | grep -oE '^EUROMOD_RELEASES_[^/]+' | head -1)
rm -rf "$DEST"; mkdir -p "$DEST"
cd "$DEST"
unzip -q "$ZIP" \
  "$VER/XMLParam/Countries/$CC/*" \
  "$VER/XMLParam/Config/*" \
  "$VER/XMLParam/AddOns/MTR/*" \
  "$VER/XMLParam/AddOns/NRR/*" \
  "$VER/Input/${CC}_training_data.txt"
mkdir -p "$VER/Output"
echo "$DEST/$VER"
