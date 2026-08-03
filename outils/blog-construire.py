#!/usr/bin/env python3
"""
Construit les pages d'articles à partir du gabarit existant.

POURQUOI ON REPART D'UN ARTICLE EXISTANT
Le blog a déjà cinq articles, avec leur navigation, leur fil d'Ariane, leurs
données structurées Article + BreadcrumbList et leur mise en page. Réécrire un
gabarit produirait deux styles sur le même site. On prend celui qui existe et on
n'y remplace que le contenu.

    python3 outils/blog-construire.py            # tout ce qui manque
    python3 outils/blog-construire.py 5          # cinq articles seulement
    python3 outils/blog-construire.py --index    # régénère seulement blog.html
"""

import html
import importlib.util
import json
import pathlib
import re
import sys
import datetime

RACINE = pathlib.Path(__file__).resolve().parent.parent
BLOG = RACINE / 'blog'
GABARIT = BLOG / 'audit-ia-guide.html'
BASE = 'https://quantum-agency.fr/'

spec = importlib.util.spec_from_file_location('g', RACINE / 'outils' / 'blog-generer.py')
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
SUJETS, POLES, ANCRAGE = G.SUJETS, G.POLES, G.ANCRAGE

MOIS = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet',
        'août', 'septembre', 'octobre', 'novembre', 'décembre']


def remplacer_entre(s, deb, fin, neuf):
    """Remplace ce qui se trouve entre deux repères, bornes comprises.

    ⚠️ On échoue bruyamment si un repère manque. Un find() qui renvoie -1 est un
    index valide en Python : sans cette garde, on réinjecterait le début du
    fichier — vécu, et le symptôme est une page en double sans aucune erreur."""
    i = s.find(deb)
    assert i >= 0, f'repère absent : {deb[:40]}'
    j = s.find(fin, i + len(deb))
    assert j >= 0, f'repère de fin absent : {fin[:40]}'
    return s[:i] + neuf + s[j + len(fin):]


def duree(corps):
    mots = len(re.findall(r'\w+', re.sub(r'<[^>]+>', ' ', corps)))
    return max(4, round(mots / 220))


