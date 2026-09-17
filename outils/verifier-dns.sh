#!/usr/bin/env bash
# Contrôle que la zone DNS de quantum-agency.fr est complète et correcte.
#
#   ./outils/verifier-dns.sh            interroge le résolveur public
#   ./outils/verifier-dns.sh ns.exemple interroge un serveur précis
#
# À lancer AVANT la bascule vers Cloudflare, pour la photo de référence, puis
# APRÈS l'import chez Cloudflare, avant de changer les serveurs de noms chez
# Hostinger. Les deux sorties doivent être identiques.

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
for ip in 185.199.108.153 185.199.109.153 185.199.110.153 185.199.111.153; do
  verifier "A $ip" A "$DOMAINE" "$ip"
done
verifier "CNAME www" CNAME "www.$DOMAINE" "nessyuhh.github.io"

printf '\n RÉCEPTION DES E-MAILS\n'
verifier "MX principal" MX "$DOMAINE" "mx1.improvmx.com"
verifier "MX secours" MX "$DOMAINE" "mx2.improvmx.com"
verifier "SPF" TXT "$DOMAINE" "include:spf.improvmx.com"

printf '\n ENVOI DEPUIS LE FORMULAIRE\n'
verifier "DKIM Resend" TXT "resend._domainkey.$DOMAINE" "p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIHcnZKX57fO3tKxVCAT"
verifier "DMARC" TXT "_dmarc.$DOMAINE" "v=DMARC1"

printf '\n SERVEURS DE NOMS\n'
printf '  %s\n' "$(dig +short NS "$DOMAINE" $AT | tr '\n' ' ')"

printf '\n %s contrôle(s) au vert, %s en échec\n\n' "$ok" "$ko"
[ "$ko" -eq 0 ] || exit 1
