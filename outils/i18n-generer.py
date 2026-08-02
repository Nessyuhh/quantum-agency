#!/usr/bin/env python3
"""
Reconstruit le dictionnaire de i18n.js, sans toucher à sa logique.

CE QUI EST PRÉSERVÉ
Tout le fichier sauf le littéral `const EN = { … }`. La mécanique — parcours des
nœuds de texte, bascule, mémorisation du choix — reste celle qui fonctionne
déjà. On ne remplace que les données.

⚠️ Les bornes du dictionnaire sont trouvées en COMPTANT LES ACCOLADES, pas en
cherchant « \\n}; » : les valeurs traduites contiennent des accolades et des
sauts de ligne, et un repère textuel coupait au mauvais endroit.

SOURCES, dans l'ordre de priorité
  1. les traductions existantes du fichier (travail humain déjà validé)
  2. outils/i18n-traductions.json (produit par i18n-traduire.py)
Une traduction existante n'est jamais écrasée.
"""

import html as _html
import json
import pathlib
import re

RACINE = pathlib.Path(__file__).resolve().parent.parent
CIBLE = RACINE / 'i18n.js'
NOUVELLES = RACINE / 'outils' / 'i18n-traductions.json'


EXCLUES = {
    'quantum-logos.html', 'quantum-logos-final.html', 'email-signature.html',
    'business-card.html', 'intro-preview.html', 'animation-atom.html',
    'quantum-logo-animation.html', 'sonde.html',
}


def bornes_de(s, nom):
    d = s.find(f'const {nom} = {{')
    assert d > 0, f'{nom} introuvable'
    i = d + len(f'const {nom} = ')
    prof = 0
    for m in re.finditer(r'[{}]', s[i:]):
        prof += 1 if m.group() == '{' else -1
        if prof == 0:
            return d, i + m.end()
    raise LookupError(nom)


def bornes(s):
    d = s.find('const EN = {')
    assert d > 0, 'dictionnaire introuvable'
    i = d + len('const EN = ')
    prof = 0
    for m in re.finditer(r'[{}]', s[i:]):
        prof += 1 if m.group() == '{' else -1
        if prof == 0:
            return d, i + m.end()
    raise LookupError('accolade de fermeture introuvable')


def existantes(bloc):
    """Paires déjà présentes. On lit clé et valeur, quel que soit le guillemet."""
    out = {}
    motif = re.compile(
        r"^\s*(?:\"((?:[^\"\\]|\\.)*)\"|'((?:[^'\\]|\\.)*)'|`([^`]*)`)\s*:\s*"
        r"(?:\"((?:[^\"\\]|\\.)*)\"|'((?:[^'\\]|\\.)*)'|`([^`]*)`)\s*,?\s*$", re.M)
    for m in motif.finditer(bloc):
        cle = next(g for g in m.groups()[:3] if g is not None)
        val = next(g for g in m.groups()[3:] if g is not None)
        out[cle.replace("\\'", "'").replace('\\"', '"')] = val.replace("\\'", "'").replace('\\"', '"')
    return out


def js(s):
    """Littéral JavaScript entre apostrophes, échappé."""
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ') + "'"


def main():
    src = CIBLE.read_text(encoding='utf-8')
    d, f = bornes(src)
    anciennes = existantes(src[d:f])

    ajouts = json.loads(NOUVELLES.read_text(encoding='utf-8')) if NOUVELLES.exists() else {}
    fusion = dict(ajouts)
    fusion.update(anciennes)          # l'existant l'emporte

    lignes = [f'  {js(k)}: {js(v)},' for k, v in sorted(fusion.items())]
    bloc = ('const EN = {\n'
            '  // Généré par outils/i18n-generer.py — ne pas éditer à la main.\n'
            '  // Pour ajouter : modifier les textes, puis relancer\n'
            '  //   i18n-extraire.py · i18n-traduire.py · i18n-generer.py\n'
            '  // Vérifier avec : i18n-verifier.py\n'
            + '\n'.join(lignes) + '\n}')

    src = src[:d] + bloc + src[f:]

    # ── TITLES ────────────────────────────────────────────────────────────
    # ⚠️ document.title n'est PAS traduit par EN : le script applique une table
    # séparée. Sept titres de page y manquaient alors qu'ils étaient traduits
    # dans EN — la couverture paraissait totale et l'onglet restait en français.
    # On la remplit depuis les <title> réels et les traductions de EN.
    import glob
    reels = {}
    for f_ in sorted(glob.glob(str(RACINE / '*.html'))):
        nom = pathlib.Path(f_).name
        if nom in EXCLUES:
            continue
        m = re.search(r'<title>(.*?)</title>', pathlib.Path(f_).read_text(encoding='utf-8'), re.S)
        if m:
            # ⚠️ Déséchapper : le HTML porte « &amp; » mais document.title rend
            # « & ». Une clé échappée ne correspondrait jamais à l'exécution.
            reels[_html.unescape(re.sub(r'\s+', ' ', m.group(1))).strip()] = nom

    dt, ft = bornes_de(src, 'TITLES')
    titres = existantes(src[dt:ft])
    ajoutes = 0
    for t in reels:
        if t in titres:
            continue
        trad = fusion.get(t)
        if trad:
            titres[t] = trad
            ajoutes += 1
    lignes_t = [f'    {js(k)}: {js(v)},' for k, v in sorted(titres.items())]
    bloc_t = 'const TITLES = {\n' + '\n'.join(lignes_t) + '\n  }'
    src = src[:dt] + bloc_t + src[ft:]
    print(f'  TITLES : {len(titres)} entrées ({ajoutes} ajoutées)')

    CIBLE.write_text(src, encoding='utf-8')
    print(f'  {len(anciennes)} entrées conservées · {len(fusion)-len(anciennes)} ajoutées')
    print(f'  dictionnaire : {len(fusion)} entrées · i18n.js {CIBLE.stat().st_size//1024} Ko')


if __name__ == '__main__':
    main()
