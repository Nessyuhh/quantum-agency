#!/usr/bin/env python3
"""
Traduit les chaînes manquantes, par lots, via bin/ai.

FORMAT NUMÉROTÉ PLUTÔT QUE JSON
Demander du JSON à un modèle produit régulièrement une virgule en trop ou un
guillemet non échappé, et c'est tout le lot qui est perdu. Des lignes numérotées
se réalignent par index : une ligne abîmée ne coûte qu'une ligne.

REPRISE
Le fichier de sortie est relu au démarrage : relancer le script ne retraduit que
ce qui manque encore. Utile parce qu'un palier gratuit finit toujours par
refuser une requête.
"""

import json
import pathlib
import re
import subprocess
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
AI = pathlib.Path.home() / 'Projects' / 'atelier-ia' / 'bin' / 'ai'
ENTREE = RACINE / 'outils' / 'i18n-manquantes.json'
SORTIE = RACINE / 'outils' / 'i18n-traductions.json'
LOT = 30

CONSIGNE = """Traduis en anglais les lignes numérotées ci-dessous. Ce sont des textes d'un site de cabinet de conseil en intelligence artificielle destiné à des dirigeants d'entreprise.

RÈGLES ABSOLUES :
- Rends EXACTEMENT le même nombre de lignes, avec la même numérotation.
- Une ligne = une traduction. Rien d'autre sur la ligne.
- Conserve la ponctuation de fin, les flèches (→), les symboles et les majuscules de style.
- Ne traduis pas les noms propres ni les noms de produits : Quantum Consulting, Claude, GPT-4o, Mistral, n8n, Make, Supabase, RGPD reste GDPR.
- Registre professionnel, sobre, orienté dirigeant. Pas de superlatifs ajoutés.
- Aucun commentaire, aucune explication, aucun bloc de code.

LIGNES :
"""


def charger(p, defaut):
    try:
        return json.loads(p.read_text(encoding='utf-8'))
    except Exception:
        return defaut


def traduire_lot(lot):
    texte = CONSIGNE + '\n'.join(f'{i+1}. {s}' for i, s in enumerate(lot))
    r = subprocess.run([str(AI), '--role', 'redaction', texte],
                       capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        return None, (r.stderr or '').strip()[-160:]
    lignes = {}
    for ligne in r.stdout.splitlines():
        m = re.match(r'\s*(\d+)\s*[.)]\s*(.+?)\s*$', ligne)
        if m:
            lignes[int(m.group(1))] = m.group(2)
    return lignes, None


def main():
    manquantes = charger(ENTREE, [])
    faites = charger(SORTIE, {})
    reste = [s for s in manquantes if s not in faites]
    print(f'  {len(manquantes)} à traduire · {len(faites)} déjà faites · {len(reste)} restantes')
    if not reste:
        return

    lots = [reste[i:i + LOT] for i in range(0, len(reste), LOT)]
    for n, lot in enumerate(lots, 1):
        rep, err = traduire_lot(lot)
        if rep is None:
            print(f'  lot {n}/{len(lots)} ✗ {err}')
            continue
        # ⚠️ Garde d'alignement : si le modèle ne rend pas exactement le même
        # nombre de lignes, les index ne correspondent plus et on collerait la
        # traduction d'une chaîne sur une autre. On jette le lot entier — un lot
        # perdu se rejoue, une traduction mal appariée passe inaperçue.
        if len(rep) != len(lot):
            print(f'  lot {n}/{len(lots)} ✗ {len(rep)} lignes rendues pour {len(lot)} — lot écarté')
            continue
        ok = 0
        for i, src in enumerate(lot):
            t = (rep.get(i + 1) or '').strip()
            # Identique au français : légitime pour « Menu », « QUANTUM » ou un
            # nom propre. C'est le compte de lignes, plus haut, qui détecte un
            # décalage — pas la ressemblance.
            if t:
                faites[src] = t
                ok += 1
        SORTIE.write_text(json.dumps(faites, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'  lot {n}/{len(lots)} · {ok}/{len(lot)} · total {len(faites)}')

    print(f'\n  → {SORTIE.relative_to(RACINE)} · {len(faites)} traductions')


if __name__ == '__main__':
    main()
