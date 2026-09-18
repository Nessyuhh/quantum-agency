#!/usr/bin/env python3
"""Icônes du site, générées depuis le favicon du kit de marque (jamais dessinées à la main).

  python3 outils/icones.py [chemin/vers/favicon.svg]

Produit à la racine du site : apple-touch-icon.png (180, ce que Safari affiche dans la
grille des onglets, les favoris et l'écran d'accueil), favicon-32.png, favicon.ico (16, 32, 48).
Le favicon.svg du site reste la version sans tuile, pour les navigateurs qui le lisent.
Rendu par Chrome sans fenêtre, sur la tuile sombre du kit : Safari met les icônes sur fond
blanc et arrondit lui-même les coins, une icône transparente y paraîtrait délavée.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.expanduser('~/Desktop/Projets/Quantum Consulting/Logos-Quantum/favicon.svg')
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
# Safari pose l'icône tactile sur du noir avant d'arrondir lui-même les coins : elle doit
# être opaque, sur la couleur de la tuile. Les favicons gardent leurs coins transparents.
TUILE = '0d0720'
TAILLES = {'apple-touch-icon.png': (180, TUILE + 'ff'), 'favicon-32.png': (32, '00000000'), 'icone-512.png': (512, '00000000')}


def rendre(svg, taille, sortie, fond):
    page = os.path.join(tempfile.mkdtemp(), 'i.html')
    with open(page, 'w') as f:
        f.write(f'<!doctype html><html><body style="margin:0;background:transparent"><img src="file://{svg}" width="{taille}" height="{taille}" style="display:block"></body></html>')
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--default-background-color={fond}',
                    f'--window-size={taille},{taille}', f'--screenshot={sortie}', f'file://{page}'], check=True, capture_output=True)


def main(svg):
    if not os.path.exists(svg):
        print(f'introuvable : {svg}', file=sys.stderr); return 1
    for nom, (taille, fond) in TAILLES.items():
        rendre(svg, taille, os.path.join(RACINE, nom), fond)
        print(f'  {nom} ({taille} px)')
    grand = Image.open(os.path.join(RACINE, 'icone-512.png')).convert('RGBA')
    grand.save(os.path.join(RACINE, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
    os.remove(os.path.join(RACINE, 'icone-512.png'))
    print('  favicon.ico (16, 32, 48 px)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else KIT))
