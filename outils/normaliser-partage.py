#!/usr/bin/env python3
"""Répare les images de partage et ramène toutes les adresses sur le domaine nu.

Deux défauts hérités, invisibles depuis le site lui-même :

1. Les 105 articles du blog désignent `og-image.svg` comme image de partage.
   Aucun réseau social n'accepte le SVG : ni LinkedIn, ni X, ni WhatsApp, ni
   Slack. Ils déclarent pourtant `twitter:card = summary_large_image`, donc ils
   promettent une grande vignette et n'en livrent aucune. Ce fichier date par
   ailleurs d'avant la refonte et porte l'ancienne identité.

2. Une partie des adresses absolues pointent sur `www.quantum-agency.fr`, qui
   répond 301 vers le domaine nu. Un canonique qui redirige est un signal
   contradictoire, et plusieurs robots de partage abandonnent à la redirection
   plutôt que de la suivre.

Le script ajoute aussi les dimensions et le texte de remplacement de l'image,
que les robots utilisent pour réserver la place de la vignette avant de l'avoir
téléchargée, et `twitter:image` là où il manque.

Usage : python3 outils/normaliser-partage.py [--verifier]
"""
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOMAINE = 'https://quantum-agency.fr'
IMAGE = DOMAINE + '/og-image.png'
ALT = "Quantum Consulting, conseil et formation en intelligence artificielle pour les PME et ETI"

# Les archives gardent l'ancien site tel qu'il était : on n'y touche pas.
EXCLUS = {'archives'}


def fichiers():
    for motif in ('*.html', 'en/*.html', 'blog/*.html', '*.xml', '*.txt'):
        for p in sorted(RACINE.glob(motif)):
            if not (set(p.relative_to(RACINE).parts) & EXCLUS):
                yield p


def corriger(s):
    """Rend le texte corrigé et la liste des corrections appliquées."""
    faits = []

    n = s.count('https://www.quantum-agency.fr')
    if n:
        s = s.replace('https://www.quantum-agency.fr', DOMAINE)
        faits.append('%d adresse(s) www' % n)

    if 'og-image.svg' in s:
        s = s.replace(DOMAINE + '/og-image.svg', IMAGE).replace('/og-image.svg', '/og-image.png')
        faits.append('image SVG remplacee par le PNG')

    # Dimensions et texte de remplacement, juste apres og:image.
    m = re.search(r'<meta property="og:image" content="[^"]*">\n', s)
    if m and 'og:image:width' not in s:
        ajout = ('<meta property="og:image:width" content="1200">\n'
                 '<meta property="og:image:height" content="630">\n'
                 '<meta property="og:image:alt" content="%s">\n' % ALT)
        s = s[:m.end()] + ajout + s[m.end():]
        faits.append('dimensions et texte de remplacement')

    # twitter:image : sans lui, X retombe sur og:image, ce qui a longtemps
    # suffi, mais la balise explicite evite d'en dependre.
    if 'og:image' in s and 'twitter:image' not in s:
        for ancre in (r'<meta name="twitter:description" content="[^"]*">\n',
                      r'<meta name="twitter:title" content="[^"]*">\n',
                      r'<meta name="twitter:card" content="[^"]*">\n'):
            m = re.search(ancre, s)
            if m:
                s = s[:m.end()] + '<meta name="twitter:image" content="%s">\n' % IMAGE + s[m.end():]
                faits.append('twitter:image')
                break

    return s, faits


def main():
    verifier = '--verifier' in sys.argv
    touches = 0
    for p in fichiers():
        avant = p.read_text(encoding='utf-8')
        apres, faits = corriger(avant)
        if apres == avant:
            continue
        touches += 1
        if not verifier:
            p.write_text(apres, encoding='utf-8')
        print('  %-46s %s' % (p.relative_to(RACINE), ', '.join(faits)))

    print('\n%d fichier(s) %s' % (touches, 'a corriger' if verifier else 'corriges'))
    if verifier and touches:
        sys.exit(1)


if __name__ == '__main__':
    main()
