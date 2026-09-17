#!/usr/bin/env python3
"""Ajoute le bloc « En bref » et la section de questions aux articles qui en
manquent, avec les données structurées FAQPage correspondantes.

Cent articles sur cent cinq ont déjà ces deux blocs : les cinq restants font
tache, et ce sont eux que les moteurs génératifs citent le moins, faute d'une
réponse courte à extraire.

Usage : python3 outils/completer-articles.py
"""
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

ARTICLES = {
    'audit-ia-guide': {
        'bref': "Un audit IA examine votre façon de travailler pour repérer les tâches répétitives qui peuvent tourner seules. Il mesure le temps qu'elles vous coûtent, vérifie ce que vos données autorisent, et se conclut par des priorités écrites. Rien ne s'achète avant que ces priorités soient posées.",
        'faq': [
            ("Combien de temps prend un audit IA ?",
             "Notre audit gratuit tient en trente minutes d'échange, suivies d'une synthèse d'une page sous quarante-huit heures. Un audit approfondi, quand l'organisation est plus complexe, s'étale sur deux à quatre semaines et couvre l'ensemble des processus plutôt qu'un seul service."),
            ("Faut-il des compétences techniques en interne pour y participer ?",
             "Non. Nous parlons avec les personnes qui font le travail, de leur journée et de ce qui les ralentit. Aucune connaissance des outils n'est nécessaire, et c'est même préférable : nous cherchons à comprendre le métier, pas la technique."),
            ("Que contient la synthèse remise à la fin ?",
             "Les trois priorités retenues, ce que chacune ferait gagner en temps, ce qu'elle demande de votre côté, et l'ordre dans lequel les traiter. Vous restez libre de la mettre en œuvre vous-même, avec un autre prestataire, ou pas du tout."),
        ],
    },
    'automatisation-processus-rh': {
        'bref': "Automatiser les ressources humaines dans une PME consiste à faire circuler les candidatures, les pièces justificatives et les informations d'arrivée sans ressaisie. Les délais de réponse aux candidats se raccourcissent, les dossiers cessent de se perdre, et les décisions sur les personnes restent entièrement humaines.",
        'faq': [
            ("L'automatisation risque-t-elle de déshumaniser le recrutement ?",
             "Elle prend en charge l'administratif : accusés de réception, collecte de documents, transmission aux bons interlocuteurs. Le tri des candidatures et la décision d'embaucher restent à vos équipes, et nous écrivons noir sur blanc ce que la machine n'a pas le droit de trancher."),
            ("Comment protéger les données des candidats et des salariés ?",
             "Nous documentons pour chaque flux quelles données circulent, par quel outil, où elles sont stockées et combien de temps. Quand la sensibilité l'exige, nous utilisons des modèles hébergés en France. Vous repartez avec cette documentation, utile à votre registre des traitements."),
            ("Par quel processus commencer ?",
             "La centralisation des candidatures et la préparation de l'arrivée d'un nouveau collaborateur sont les deux plus simples à mettre en place, et ceux dont l'effet se voit le plus vite. Ils ne touchent ni à la paie ni aux données sensibles."),
        ],
    },
    'claude-vs-gpt4o': {
        'bref': "Comparer deux familles de modèles n'a de sens qu'au regard de vos tâches réelles. Nous testons les candidats sur vos propres documents, sur une tâche que vous faites vraiment, puis nous comparons les résultats et le coût. C'est ce test qui tranche, pas les classements publiés.",
        'faq': [
            ("Peut-on utiliser plusieurs modèles dans la même entreprise ?",
             "Oui, et c'est souvent le plus économique. Une tâche d'analyse exigeante et une tâche de routine n'appellent pas le même modèle ni le même coût. Nous montons les automatisations de façon à pouvoir changer de modèle sans tout réécrire."),
            ("Lequel est le plus sûr pour les données de l'entreprise ?",
             "La sécurité dépend surtout du mode d'accès, pas de la marque. Les accès professionnels n'utilisent pas vos données pour entraîner les modèles, contrairement à certaines offres grand public. Quand les données ne doivent pas sortir de France, nous déployons un modèle hébergé sur des serveurs français."),
            ("Comment tester avant d'engager un abonnement d'équipe ?",
             "Choisissez une tâche que vous faites chaque semaine, rassemblez dix cas passés dont vous connaissez le bon résultat, et soumettez-les à chaque modèle. La comparaison sur vos propres dossiers vaut mieux que n'importe quel comparatif, y compris celui-ci."),
        ],
    },
    'rgpd-ia-entreprise': {
        'bref': "Utiliser l'IA sans exposer les données de vos clients tient à trois décisions : quels outils sont autorisés, quelles informations n'y entrent jamais, et où les traitements ont lieu. Ces règles s'écrivent une fois, se tiennent en une page, et se transmettent aux équipes le jour où elles commencent.",
        'faq': [
            ("Les échanges avec un outil d'IA servent-ils à entraîner les modèles ?",
             "Cela dépend de l'offre souscrite. Les offres grand public gratuites le prévoient souvent dans leurs conditions, les accès professionnels et les interfaces de programmation l'excluent contractuellement. C'est la première chose à vérifier avant d'autoriser un outil dans l'entreprise."),
            ("Quelles règles poser en premier aux équipes ?",
             "Interdire la saisie de données de santé, de données bancaires identifiables et de fichiers clients bruts dans un outil non validé par la direction. Cette seule règle écarte la majorité des risques, et elle tient en une phrase compréhensible par tous."),
            ("Que faut-il documenter de notre côté ?",
             "Votre registre des traitements et votre politique de confidentialité doivent mentionner l'usage de l'IA, les données concernées et les prestataires impliqués. Nous fournissons cette documentation pour chaque flux que nous mettons en place, afin que vous puissiez la reprendre telle quelle."),
        ],
    },
    'roi-ia-pme': {
        'bref': "Évaluer ce que rapporte un projet d'IA revient à comparer le temps réellement libéré au coût de l'outil et de l'accompagnement. Le calcul n'a de valeur que si le temps de départ a été mesuré avant, sur une tâche précise. Sans cette mesure initiale, aucun gain n'est démontrable.",
        'faq': [
            ("En combien de temps un projet d'automatisation se rentabilise-t-il ?",
             "Cela dépend entièrement du temps que la tâche vous coûte aujourd'hui et de sa fréquence. C'est précisément ce que l'audit chiffre, sur vos chiffres à vous, avant tout engagement. Méfiez-vous des délais annoncés à l'avance sans connaître votre organisation."),
            ("Quels coûts sont souvent oubliés ?",
             "La formation des personnes qui utiliseront l'outil, l'abonnement mensuel aux plateformes d'automatisation, et le temps de surveillance des premières semaines. Nous les faisons figurer dans le chiffrage dès le départ, car ce sont eux qui font dérailler les budgets."),
            ("Comment mesurer le temps gagné ?",
             "Relevez le temps passé sur la tâche pendant une semaine avant de commencer, puis le nombre de dossiers traités seuls après la mise en service. La comparaison est parlante et se tient sur une feuille, sans outil de mesure particulier."),
        ],
    },
}


