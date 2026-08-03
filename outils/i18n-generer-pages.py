#!/usr/bin/env python3
"""
Génère les pages anglaises dans /en/, à partir des pages françaises.

POURQUOI CE FICHIER EXISTE
La traduction était entièrement côté navigateur : `quantum-agency.fr/` servait la
même URL en français et en anglais. Google n'indexait donc QUE le français —
1 721 traductions invisibles au référencement.

Une page anglaise doit avoir sa propre URL, son propre <title>, et être reliée à
sa jumelle française par hreflang. C'est la seule façon d'exister à
l'international.

EFFET DE BORD BÉNÉFIQUE
Les pages n'ont plus besoin de charger i18n.js et son dictionnaire de 229 Ko :
la traduction est faite une fois, ici, au lieu d'être refaite dans chaque
navigateur. Un sélecteur de 1 Ko suffit, qui pointe vers l'autre URL.

⚠️ La traduction ne touche QUE le texte. On ne traduit jamais :
   · le contenu des balises script, style, noscript
   · les valeurs d'attribut techniques (class, id, href, src…)
   · une chaîne absente du dictionnaire — elle reste en français et le
     vérificateur la signalera
"""

import html
import pathlib
import re
import shutil
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
SORTIE = RACINE / 'en'
BASE = 'https://quantum-agency.fr/'

EXCLUES = {
    'quantum-logos.html', 'quantum-logos-final.html', 'email-signature.html',
    'business-card.html', 'intro-preview.html', 'animation-atom.html',
    'quantum-logo-animation.html', 'sonde.html', '404.html',
}

MOTIF_CLE = r"""^[ \t]*(?:"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)'|`([^`]*)`)[ \t]*:[ \t]*"""
MOTIF_PAIRE = re.compile(
    MOTIF_CLE + r"""(?:"((?:[^"\\]|\\.)*)"|'((?:[^'\\]|\\.)*)'|`([^`]*)`)""", re.M)


def desechappe(s):
    return s.replace("\\'", "'").replace('\\"', '"').replace('\\\\', '\\')


def bloc_objet(s, nom):
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


def dictionnaires():
    """Source unique : outils/i18n-traductions.json.

    ⚠️ i18n.js n'existe plus. Il portait le dictionnaire ET le traduisait dans
    le navigateur — 232 Ko téléchargés à chaque visite pour refaire un travail
    qui se fait une fois, ici. Les pages anglaises sont maintenant statiques.
    """
    import json
    f = RACINE / 'outils' / 'i18n-traductions.json'
    return {k.strip(): v.strip() for k, v in
            json.loads(f.read_text(encoding='utf-8')).items()}


NORM = re.compile(r'\s+')
IGNORE = ('script', 'style', 'noscript')


def traduire_html(src, dico, manquantes):
    """Remplace le texte des nœuds et des attributs traduisibles."""
    zones = []
    for t in IGNORE:
        for m in re.finditer(rf'<{t}\b[^>]*>.*?</{t}>', src, re.S | re.I):
            zones.append((m.start(), m.end()))

    def protege(i):
        return any(a <= i < b for a, b in zones)

    # ── Texte entre balises ────────────────────────────────────────────────
    out, pos = [], 0
    for m in re.finditer(r'>([^<>]+)<', src):
        if protege(m.start()):
            continue
        brut = m.group(1)
        cle = NORM.sub(' ', html.unescape(brut)).strip()
        if len(cle) < 2 or not re.search(r'[a-zà-ÿ]', cle, re.I):
            continue
        trad = dico.get(cle)
        if trad is None:
            manquantes.add(cle)
            continue
        # On conserve les espaces de bordure d'origine : les retirer collerait
        # les mots aux balises voisines et changerait le rendu.
        gauche = brut[:len(brut) - len(brut.lstrip())]
        droite = brut[len(brut.rstrip()):]
        out.append(src[pos:m.start() + 1])
        out.append(gauche + html.escape(trad, quote=False) + droite)
        pos = m.end() - 1
    out.append(src[pos:])
    s = ''.join(out)

    # ── Attributs porteurs de texte ────────────────────────────────────────
    def rempl_attr(m):
        avant, val = m.group(1), m.group(2)
        cle = NORM.sub(' ', html.unescape(val)).strip()
        if len(cle) < 2 or not re.search(r'[a-zà-ÿ]', cle, re.I):
            return m.group(0)
        trad = dico.get(cle)
        if trad is None:
            manquantes.add(cle)
            return m.group(0)
        return f'{avant}"{html.escape(trad, quote=True)}"'

    s = re.sub(r'((?:placeholder|aria-label|alt|title)=)"([^"]*)"', rempl_attr, s)
    s = re.sub(r'((?:name|property)="(?:description|og:title|og:description|'
               r'twitter:title|twitter:description)"\s+content=)"([^"]*)"', rempl_attr, s)

    # ⚠️ Pas de traitement séparé du <title> : son contenu est déjà passé par
    # le remplacement des nœuds de texte plus haut. Le retraiter le cherchait
    # une seconde fois DÉJÀ TRADUIT, donc introuvable — d'où 20 fausses alertes.
    return s


