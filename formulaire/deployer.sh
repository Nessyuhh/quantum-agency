#!/usr/bin/env bash
# Déploie le Worker du formulaire et branche le site dessus.
#
#   cd formulaire && ./deployer.sh
#
# Deux étapes demandent votre intervention : l'authentification Cloudflare,
# qui ouvre une page dans le navigateur, et la clé Resend, qui est saisie
# à la main pour ne jamais être écrite sur le disque.

set -euo pipefail
cd "$(dirname "$0")"
RACINE="$(cd .. && pwd)"

titre() { printf '\n\033[1m%s\033[0m\n' "$1"; }

command -v wrangler >/dev/null || { echo "wrangler est introuvable. Installez-le : npm install -g wrangler"; exit 1; }

titre "1/5  Compte Cloudflare"
if wrangler whoami 2>&1 | grep -q "not authenticated"; then
  echo "Une page va s'ouvrir dans votre navigateur. Créez le compte si besoin, puis autorisez."
  wrangler login
else
  echo "Session déjà ouverte."
fi

titre "2/5  Clé Resend"
if wrangler secret list 2>/dev/null | grep -q RESEND_API_KEY; then
  echo "La clé est déjà en place. Pour la remplacer : wrangler secret put RESEND_API_KEY"
else
  echo "Collez la clé Resend dédiée au site (créée sur resend.com, permission d'envoi seule)."
  echo "Elle n'est ni affichée ni enregistrée sur le disque."
  wrangler secret put RESEND_API_KEY
fi

titre "3/5  Déploiement"
SORTIE="$(wrangler deploy 2>&1 | tee /dev/tty)"
URL="$(printf '%s' "$SORTIE" | grep -oE 'https://[a-z0-9.-]+\.workers\.dev' | head -1)"
[ -n "$URL" ] || { echo "URL du Worker introuvable dans la sortie. Relevez-la et lancez : ./brancher.sh <url>"; exit 1; }
echo "Worker en ligne : $URL"

titre "4/5  Branchement du site"
cd "$RACINE"
# LC_ALL=C : sed de macOS refuse certains octets UTF-8 sans cette variable.
LC_ALL=C sed -i '' "s#data-webhook=\"[^\"]*\"#data-webhook=\"$URL\"#g" ./*.html en/*.html
N="$(grep -l "data-webhook=\"$URL\"" ./*.html en/*.html | wc -l | tr -d ' ')"
echo "$N fichiers branchés sur le Worker (12 attendus)."

titre "5/5  Vérification"
CODE="$(curl -s -o /tmp/reponse-worker.json -w '%{http_code}' -X POST "$URL" \
  -H 'Content-Type: application/json' -H 'Origin: https://quantum-agency.fr' \
  -d '{"nom":"Essai de mise en service","email":"contact@quantum-agency.fr","entreprise":"Quantum Consulting","message":"Message de test envoye par deployer.sh","page":"/contact.html","timestamp":"'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'"}')"
REFUS="$(curl -s -o /dev/null -w '%{http_code}' -X POST "$URL" \
  -H 'Content-Type: application/json' -H 'Origin: https://exemple-etranger.fr' -d '{}')"

echo "Envoi depuis une origine autorisée : $CODE (200 attendu)"
echo "Envoi depuis une origine étrangère : $REFUS (403 attendu)"
[ "$CODE" = "200" ] || { echo "Réponse du Worker : $(cat /tmp/reponse-worker.json)"; echo "Vérifiez la clé Resend et que quantum-agency.fr est un domaine vérifié chez Resend."; exit 1; }

titre "Terminé"
echo "Un e-mail de test doit être arrivé sur contact@quantum-agency.fr."
echo "Relisez la modification puis validez :"
echo "  git diff --stat"
echo "  git commit -am \"Formulaire d'audit branché sur le Worker\""
