#!/usr/bin/env bash
# Branche les formulaires du site sur une URL de Worker déjà déployé.
#   ./brancher.sh https://quantum-formulaire.exemple.workers.dev
set -euo pipefail
URL="${1:-}"
[ -n "$URL" ] || { echo "Usage : ./brancher.sh <url-du-worker>"; exit 1; }
cd "$(dirname "$0")/.."
LC_ALL=C sed -i '' "s#data-webhook=\"[^\"]*\"#data-webhook=\"$URL\"#g" ./*.html en/*.html
echo "$(grep -l "data-webhook=\"$URL\"" ./*.html en/*.html | wc -l | tr -d ' ') fichiers branchés (12 attendus)."
