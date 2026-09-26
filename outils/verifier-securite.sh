#!/usr/bin/env bash
# Contrôle, sur le site en production, les en-têtes de sécurité et
# l'inaccessibilité des fichiers internes.
#
#   ./outils/verifier-securite.sh
#
# Les en-têtes sont posés par Cloudflare (prompt 5 de PROMPTS-EXTERNES.md) :
# GitHub Pages ne permet pas d'en envoyer. Tant que ce prompt n'a pas été
# exécuté, les contrôles d'en-têtes échouent, c'est attendu.

set -uo pipefail
SITE="https://quantum-agency.fr"
ok=0; ko=0

marque() {
  if [ "$1" = ok ]; then printf '  \033[32m✓\033[0m %s\n' "$2"; ok=$((ok+1))
  else printf '  \033[31m✗\033[0m %s\n' "$2"; ko=$((ko+1)); fi
}

entetes="$(curl -sSI "$SITE/" | tr -d '\r')"
exige() {
  if printf '%s\n' "$entetes" | grep -qi "^$1: .*$2"; then marque ok "$1"
  else marque ko "$1 attendu, contenant « $2 »"; fi
}

echo "En-têtes de la page d'accueil"
exige strict-transport-security 'max-age=[0-9]\{8\}'
exige x-content-type-options nosniff
exige x-frame-options DENY
exige content-security-policy "frame-ancestors 'none'"
exige referrer-policy strict-origin-when-cross-origin
exige permissions-policy 'camera=()'
exige cross-origin-opener-policy same-origin

echo "Politique de sécurité du contenu dans la page"
if curl -sS "$SITE/" | grep -q 'http-equiv="Content-Security-Policy"'; then marque ok 'balise CSP présente'
else marque ko 'balise CSP absente, publier la dernière version'; fi

echo "Redirections"
code="$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' "http://quantum-agency.fr/")"
case "$code" in 301\ https://quantum-agency.fr/*) marque ok "http vers https ($code)";; *) marque ko "http vers https, obtenu : $code";; esac
code="$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' "https://www.quantum-agency.fr/")"
case "$code" in 301\ https://quantum-agency.fr/*) marque ok "www vers domaine nu ($code)";; *) marque ko "www vers domaine nu, obtenu : $code";; esac

echo "Fichiers internes, qui ne doivent pas être servis"
for chemin in JOURNAL-REFONTE.md ARBORESCENCE.md formulaire/worker.js formulaire/deployer.sh formulaire/wrangler.toml outils/PROMPTS-EXTERNES.md outils/charte-sync.py; do
  code="$(curl -s -o /dev/null -w '%{http_code}' "$SITE/$chemin")"
  if [ "$code" = 403 ] || [ "$code" = 404 ]; then marque ok "/$chemin ($code)"
  else marque ko "/$chemin répond $code"; fi
done

echo "Fichiers publics attendus"
for chemin in robots.txt sitemap.xml llms.txt llms-full.txt .well-known/security.txt; do
  code="$(curl -s -o /dev/null -w '%{http_code}' "$SITE/$chemin")"
  [ "$code" = 200 ] && marque ok "/$chemin" || marque ko "/$chemin répond $code"
done

echo
echo "$ok contrôle(s) réussi(s), $ko échec(s)."
[ "$ko" -eq 0 ]