def construire(sujet, i, corps):
    slug, titre, pole, question, angle = sujet
    gab = GABARIT.read_text(encoding='utf-8')
    d = datetime.date.today()
    date_lisible = f'{MOIS[d.month - 1].capitalize()} {d.year}'
    url = f'{BASE}blog/{slug}.html'
    desc = (question + ' ' + angle)[:155].rsplit(' ', 1)[0] + '…'

    s = gab
    s = re.sub(r'<title>.*?</title>',
               f'<title>{html.escape(titre)} | Quantum Consulting</title>', s, flags=re.S)
    s = re.sub(r'(<meta name="description" content=)"[^"]*"',
               rf'\1"{html.escape(desc, quote=True)}"', s)
    s = re.sub(r'(<link rel="canonical" href=)"[^"]*"', rf'\1"{url}"', s)
    for prop in ('og:url',):
        s = re.sub(rf'(<meta property="{prop}" content=)"[^"]*"', rf'\1"{url}"', s)
    for prop in ('og:title', 'twitter:title'):
        s = re.sub(rf'(<meta (?:property|name)="{prop}" content=)"[^"]*"',
                   rf'\1"{html.escape(titre, quote=True)} | Quantum Consulting"', s)
    for prop in ('og:description', 'twitter:description'):
        s = re.sub(rf'(<meta (?:property|name)="{prop}" content=)"[^"]*"',
                   rf'\1"{html.escape(desc, quote=True)}"', s)

    # ── Données structurées ────────────────────────────────────────────────
    art = {
        '@context': 'https://schema.org', '@type': 'BlogPosting',
        'headline': titre, 'description': desc, 'url': url,
        'mainEntityOfPage': {'@type': 'WebPage', '@id': url},
        'inLanguage': 'fr', 'datePublished': d.isoformat(), 'dateModified': d.isoformat(),
        'author': {'@type': 'Organization', 'name': 'Quantum Consulting', 'url': BASE},
        'publisher': {'@type': 'Organization', 'name': 'Quantum Consulting', 'url': BASE},
        'articleSection': POLES[pole],
        'about': {'@type': 'Thing', 'name': POLES[pole]},
    }
    fil = {
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Accueil', 'item': BASE},
            {'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': BASE + 'blog.html'},
            {'@type': 'ListItem', 'position': 3, 'name': titre, 'item': url},
        ],
    }
    # ⚠️ FAQPage extrait du corps réel, jamais réécrit à la main : une donnée
    # structurée qui ne correspond pas au texte visible est une pénalité, pas un
    # bonus. Google la compare à la page.
    qr = []
    for m in re.finditer(r'<div class="faq-q">\s*<h3[^>]*>(.*?)</h3>\s*<p>(.*?)</p>',
                         corps, re.S):
        q = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        r_ = re.sub(r'<[^>]+>', '', m.group(2)).strip()
        if q and r_:
            qr.append({'@type': 'Question', 'name': q,
                       'acceptedAnswer': {'@type': 'Answer', 'text': r_}})
    structures = [art, fil]
    if len(qr) >= 3:
        structures.append({'@context': 'https://schema.org', '@type': 'FAQPage',
                           'mainEntity': qr})

    blocs = ''.join(
        '<script type="application/ld+json">' + json.dumps(x, ensure_ascii=False,
                                                           separators=(',', ':')) + '</script>\n'
        for x in structures)
    s = re.sub(r'(<script type="application/ld\+json">.*?</script>\s*)+', blocs, s,
               count=1, flags=re.S)

    # ── Corps ──────────────────────────────────────────────────────────────
    corps_lie, n_liens = G.poser_liens(corps, sujet, i)
    contenu = (f'  <nav class="breadcrumb" aria-label="Fil d\'Ariane">\n'
               f'    <a href="/index.html">Accueil</a><span>›</span>'
               f'<a href="/blog.html">Blog</a><span>›</span>'
               f'<span aria-current="page">{html.escape(titre[:48])}</span>\n  </nav>\n'
               f'  <div class="art-cat">{POLES[pole]}</div>\n'
               f'  <h1>{html.escape(titre)}</h1>\n'
               f'  <div class="art-meta">\n    <span>Quantum Consulting</span>\n'
               f'    <span>{date_lisible}</span>\n'
               f'    <span>{duree(corps)} min de lecture</span>\n  </div>\n'
               f'  <div class="art-body">\n{corps_lie}\n  </div>\n'
               f'{G.bloc_lire_aussi(i)}\n')
    s = remplacer_entre(s, '<article class="art-wrap">', '</article>',
                        '<article class="art-wrap">\n' + contenu + '</article>')

    style = '''<style>
.art-reponse{border-left:3px solid #a855f7;background:rgba(168,85,247,.07);
  padding:1rem 1.2rem;border-radius:0 12px 12px 0;margin:0 0 2rem;font-size:1.02rem}
.art-faq{margin-top:3rem;border-top:1px solid rgba(255,255,255,.09);padding-top:2rem}
.art-faq .faq-q{margin-bottom:1.4rem}
.art-faq .faq-q h3{font-size:1.02rem;font-weight:700;margin:0 0 .4rem;color:#e2e8f0}
.art-faq .faq-q p{margin:0;color:#94a3b8}
.lire-aussi{margin-top:3rem;border-top:1px solid rgba(255,255,255,.09);padding-top:2rem}
.lire-aussi ul{list-style:none;padding:0;display:grid;gap:.6rem}
.lire-aussi a{color:#a855f7;text-decoration:none;font-weight:600}
.lire-aussi a:hover{text-decoration:underline}
</style>'''
    if '.art-reponse{' not in s:
        s = s.replace('</head>', style + '\n</head>', 1)

    # Les liens relatifs du gabarit deviennent absolus : /blog/ est un
    # sous-dossier, « ../contact.html » se casse dès qu'on descend d'un cran.
    s = re.sub(r'(href|src)="\.\./', r'\1="/', s)
    return s, n_liens


