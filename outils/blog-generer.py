#!/usr/bin/env python3
"""
Génère les articles du blog : rédaction par l'atelier, mise en page ici.

MAILLAGE INTERNE — la raison d'être de ce fichier
Cent articles isolés ne valent pas mieux que dix. Ce qui fait la différence,
c'est le maillage : chaque article renvoie vers d'autres articles du même pôle,
vers un article d'un pôle voisin, et vers la page de service correspondante.

Les liens sont calculés ICI, pas demandés au modèle : un modèle invente des URL.
Il rédige le texte, on pose les liens.

REPRISE
Un article déjà écrit n'est pas réécrit. Relancer le script complète ce qui
manque — indispensable quand un palier gratuit refuse une requête.
"""

import html
import json
import pathlib
import re
import subprocess
import sys
import datetime

RACINE = pathlib.Path(__file__).resolve().parent.parent
AI = pathlib.Path.home() / 'Projects' / 'atelier-ia' / 'bin' / 'ai'
BLOG = RACINE / 'blog'
BASE = 'https://quantum-agency.fr/'

sys.path.insert(0, str(RACINE / 'outils'))
from blog_sujets_import import SUJETS, POLES, ANCRAGE  # noqa: E402


def voisins(i):
    """Trois articles du même pôle, un d'un pôle voisin. Le maillage doit être
    dense dans un pôle et lâche entre pôles : c'est ce qui donne au moteur une
    structure thématique lisible plutôt qu'un tas de liens."""
    slug, titre, pole = SUJETS[i][0], SUJETS[i][1], SUJETS[i][2]
    meme = [s for s in SUJETS if s[2] == pole and s[0] != slug]
    autre = [s for s in SUJETS if s[2] != pole]
    pris = [meme[(i + k) % len(meme)] for k in (1, 3, 5)]
    pris.append(autre[(i * 7) % len(autre)])
    return pris


CONSIGNE = """Tu rédiges un article de blog pour un cabinet français de conseil et de formation en intelligence artificielle. Le lecteur est un dirigeant de PME ou d'ETI française, non technicien, pressé, méfiant vis-à-vis des promesses.

TITRE : {titre}
PROBLÉMATIQUE : {question}
CE QUE L'ARTICLE DOIT APPORTER : {angle}

RÈGLES D'ÉCRITURE
- Français, vouvoiement, registre professionnel et sobre. Pas de superlatifs, pas d'enthousiasme de brochure.
- LONGUEUR IMPÉRATIVE : entre 900 et 1200 mots. Un article de 500 mots est refusé.
- ⛔ INTERDIT d'ouvrir par « En tant que dirigeant… », « À l'ère du numérique… »,
  « L'intelligence artificielle est devenue… » ou toute formule qui explique au
  lecteur ce qu'il sait déjà. Commence par une SITUATION précise : un moment, un
  document, un chiffre observé, une phrase entendue en réunion.
- Ne définis jamais l'IA. Le lecteur sait ce que c'est ; il ne sait pas quoi en faire.
- Sois spécifique : des situations, des ordres de grandeur, des contre-exemples. Si tu avances un chiffre, présente-le comme un ordre de grandeur, jamais comme une mesure.
- Au moins une partie doit traiter un cas où la réponse est « ne le faites pas », avec la raison.
- Nomme des outils réels quand c'est pertinent (n8n, Make, Claude, GPT-4o, Mistral, Excel, un CRM) plutôt que « une solution d'IA ».
- Dis aussi ce qui NE marche pas, et dans quels cas la réponse est « n'y allez pas ».
- Aucune promesse de résultat chiffré.
- Pas de conclusion qui résume ce qui vient d'être dit ; termine sur la prochaine action concrète.

FORMAT DE SORTIE — strictement du HTML, sans <html>, <head> ni <body>.
L'article doit contenir TROIS blocs, dans cet ordre :

1. LA RÉPONSE COURTE, en tout premier :
   <p class="art-reponse"><strong>En bref.</strong> …</p>
   Deux à quatre phrases qui répondent DIRECTEMENT à la problématique, sans
   renvoyer à la suite. Un lecteur pressé doit repartir avec la réponse. Écris-la
   comme si elle devait être citée seule, hors de son contexte.

2. LE CORPS :
   - 4 à 6 <h2>, des <h3> si nécessaire
   - des <p>, des <ul><li>, et un <table> si une comparaison le justifie
   - aucun <a>, aucun <h1> : liens et titre sont posés par le gabarit

3. LA FAQ, en dernier, exactement dans cette forme :
   <section class="art-faq">
     <h2>Questions fréquentes</h2>
     <div class="faq-q"><h3>Question ?</h3><p>Réponse en 2 à 4 phrases.</p></div>
     … 3 à 5 questions au total
   </section>
   Des questions RÉELLEMENT différentes de ce que traitent les <h2>, formulées
   comme on les taperait dans un moteur de recherche. Chaque réponse doit se
   suffire à elle-même.

Pas de bloc markdown autour, pas de commentaire, uniquement le HTML de l'article.
"""


