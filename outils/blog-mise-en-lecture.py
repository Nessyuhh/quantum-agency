#!/usr/bin/env python3
"""
Applique la mise en lecture aux articles déjà écrits, sans toucher au texte.

CE QUE ÇA POSE
  · le style de lecture : paragraphes lisibles, tableaux qui défilent sur mobile
  · assets/article.js : sommaire, barre de progression, section active
  · la navigation article précédent / suivant, DANS LE MÊME PÔLE

POURQUOI SÉPARÉMENT DE LA GÉNÉRATION
Le texte est bon, c'est la mise en forme qui manquait. Régénérer 100 articles
pour poser un sommaire serait absurde, et on perdrait des textes déjà validés.
Ce script est rejouable : il ne pose que ce qui manque.
"""

import importlib.util
import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
BLOG = RACINE / 'blog'

spec = importlib.util.spec_from_file_location('c', RACINE / 'outils' / 'blog-construire.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def main():
    index = {s[0]: i for i, s in enumerate(C.SUJETS)}
    faits = 0
    for f in sorted(BLOG.glob('*.html')):
        s = f.read_text(encoding='utf-8')
        avant = s

        if '.art-progres{' not in s:
            s = s.replace('</head>', C.STYLE_LECTURE + '\n</head>', 1)
        if 'assets/article.js' not in s:
            s = s.replace('</body>', '<script src="/assets/article.js" defer></script>\n</body>', 1)

        # ⚠️ La navigation se pose entre le bloc « À lire aussi » et la fin de
        # l'article. Un article hors catalogue n'a pas de voisins : on le laisse.
        if f.stem in index and 'class="art-nav"' not in s:
            nav = C.nav_precedent_suivant(index[f.stem])
            if nav:
                i = s.find('</aside>')
                if i > 0:
                    s = s[:i + len('</aside>')] + '\n' + nav + s[i + len('</aside>'):]
                else:
                    s = s.replace('</article>', nav + '\n</article>', 1)

        if s != avant:
            f.write_text(s, encoding='utf-8')
            faits += 1

    print(f'  {faits} articles mis en lecture')

    # Contrôle : ce qui manque encore
    manque = []
    for f in sorted(BLOG.glob('*.html')):
        s = f.read_text(encoding='utf-8')
        pb = []
        if '.art-progres{' not in s: pb.append('style')
        if 'assets/article.js' not in s: pb.append('script')
        if f.stem in index and 'class="art-nav"' not in s: pb.append('nav')
        if pb: manque.append((f.stem, pb))
    if manque:
        print(f'  ⚠ incomplets : {len(manque)}')
        for n, pb in manque[:5]:
            print(f'     {n} — {", ".join(pb)}')
    else:
        print('  ✓ tous complets')


if __name__ == '__main__':
    main()