def index_blog(existants):
    """Régénère blog.html : toutes les cartes, groupées par pôle."""
    p = RACINE / 'blog.html'
    s = p.read_text(encoding='utf-8')
    par_pole = {}
    for i, sj in enumerate(SUJETS):
        if sj[0] in existants:
            par_pole.setdefault(sj[2], []).append(sj)
    blocs = []
    for cle, nom in POLES.items():
        lot = par_pole.get(cle, [])
        if not lot:
            continue
        cartes = '\n'.join(
            f'      <a class="bl-card" data-pole="{sj[2]}" href="/blog/{sj[0]}.html">\n'
            f'        <span class="bl-cat">{nom}</span>\n'
            f'        <h3>{html.escape(sj[1])}</h3>\n'
            f'        <p>{html.escape(sj[3])}</p>\n'
            f'        <span class="bl-lien">Lire l\'article →</span>\n'
            f'      </a>' for sj in lot)
        blocs.append(f'  <section class="bl-pole" id="pole-{cle}">\n'
                     f'    <h2>{nom}</h2>\n    <div class="bl-grid">\n{cartes}\n'
                     f'    </div>\n  </section>')
    # ── Filtres ───────────────────────────────────────────────────────────
    # ⚠️ Les cartes restent TOUTES dans le HTML : le filtre masque, il ne
    # supprime pas. Un moteur qui n'exécute pas le script doit voir les 100
    # articles, et un visiteur sans JavaScript aussi.
    nb = {}
    for sj in SUJETS:
        if sj[0] in existants:
            nb[sj[2]] = nb.get(sj[2], 0) + 1
    onglets = ''.join(
        f'<button type="button" class="bl-f" data-f="{cle}">{nom} '
        f'<span class="bl-n">{nb[cle]}</span></button>'
        for cle, nom in POLES.items() if nb.get(cle))
    filtre = ('  <nav class="bl-filtres" aria-label="Filtrer par thème">\n'
              f'    <button type="button" class="bl-f actif" data-f="tous">Tous '
              f'<span class="bl-n">{len(existants)}</span></button>{onglets}\n'
              '  </nav>\n')
    corps = filtre + '\n'.join(blocs)
    style = '''<style>
.bl-pole{max-width:1180px;margin:0 auto;padding:3.5rem 5% 0}
.bl-pole h2{font-size:1.5rem;font-weight:800;letter-spacing:-.02em;margin:0 0 1.4rem}
.bl-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1.2rem}
.bl-card{display:flex;flex-direction:column;gap:.5rem;padding:1.4rem;border-radius:16px;
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);
  text-decoration:none;color:inherit;transition:border-color .2s,transform .2s}
.bl-card:hover{border-color:rgba(168,85,247,.45);transform:translateY(-2px)}
.bl-cat{font-size:.62rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#a855f7}
.bl-card h3{font-size:1.02rem;font-weight:700;line-height:1.35;margin:0}
.bl-card p{font-size:.85rem;color:#94a3b8;margin:0;flex:1}
.bl-lien{font-size:.8rem;font-weight:700;color:#a855f7}
/* Sous 640 px, une seule colonne : deux colonnes de 300 px ne tiennent pas. */
@media(max-width:640px){.bl-pole{padding:2.5rem 6% 0}.bl-grid{grid-template-columns:1fr}}
.bl-filtres{max-width:1180px;margin:0 auto;padding:1.5rem 5% 0;display:flex;flex-wrap:wrap;gap:.5rem}
.bl-f{display:inline-flex;align-items:center;gap:.4rem;padding:.6rem 1rem;min-height:44px;
  border-radius:100px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.03);
  color:#cbd5e1;font:600 .8rem Inter,system-ui,sans-serif;cursor:pointer;
  transition:border-color .2s,color .2s,background .2s}
.bl-f:hover{color:#fff;border-color:rgba(168,85,247,.4)}
.bl-f.actif{color:#fff;background:rgba(124,58,237,.18);border-color:rgba(168,85,247,.55)}
.bl-n{font-size:.7rem;opacity:.6}
.bl-pole[hidden]{display:none}
@media(max-width:640px){.bl-filtres{padding:1.2rem 6% 0;overflow-x:auto;flex-wrap:nowrap;
  scrollbar-width:none}.bl-filtres::-webkit-scrollbar{display:none}.bl-f{white-space:nowrap}}
</style>
<script>
/* Filtre par thème. Les cartes ne sont jamais retirées du DOM : masquer garde
   les 100 articles visibles pour un moteur et pour qui n'a pas de JavaScript. */
document.addEventListener('DOMContentLoaded', function () {
  var boutons = [].slice.call(document.querySelectorAll('.bl-f'));
  var poles = [].slice.call(document.querySelectorAll('.bl-pole'));
  if (!boutons.length) return;
  function appliquer(cle) {
    poles.forEach(function (p) {
      p.hidden = cle !== 'tous' && p.id !== 'pole-' + cle;
    });
    boutons.forEach(function (b) {
      var on = b.dataset.f === cle;
      b.classList.toggle('actif', on);
      b.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    /* L'URL porte le filtre : un thème se partage et se met en favori. */
    history.replaceState(null, '', cle === 'tous' ? location.pathname : '#' + cle);
  }
  boutons.forEach(function (b) {
    b.addEventListener('click', function () { appliquer(b.dataset.f); });
  });
  var depart = location.hash.slice(1);
  if (depart && document.getElementById('pole-' + depart)) appliquer(depart);
});
</script>'''
    i = s.find('<main')
    j = s.find('</main>')
    assert i > 0 and j > i, 'blog.html : <main> introuvable'
    tete = s[:i]

    DEB, FIN = '<!-- blog:style -->', '<!-- /blog:style -->'
    a, b = tete.find(DEB), tete.find(FIN)
    if a >= 0 and b > a:
        tete = tete[:a] + DEB + '\n' + style + '\n' + tete[b:]
    else:
        tete = tete.replace('</head>', DEB + '\n' + style + '\n' + FIN + '\n</head>', 1)
    entete = ('<main id="main-content">\n'
              '  <header class="pg-hero">\n'
              '    <div class="pg-tag">Le blog</div>\n'
              f'    <h1>{len(existants)} articles pour décider en connaissance de cause</h1>\n'
              '    <p class="pg-sub">Une problématique par article. Ce qui marche, ce qui ne marche '
              'pas, et à quelles conditions.</p>\n  </header>\n')
    p.write_text(tete + entete + corps + '\n' + s[j:], encoding='utf-8')
    return len(existants)


