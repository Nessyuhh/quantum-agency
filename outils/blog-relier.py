#!/usr/bin/env python3
"""
Repose le maillage interne sur des articles déjà écrits, sans les réécrire.

POURQUOI CE FICHIER EXISTE
La première version de la pose de liens ne cherchait qu'un seul mot par cible et
ne plaçait que 0 à 3 liens par article. Régénérer le texte pour corriger ça
serait absurde : le texte est bon, c'est le maillage qui manquait.

Ce script reprend le corps de chaque article, retire les liens déjà posés par
l'ancienne passe, et applique la nouvelle logique. Le texte n'est jamais touché.

    python3 outils/blog-relier.py           # tous les articles
    python3 outils/blog-relier.py --essai   # montre sans écrire
"""

import importlib.util
import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
BLOG = RACINE / 'blog'

spec = importlib.util.spec_from_file_location('g', RACINE / 'outils' / 'blog-generer.py')
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)


def main():
    essai = '--essai' in sys.argv
    index = {s[0]: i for i, s in enumerate(G.SUJETS)}
    total_avant = total_apres = traites = 0

    for f in sorted(BLOG.glob('*.html')):
        if f.stem not in index:
            continue                      # article historique, hors catalogue
        s = f.read_text(encoding='utf-8')
        d = s.find('<div class="art-body">')
        fin = s.find('</div>\n  <aside')
        if fin < 0:
            fin = s.find('<aside')
        if d < 0 or fin < 0:
            print(f'  ⚠ {f.stem} : corps introuvable')
            continue

        corps = s[d + len('<div class="art-body">'):fin]
        avant = corps.count('<a href')

        # ⚠️ On retire les liens INTERNES posés précédemment, jamais le texte :
        # le motif ne garde que le contenu de l'ancre.
        propre = re.sub(r'<a href="/(?:blog/)?[^"]*"[^>]*>(.*?)</a>', r'\1', corps)

        relie, poses = G.poser_liens(propre, G.SUJETS[index[f.stem]], index[f.stem])
        total_avant += avant
        total_apres += poses
        traites += 1
        if not essai:
            f.write_text(s[:d + len('<div class="art-body">')] + relie + s[fin:],
                         encoding='utf-8')
        print(f'  {f.stem[:44]:46} {avant:>2} → {poses:>2} liens')

    print(f'\n  {traites} articles · {total_avant} → {total_apres} liens internes'
          f' ({total_apres / traites:.1f} par article)' if traites else '  aucun article')
    if essai:
        print('  (essai : rien écrit)')


if __name__ == '__main__':
    main()
