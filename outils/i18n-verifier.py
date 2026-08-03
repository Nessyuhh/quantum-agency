#!/usr/bin/env python3
"""
Vérifie que 100 % du site reste traduisible.

POURQUOI CE FICHIER EXISTE
Un dictionnaire complet à un instant donné ne vaut rien : il suffit d'un titre
réécrit pour rouvrir un trou, en silence. Ce script rejoue l'extraction et
échoue si une seule chaîne n'a pas de traduction.

À lancer après toute modification de texte :
    python3 outils/i18n-verifier.py

Code de sortie 1 s'il manque quoi que ce soit — utilisable dans un hook.
"""

import importlib.util
import json
import pathlib
import re
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent

spec = importlib.util.spec_from_file_location('ex', RACINE / 'outils' / 'i18n-extraire.py')
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)


def cles_du_dictionnaire():
    """Clés du dictionnaire — source unique, outils/i18n-traductions.json."""
    import json
    f = RACINE / 'outils' / 'i18n-traductions.json'
    return {k.strip() for k in json.loads(f.read_text(encoding='utf-8'))}


def main():
    par_page, toutes = ex.extraire()
    connues = cles_du_dictionnaire()
    manquantes = {s: v for s, v in toutes.items() if s not in connues}

    total = len(toutes)
    ok = total - len(manquantes)
    print(f'  {len(par_page)} pages · {total} chaînes uniques')
    print(f'  couverture : {ok}/{total}  ({round(ok/total*100)} %)')

    if not manquantes:
        print('\n  ✓ 100 % du site est traduisible')
        return 0

    print(f'\n  ⛔ {len(manquantes)} chaînes sans traduction :\n')
    par_p = {}
    for s, pages in manquantes.items():
        for p in pages:
            par_p.setdefault(p, []).append(s)
    for p, ss in sorted(par_p.items(), key=lambda x: -len(x[1])):
        print(f'  {p} ({len(ss)})')
        for s in ss[:4]:
            print(f'      « {s[:70]} »')
        if len(ss) > 4:
            print(f'      … et {len(ss)-4} autres')
    print('\n  Pour corriger :')
    print('    python3 outils/i18n-extraire.py && python3 outils/i18n-traduire.py')
    print('    python3 outils/i18n-generer.py')
    return 1


if __name__ == '__main__':
    sys.exit(main())