if __name__ == '__main__':
    BLOG.mkdir(exist_ok=True)
    args = sys.argv[1:]
    if '--index' in args:
        n = index_blog({s[0] for s in SUJETS if (BLOG / f'{s[0]}.html').exists()})
        print(f'  blog.html régénéré · {n} articles')
        sys.exit(0)
    limite = int(args[0]) if args and args[0].isdigit() else len(SUJETS)

    faits = ecrits = 0
    for i, sj in enumerate(SUJETS):
        cible = BLOG / f'{sj[0]}.html'
        if cible.exists():
            faits += 1
            continue
        if ecrits >= limite:
            continue
        corps, err = G.rediger(sj)
        if corps is None:
            print(f'  ✗ {sj[0]:44} {err}')
            continue
        page, nl = construire(sj, i, corps)
        cible.write_text(page, encoding='utf-8')
        ecrits += 1
        print(f'  ✓ {sj[0]:44} {len(page)//1024:>3} Ko · {nl} liens internes')

    total = sum(1 for s in SUJETS if (BLOG / f'{s[0]}.html').exists())
    print(f'\n  {ecrits} écrits · {total}/{len(SUJETS)} au total')
    if total:
        index_blog({s[0] for s in SUJETS if (BLOG / f'{s[0]}.html').exists()})
        print('  blog.html régénéré')


# ═══════════════════════════════════════════════════════════════════════════
#  Mise en lecture — appliqué APRÈS écriture, sur les articles existants
# ═══════════════════════════════════════════════════════════════════════════