def liens_alternes(nom):
    """hreflang croisé + x-default. Sans ces trois lignes, les deux versions se
    concurrencent au lieu de se compléter."""
    fr = BASE + ('' if nom == 'index.html' else nom)
    en = BASE + 'en/' + ('' if nom == 'index.html' else nom)
    return (f'<link rel="alternate" hreflang="fr" href="{fr}">\n'
            f'<link rel="alternate" hreflang="en" href="{en}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{fr}">\n')


def main():
    dico = dictionnaires()
    pages = sorted(p for p in RACINE.glob('*.html') if p.name not in EXCLUES)
    SORTIE.mkdir(exist_ok=True)
    manquantes = set()
    print(f'  dictionnaire : {len(dico)} entrées · {len(pages)} pages')

    for p in pages:
        src = p.read_text(encoding='utf-8')
        s = traduire_html(src, dico, manquantes)

        s = re.sub(r'<html([^>]*)\slang="fr"', r'<html\1 lang="en"', s)
        if 'lang="en"' not in s[:200]:
            s = re.sub(r'<html\b', '<html lang="en"', s, count=1)

        cible = BASE + 'en/' + ('' if p.name == 'index.html' else p.name)
        s = re.sub(r'<link rel="canonical"[^>]*>', f'<link rel="canonical" href="{cible}">', s)
        s = re.sub(r'(<meta property="og:url" content=)"[^"]*"', rf'\1"{cible}"', s)
        s = re.sub(r'(<meta property="og:locale" content=)"[^"]*"', r'\1"en_US"', s)

        s = re.sub(r'<link rel="alternate" hreflang[^>]*>\n?', '', s)
        s = s.replace('</head>', liens_alternes(p.name) + '</head>', 1)

        # Liens internes : rester dans /en/. Les chemins absolus vers les
        # ressources (/assets/, /favicon.svg) ne bougent pas.
        s = re.sub(r'href="/((?!en/)[a-z0-9-]+\.html)"', r'href="/en/\1"', s)
        s = re.sub(r'href="((?!https?:|/|#)[a-z0-9-]+\.html)"', r'href="\1"', s)

        # ⚠️ Ressources en chemin ABSOLU. Depuis /en/, un href="favicon.svg"
        # relatif cherche /en/favicon.svg et renvoie 404 — une erreur console
        # qui coûte des points de bonnes pratiques.
        s = re.sub(r'(href|src)="((?!https?:|/|#|data:)[\w.-]+\.(?:svg|png|ico|css|js|webp))"',
                   r'\1="/\2"', s)

        # i18n.js n'a plus lieu d'être : la page EST traduite.
        s = re.sub(r'\s*<script src="/?i18n\.js[^"]*"[^>]*></script>', '', s)
        s = s.replace('</body>', '<script src="/lang-switch.js" defer></script>\n</body>', 1)

        (SORTIE / p.name).write_text(s, encoding='utf-8')

    # Les pages françaises reçoivent les mêmes hreflang et le même sélecteur.
    for p in pages:
        s = p.read_text(encoding='utf-8')
        s = re.sub(r'<link rel="alternate" hreflang[^>]*>\n?', '', s)
        s = s.replace('</head>', liens_alternes(p.name) + '</head>', 1)
        s = re.sub(r'\s*<script src="/?i18n\.js[^"]*"[^>]*></script>', '', s)
        if 'lang-switch.js' not in s:
            s = s.replace('</body>', '<script src="/lang-switch.js" defer></script>\n</body>', 1)
        p.write_text(s, encoding='utf-8')

    print(f'  → {len(pages)} pages dans /en/')
    if manquantes:
        print(f'  ⚠️  {len(manquantes)} chaînes sans traduction, restées en français :')
        for x in sorted(manquantes)[:12]:
            print(f'      « {x[:70]} »')
    else:
        print('  ✓ aucune chaîne laissée en français')
    return 1 if manquantes else 0


if __name__ == '__main__':
    sys.exit(main())
