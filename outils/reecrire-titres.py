#!/usr/bin/env python3
"""Réécrit titre, métadescription et h1 d'articles, partout où ils figurent.

Un titre vit à six endroits dans une page : la balise title, le h1, les deux
déclarations de partage social, la description et le champ headline des données
structurées. En oublier un crée une incohérence que les moteurs remarquent.

Usage : python3 outils/reecrire-titres.py
"""
import html
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SUFFIXE = ' | Quantum Consulting'

# slug : (nouveau titre, nouvelle métadescription)
REECRITURES = {
    'fenetre-contexte-pourquoi-ca-compte': (
        "Traitement de gros documents par l'IA : les règles pour votre PME",
        "Comment l'IA lit vos rapports et contrats volumineux, ce qu'elle retient vraiment, et ce qui se perd quand le document est trop long."),
    'modeles-raisonnement-quand': (
        "Modèles d'IA à raisonnement : dans quels cas valent-ils leur coût en PME ?",
        "Quand un modèle qui raisonne étape par étape justifie sa dépense, et quand un modèle ordinaire suffit largement pour votre entreprise."),
    'multimodal-a-quoi-ca-sert': (
        "IA multimodale en entreprise : traiter images, enregistrements et documents",
        "Ce qu'apporte une IA capable de lire une image, un document scanné ou un enregistrement de réunion, avec des usages concrets en PME."),
    'cout-reel-api-llm': (
        "Coût de l'IA en PME : estimer et maîtriser ses factures d'utilisation",
        "Le prix affiché ne fait pas la facture. Les postes qui pèsent vraiment, et comment garder la dépense sous contrôle dans une PME."),
    'changer-de-modele-sans-tout-refaire': (
        "Changer de modèle d'IA sans bloquer les outils de l'entreprise",
        "Comment faire évoluer le modèle qui équipe vos automatisations sans tout réécrire, et comment éviter de dépendre d'un seul éditeur."),
    'claude-vs-gpt4o': (
        "Claude ou GPT-6 : quel modèle d'IA choisir pour votre PME ?",
        "Comparaison des deux familles de modèles selon vos usages réels : analyse de documents, rédaction, automatisation et budget."),
    'audit-ia-guide': (
        "Audit IA en PME : le guide complet pour cartographier vos opportunités",
        "Comment se déroule un audit IA, ce qu'il examine, ce qu'il produit, et comment lire ses conclusions avant d'engager le moindre budget."),
}


def remplacer(chemin, titre, description):
    p = RACINE / 'blog' / (chemin + '.html')
    s = p.read_text(encoding='utf-8')
    avant = s
    echappe = html.escape(titre, quote=True).replace("'", '&#x27;')

    s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % (echappe + SUFFIXE), s, count=1, flags=re.S)
    s = re.sub(r'<h1>.*?</h1>', '<h1>%s</h1>' % echappe, s, count=1, flags=re.S)
    for balise, attribut in (('meta property="og:title"', 'content'), ('meta name="twitter:title"', 'content')):
        s = re.sub(r'<%s %s="[^"]*"' % (balise, attribut),
                   '<%s %s="%s"' % (balise, attribut, echappe + SUFFIXE), s, count=1)
    for balise in ('meta name="description"', 'meta property="og:description"', 'meta name="twitter:description"'):
        s = re.sub(r'<%s content="[^"]*"' % balise,
                   '<%s content="%s"' % (balise, html.escape(description, quote=True)), s, count=1)
    # headline des données structurées : apostrophes réelles, pas d'entités
    s = re.sub(r'"headline":"[^"]*"', '"headline":%s' % json.dumps(titre, ensure_ascii=False), s, count=1)
    # dernier maillon du fil d'Ariane
    s = re.sub(r'(<span aria-current="page">)[^<]*(</span>)', r'\g<1>%s\g<2>' % echappe[:60], s, count=1)

    if s == avant:
        sys.exit('aucune modification dans %s' % chemin)
    p.write_text(s, encoding='utf-8')

    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        json.loads(m.group(1))
    return len(titre), len(description)


def main():
    for slug, (titre, description) in REECRITURES.items():
        lt, ld = remplacer(slug, titre, description)
        drapeau = ' TITRE LONG' if lt > 70 else ''
        drapeau += ' DESCRIPTION LONGUE' if ld > 155 else ''
        print('  %-38s titre %2d, description %3d%s' % (slug, lt, ld, drapeau))
    print('%d article(s) réécrit(s)' % len(REECRITURES))


if __name__ == '__main__':
    main()
