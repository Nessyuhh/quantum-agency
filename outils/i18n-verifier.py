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


def bloc_objet(s, nom):
    """Étendue d'un littéral d'objet, par comptage d'accolades.

    ⚠️ Chercher « \\n}; » coupait au premier objet rencontré : le fichier en
    contient DEUX — EN pour le corps de page, TITLES pour les <title>. Les
    9 titres manquants n'étaient pas absents, ils étaient hors du périmètre lu.
    """
    d = s.find(f'const {nom} = {{')
    if d < 0:
        return ''
    i = d + len(f'const {nom} = ')
    prof = 0
    for m in re.finditer(r'[{}]', s[i:]):
        prof += 1 if m.group() == '{' else -1
        if prof == 0:
            return s[i:i + m.end()]
    return ''


def cles_du_dictionnaire():
    s = (RACINE / 'i18n.js').read_text(encoding='utf-8')
    bloc = bloc_objet(s, 'EN') + '\n' + bloc_objet(s, 'TITLES')
    return {
        ex.desechappe(next(g for g in m.groups() if g is not None)).strip()
        for m in re.finditer(ex.MOTIF_CLE, bloc, re.M)
    }


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