STYLE_LECTURE = '''<style>
/* Barre de progression : augmente le taux d'achèvement, réduit le rebond. */
.art-progres{position:fixed;top:0;left:0;height:3px;width:100%;transform:scaleX(0);
  transform-origin:left center;z-index:900;pointer-events:none;
  background:linear-gradient(90deg,#7c3aed,#a855f7,#06b6d4)}
/* Sommaire : le lecteur sait où il est et peut sauter. Utile dès 4 sections. */
.art-sommaire{margin:0 0 2.4rem;padding:1.1rem 1.3rem;border-radius:14px;
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08)}
.art-sommaire-t{margin:0 0 .6rem;font-size:.66rem;font-weight:800;letter-spacing:.14em;
  text-transform:uppercase;color:#a855f7}
.art-sommaire ol{margin:0;padding-left:1.1rem;display:grid;gap:.35rem}
.art-sommaire a{color:#cbd5e1;text-decoration:none;font-size:.9rem;line-height:1.45}
.art-sommaire a:hover{color:#fff}
.art-sommaire a[aria-current]{color:#a855f7;font-weight:700}
/* ⚠️ Paragraphes courts : 73 % des visiteurs partent en moins de dix secondes
   si la page est difficile à lire, et 79 % balaient au lieu de lire. */
.art-body p{margin:0 0 1.15rem;max-width:68ch}
.art-body h2{margin:2.6rem 0 .9rem;font-size:1.42rem;font-weight:800;letter-spacing:-.02em;
  scroll-margin-top:96px}
.art-body h3{margin:1.8rem 0 .6rem;font-size:1.08rem;font-weight:700}
.art-body ul,.art-body ol{margin:0 0 1.3rem;padding-left:1.3rem;display:grid;gap:.45rem}
.art-body table{width:100%;border-collapse:collapse;margin:0 0 1.5rem;font-size:.9rem;
  display:block;overflow-x:auto}
.art-body th,.art-body td{padding:.6rem .8rem;border-bottom:1px solid rgba(255,255,255,.09);
  text-align:left}
.art-body th{font-weight:700;color:#e2e8f0}
/* Navigation d'article : prolonge la session au lieu de la clore. */
.art-nav{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:2.5rem;
  border-top:1px solid rgba(255,255,255,.09);padding-top:1.6rem}
.art-nav a{display:flex;flex-direction:column;gap:.3rem;padding:1rem 1.1rem;border-radius:14px;
  background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);
  text-decoration:none;color:inherit;transition:border-color .2s}
.art-nav a:hover{border-color:rgba(168,85,247,.45)}
.art-nav .sens{font-size:.66rem;font-weight:800;letter-spacing:.13em;text-transform:uppercase;
  color:#a855f7}
.art-nav .titre{font-size:.94rem;font-weight:700;line-height:1.35}
.art-nav .suivant{text-align:right}
@media(max-width:640px){
  .art-nav{grid-template-columns:1fr}
  .art-nav .suivant{text-align:left}
  .art-body p{font-size:1rem}
}
</style>'''


def nav_precedent_suivant(i):
    """Article précédent et suivant DANS LE MÊME PÔLE.

    ⚠️ Enchaîner sur l'ordre du catalogue ferait passer de « Conformité » à
    « Par métier » sans transition. Le lecteur qui finit un article sur le RGPD
    veut le suivant sur le RGPD, pas un saut thématique."""
    pole = SUJETS[i][2]
    memes = [k for k, s in enumerate(SUJETS) if s[2] == pole]
    pos = memes.index(i)
    prec = memes[pos - 1] if pos > 0 else memes[-1]
    suiv = memes[(pos + 1) % len(memes)]
    if prec == i or suiv == i:
        return ''
    p, s_ = SUJETS[prec], SUJETS[suiv]
    return f'''  <nav class="art-nav" aria-label="Navigation entre articles">
    <a class="precedent" href="/blog/{p[0]}.html" rel="prev">
      <span class="sens">← Précédent</span>
      <span class="titre">{html.escape(p[1])}</span>
    </a>
    <a class="suivant" href="/blog/{s_[0]}.html" rel="next">
      <span class="sens">Suivant →</span>
      <span class="titre">{html.escape(s_[1])}</span>
    </a>
  </nav>'''
