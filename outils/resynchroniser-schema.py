#!/usr/bin/env python3
"""Aligne les données structurées de chaque page sur ce que la page affiche.

Deux écarts constatés sur le blog :

1. Le dernier maillon du fil d'Ariane était coupé à soixante caractères, en
   plein milieu d'un mot : « Audit IA en PME : le guide complet pour
   cartographier vos op ». Le fil d'Ariane passe à la ligne tout seul, rien ne
   justifiait cette coupe. Elle est supprimée.

2. Sept articles avaient été retitrés sans que le fil d'Ariane structuré ni la
   description du schéma suivent. Un titre qui diffère entre la page et ses
   données structurées est exactement ce que Google demande d'éviter, puisque
   c'est le schéma qui alimente l'affichage dans les résultats.

La page reste la source unique : le script lit son h1, sa métadescription et
son fil d'Ariane visible, puis réécrit le schéma d'après eux, jamais l'inverse.

Usage : python3 outils/resynchroniser-schema.py [--verifier]
"""
import html
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent


def pages():
    for motif in ('*.html', 'en/*.html', 'blog/*.html'):
        yield from sorted(RACINE.glob(motif))


def traiter(p, verifier):
    s = p.read_text(encoding='utf-8')
    faits = []

    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', s, re.S)
    if not h1:
        return None
    titre_html = h1.group(1).strip()
    titre = html.unescape(re.sub(r'<[^>]+>', '', titre_html)).strip()

    d = re.search(r'<meta name="description" content="([^"]*)"', s)
    description = html.unescape(d.group(1)) if d else None

    # Fil d'Ariane visible : le dernier maillon porte le titre entier.
    m = re.search(r'(<span aria-current="page">)([^<]*)(</span>)', s)
    if m and m.group(2) != titre_html:
        s = s[:m.start(2)] + titre_html + s[m.end(2):]
        faits.append('fil d Ariane visible')

    def reecrire(bloc, modifier):
        nonlocal s
        try:
            donnees = json.loads(bloc.group(1))
        except Exception:
            return False
        if not modifier(donnees):
            return False
        neuf = '<script type="application/ld+json">%s</script>' % json.dumps(
            donnees, ensure_ascii=False, separators=(',', ':'))
        s = s[:bloc.start()] + neuf + s[bloc.end():]
        return True

    for _ in range(4):
        change = False
        for bloc in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try:
                genre = json.loads(bloc.group(1)).get('@type')
            except Exception:
                continue

            if genre == 'BreadcrumbList':
                def fil(d):
                    dernier = d['itemListElement'][-1]
                    if dernier.get('name') == titre:
                        return False
                    dernier['name'] = titre
                    return True
                if reecrire(bloc, fil):
                    faits.append('fil d Ariane structure'); change = True; break

            if genre in ('BlogPosting', 'Article') and description:
                def article(d):
                    besoin = d.get('headline') != titre or d.get('description') != description
                    d['headline'] = titre
                    d['description'] = description
                    return besoin
                if reecrire(bloc, article):
                    faits.append('titre et description du schema'); change = True; break
        if not change:
            break

    if not faits:
        return None
    if not verifier:
        p.write_text(s, encoding='utf-8')
    return faits


def main():
    verifier = '--verifier' in sys.argv
    n = 0
    for p in pages():
        faits = traiter(p, verifier)
        if faits:
            n += 1
            print('  %-48s %s' % (p.relative_to(RACINE), ', '.join(dict.fromkeys(faits))))
    print('\n%d page(s) %s' % (n, 'a resynchroniser' if verifier else 'resynchronisees'))
    if verifier and n:
        sys.exit(1)


if __name__ == '__main__':
    main()
