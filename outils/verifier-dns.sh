#!/usr/bin/env bash
# Contrôle que la zone DNS de quantum-agency.fr est complète et correcte.
#
#   ./outils/verifier-dns.sh            interroge le résolveur public
#   ./outils/verifier-dns.sh ns.exemple interroge un serveur précis
#
# Les contrôles de courrier passent par le DNS, ceux du site par une vraie
# requête : derrière le proxy Cloudflare, les adresses IP du domaine sont
# celles de Cloudflare et ne disent plus rien de l'hébergement.
#
# Un résolveur local peut garder l'ancienne délégation en cache pendant une
# journée. Pour un résultat fiable pendant une bascule, interroger un résolveur
# public : ./outils/verifier-dns.sh 1.1.1.1

set -uo pipefail
DOMAINE="quantum-agency.fr"
SERVEUR="${1:-}"
[ -n "$SERVEUR" ] && AT="@$SERVEUR" || AT=""

ok=0; ko=0
verifier() {
  local libelle="$1" type="$2" nom="$3" attendu="$4"
  local obtenu
  obtenu="$(dig +short "$type" "$nom" $AT 2>/dev/null | tr -d '"' | tr -d ' ' | sort | tr '\n' ' ' | sed 's/ $//')"
  if printf '%s' "$obtenu" | grep -qi -- "$attendu"; then
    printf '  \033[32m✓\033[0m %-34s %s\n' "$libelle" "${obtenu:0:60}"
    ok=$((ok+1))
  else
    printf '  \033[31m✗\033[0m %-34s attendu : %s\n' "$libelle" "$attendu"
    printf '    %-34s obtenu  : %s\n' "" "${obtenu:-rien}"
    ko=$((ko+1))
  fi
}

printf '\nZone de %s %s\n\n' "$DOMAINE" "${SERVEUR:+(via $SERVEUR)}"

printf ' SITE\n'
# Derrière le proxy Cloudflare, le DNS ne rend plus les adresses de GitHub :
# il rend celles du réseau de Cloudflare. Vérifier les adresses n'a donc plus
# de sens, seule compte la réponse réelle du site.
verifier_http() {
  local libelle="$1" url="$2" attendu="$3"
  local code
  code="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$url" 2>/dev/null)"
  if [ "$code" = "$attendu" ]; then
    printf '  \033[32m✓\033[0m %-34s %s\n' "$libelle" "$code"
    ok=$((ok+1))
  else
    printf '  \033[31m✗\033[0m %-34s attendu %s, obtenu %s\n' "$libelle" "$attendu" "${code:-aucune réponse}"
    ko=$((ko+1))
  fi
}
verifier_http "accueil" "https://$DOMAINE/" 200
verifier_http "une page intérieure" "https://$DOMAINE/services.html" 200
verifier_http "version anglaise" "https://$DOMAINE/en/" 200
verifier_http "www redirige" "https://www.$DOMAINE/" 301

printf '\n RÉCEPTION DES E-MAILS\n'
verifier "MX principal" MX "$DOMAINE" "mx1.improvmx.com"
verifier "MX secours" MX "$DOMAINE" "mx2.improvmx.com"
verifier "SPF" TXT "$DOMAINE" "include:spf.improvmx.com"

printf '\n ENVOI DEPUIS LE FORMULAIRE\n'
verifier "DKIM Resend" TXT "resend._domainkey.$DOMAINE" "p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIHcnZKX57fO3tKxVCAT"
verifier "DMARC" TXT "_dmarc.$DOMAINE" "v=DMARC1"
# Retours de Resend : sans eux, les rejets et les plaintes ne reviennent pas,
# et la réputation du domaine se dégrade sans que rien ne le signale.
verifier "MX de retour Resend" MX "send.$DOMAINE" "feedback-smtp.eu-west-1.amazonses.com"
verifier "SPF de retour Resend" TXT "send.$DOMAINE" "include:amazonses.com"

printf '\n SERVEURS DE NOMS\n'
printf '  %s\n' "$(dig +short NS "$DOMAINE" $AT | tr '\n' ' ')"

printf '\n %s contrôle(s) au vert, %s en échec\n\n' "$ok" "$ko"
[ "$ko" -eq 0 ] || exit 1
