#!/usr/bin/env python3
"""Reconstruit le bloc FAQPage de chaque page à partir de ses questions visibles.

Les données structurées et le texte affiché avaient divergé sur trois articles :
une balise fermante mal écrite avait fait disparaître une question du bloc, et
sur un troisième article deux questions s'étaient fondues en une seule, avec un
retour à la ligne au milieu d'une chaîne, ce qui rendait le JSON invalide et
donc le bloc entier ignoré par les moteurs.

Déclarer une question dans les données structurées sans l'afficher, ou
l'inverse, est un écart que Google sanctionne. Plutôt que de corriger à la main,
le bloc est régénéré depuis le HTML : la page devient la source unique.

Usage : python3 outils/resynchroniser-faq.py [--verifier]
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


def questions_visibles(s):
    """Rend la liste (question, réponse) telle que le visiteur la lit."""
    bloc = re.search(r'<section class="art-faq".*?</section>', s, re.S)
    if not bloc:
        return []
    paires = []
    for q, r in re.findall(r'<h3>(.*?)</h3>\s*<p>(.*?)</p>', bloc.group(0), re.S):
        nettoyer = lambda t: html.unescape(re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', t))).strip()
        paires.append((nettoyer(q), nettoyer(r)))
    return paires


def traiter(p, verifier):
    s = p.read_text(encoding='utf-8')
    paires = questions_visibles(s)
    if not paires:
        return None

    bloc = None
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        if '"FAQPage"' in m.group(1):
            bloc = m
    if bloc is None:
        return None

    try:
        avant = len(json.loads(bloc.group(1))['mainEntity'])
    except Exception:
        avant = 'invalide'
    if avant == len(paires):
        return None

    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}}
        for q, r in paires]}
    remplacement = '<script type="application/ld+json">%s</script>' % json.dumps(
        schema, ensure_ascii=False, separators=(',', ':'))
    s = s[:bloc.start()] + remplacement + s[bloc.end():]

    if not verifier:
        p.write_text(s, encoding='utf-8')
    return avant, len(paires)


def main():
    verifier = '--verifier' in sys.argv
    n = 0
    for p in pages():
        r = traiter(p, verifier)
        if r:
            n += 1
            print('  %-48s %s question(s) declarees -> %d' % (p.relative_to(RACINE), r[0], r[1]))
    print('\n%d page(s) %s' % (n, 'a resynchroniser' if verifier else 'resynchronisees'))
    if verifier and n:
        sys.exit(1)


if __name__ == '__main__':
    main()