def rediger(sujet, tentatives=3):
    """Réessaie : un modèle rend parfois une ébauche de 200 mots sans raison,
    et la tentative suivante donne 1 300 mots sur la même consigne."""
    dernier = ''
    for n in range(tentatives):
        t, err = _rediger_une(sujet)
        if t is not None:
            return t, None
        dernier = err
    return None, dernier


def _rediger_une(sujet):
    slug, titre, pole, question, angle = sujet
    r = subprocess.run(
        [str(AI), '--role', 'article',
         CONSIGNE.format(titre=titre, question=question, angle=angle)],
        capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        return None, (r.stderr or '').strip()[-160:]
    t = r.stdout.strip()

    # ⚠️ LE PIÈGE QUI A PUBLIÉ DU RAISONNEMENT DANS 5 ARTICLES
    # L'ancien nettoyage n'enlevait un bloc de code qu'en DÉBUT et en FIN de
    # sortie. Quand le modèle réfléchit à voix haute puis ouvre ```html, le bloc
    # est au milieu : rien n'était retiré, et « Let's draft », « We must ensure
    # no <a> tags » se retrouvaient dans le corps de l'article publié.
    # On garde donc le CONTENU du bloc où qu'il soit, et on ne se contente plus
    # de rogner les extrémités.
    bloc = re.search(r'```(?:html)?\s*(.+?)\s*```', t, re.S)
    if bloc:
        t = bloc.group(1)
    t = re.sub(r'```[a-z]*', '', t)
    # Un modèle à raisonnement peut aussi rendre son <think> en clair.
    t = re.sub(r'<think>.*?</think>', '', t, flags=re.S | re.I)
    t = re.sub(r'</?(?:html|head|body|h1)[^>]*>', '', t)
    # ⚠️ Contrôle sur le nombre de MOTS, pas de caractères : le HTML gonfle le
    # compte et masquait des articles de 480 mots jugés « assez longs ».
    import re as _re
    mots = len(_re.findall(r'\w+', _re.sub(r'<[^>]+>', ' ', t)))
    faq = t.count('faq-q')
    # ⚠️ Traces de raisonnement laissées dans le texte. Le contrôle porte sur
    # l'ANGLAIS : l'article est en français, donc toute tournure de délibération
    # anglaise est forcément du résidu de modèle, jamais du contenu voulu.
    fuite = _re.search(
        r"(?i)\b(let's|we need to|we must|we'll|i'll write|let me draft|draft:|word count)\b", t)

    # Plafond autant que plancher. Le prompt demande 900 à 1200 mots ; au-delà
    # de 2000, ce n'est plus un article long, c'est autre chose qui a fuité —
    # les 5 articles pollués faisaient tous entre 4000 et 6100 mots.
    if (t.count('<h2') < 3 or mots < 750 or mots > 2000
            or 'art-reponse' not in t or faq < 3 or fuite):
        return None, (f'refusé : {mots} mots, {t.count("<h2")} parties, '
                      f'{faq} questions, réponse courte {"oui" if "art-reponse" in t else "NON"}'
                      + (f', RAISONNEMENT résiduel « {fuite.group(0)} »' if fuite else ''))
    return t, None


# ── Mots distinctifs ──────────────────────────────────────────────────────
# ⚠️ Une ancre comme « surtout », « compte » ou « projet » ne dit rien au moteur
# et déroute le lecteur. Plutôt qu'une liste noire à rallonge, on MESURE : un mot
# présent dans beaucoup de titres est générique, un mot rare est distinctif.
def _frequences():
    from collections import Counter
    c = Counter()
    for _, titre, _, _, _ in SUJETS:
        for m in set(re.findall(r"[\wÀ-ÿ']+", titre.lower())):
            c[m] += 1
    return c


_FREQ = _frequences()
_BANNIS = {'surtout', 'compte', 'projet', 'entreprise', 'quand', 'faut', 'avant',
           'comment', 'pourquoi', 'quel', 'quelle', 'votre', 'leur', 'cette',
           'toute', 'tout', 'plus', 'moins', 'entre', 'entreprises', 'peut',
           'dans', 'pour', 'avec', 'sans', 'celui', 'ceux', 'elle', 'elles',
           'faire', 'chose', 'sujet', 'point', 'cas'}


def poser_liens(corps, sujet, i):
    """Insère les liens internes DANS le corps, là où le texte s'y prête.

    Deux règles issues de l'expérience :
      · plusieurs ancres candidates par cible, sinon on ne place que 0 à 3 liens
        par article là où le maillage en demande 4 à 6 ;
      · l'ancre doit être DISTINCTIVE — mesurée sur la fréquence du mot dans
        l'ensemble des titres, pas devinée.

    On ne remplace qu'une occurrence par cible, jamais dans une balise, dans un
    lien existant, ni dans un titre.
    """
    def ancres(titre):
        mots = [m for m in re.findall(r"[\wÀ-ÿ']+", titre.lower())
                if len(m) > 4 and m not in _BANNIS and _FREQ.get(m, 0) <= 16]
        out = [a + r'\s+' + b for a, b in zip(mots, mots[1:])]   # paires d'abord
        out += [m for m in mots if len(m) > 5]                    # puis mots longs
        return out

    cibles = [(v[1], f'/blog/{v[0]}.html') for v in voisins(i)]
    cibles.append((POLES[sujet[2]], '/' + ANCRAGE[sujet[2]]))

    segments = re.split(r'(<[^>]+>)', corps)
    poses = 0
    for titre, url in cibles:
        place = False
        for motif_txt in ancres(titre):
            if place:
                break
            motif = re.compile(r'\b(' + motif_txt + r')\b', re.I)
            for k, seg in enumerate(segments):
                if seg.startswith('<') or '</a>' in seg or len(seg) < 40:
                    continue
                if k > 0 and re.match(r'<h[1-4]', segments[k - 1] or ''):
                    continue
                if motif.search(seg):
                    segments[k] = motif.sub(
                        lambda m: f'<a href="{url}">{m.group(1)}</a>', seg, count=1)
                    poses += 1
                    place = True
                    break
    return ''.join(segments), poses


def bloc_lire_aussi(i):
    li = '\n'.join(
        f'      <li><a href="/blog/{v[0]}.html">{html.escape(v[1])}</a></li>'
        for v in voisins(i))
    return f'''  <aside class="lire-aussi" aria-labelledby="lire-aussi-t">
    <h2 id="lire-aussi-t">À lire aussi</h2>
    <ul>
{li}
    </ul>
  </aside>'''


if __name__ == '__main__':
    print('  Ce fichier est appelé par blog-construire.py')
