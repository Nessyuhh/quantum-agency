#!/bin/bash
# Sert la variante en local, accessible depuis le téléphone sur le même Wi-Fi.
#   ./servir.sh          → variante Gemini sur le port 8896
#   ./servir.sh 8897     → autre port
# Arrêter : Ctrl-C, ou   pkill -f 'http.server 8896'

PORT="${1:-8896}"
DOSSIER="$(cd "$(dirname "$0")/gemini" && pwd)"
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null)

echo
echo "  Quantum — variante Gemini"
echo "  ─────────────────────────────────────────────"
echo "  dossier      $DOSSIER"
echo "  ordinateur   http://localhost:$PORT"
[ -n "$IP" ] && echo "  téléphone    http://$IP:$PORT   (même Wi-Fi)"
echo "  ─────────────────────────────────────────────"
echo "  Ctrl-C pour arrêter"
echo

# --bind 0.0.0.0 pour que le téléphone puisse joindre la machine. Le serveur ne
# sert que ce dossier, et uniquement sur le réseau local.
cd "$DOSSIER" && exec python3 -m http.server "$PORT" --bind 0.0.0.0
