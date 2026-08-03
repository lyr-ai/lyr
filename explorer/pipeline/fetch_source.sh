#!/usr/bin/env bash
# Fetch the public-domain source (Project Gutenberg #1342, Pride and Prejudice).
# Not committed to the repo — regenerable, ~700 KB.
set -e
DATA="$(cd "$(dirname "$0")/.." && pwd)/data"
mkdir -p "$DATA"
curl -s -L -o "$DATA/pride-and-prejudice.raw.txt" \
  "https://www.gutenberg.org/files/1342/1342-0.txt"
echo "fetched -> explorer/data/pride-and-prejudice.raw.txt ($(wc -l < "$DATA/pride-and-prejudice.raw.txt") lines)"