def completer(slug, donnees):
    p = RACINE / 'blog' / (slug + '.html')
    s = p.read_text(encoding='utf-8')
    if 'art-reponse' in s or 'art-faq' in s:
        sys.exit('%s possède déjà ces blocs' % slug)

    bref = '<p class="art-reponse"><strong>En bref.</strong> %s</p>\n' % donnees['bref']
    s = s.replace('<div class="art-body">\n', '<div class="art-body">\n' + bref, 1)

    questions = ''.join(
        '    <div class="faq-q"><h3>%s</h3><p>%s</p></div>\n' % (q, r) for q, r in donnees['faq'])
    faq = ('<section class="art-faq" aria-labelledby="faq-t">\n'
           '    <h2 id="faq-t">Questions fréquentes</h2>\n' + questions + '  </section>\n')
    marque = '  <aside class="lire-aussi"'
    if marque in s:
        s = s.replace(marque, faq + marque, 1)
    else:
        s = s.replace('</article>', faq + '</article>', 1)

    schema = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}}
        for q, r in donnees['faq']]}
    balise = '<script type="application/ld+json">%s</script>\n' % json.dumps(schema, ensure_ascii=False, separators=(',', ':'))
    s = s.replace('</head>', balise + '</head>', 1)

    p.write_text(s, encoding='utf-8')
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        json.loads(m.group(1))
    return len(donnees['bref'].split())


def main():
    for slug, donnees in ARTICLES.items():
        mots = completer(slug, donnees)
        print('  %-30s résumé de %d mots, %d questions' % (slug, mots, len(donnees['faq'])))
    print('%d article(s) complété(s)' % len(ARTICLES))


if __name__ == '__main__':
    main()
