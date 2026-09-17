# Prompts pour les manipulations hors du site

Quatre tâches demandent un accès à un compte tiers, donc une autre session
Claude Code, connectée à ce compte. Chaque bloc ci-dessous se copie tel quel :
il est écrit pour être lu par une session qui ne sait rien de ce projet.

Ordre d'intérêt : 1 avant 2, les deux avant 3 et 4.

Règle commune, rappelée dans chaque prompt : **rien ne se crée ni ne s'envoie
sans l'accord explicite de l'utilisateur**, prise de compte comprise.

---

## 1. Vider le cache des aperçus de partage

À faire en premier, et une seule fois. Sans cela, la correction déjà déployée
reste invisible pendant des semaines sur les réseaux.

> Contexte. Le site quantum-agency.fr (cabinet de conseil en IA, statique sur
> GitHub Pages derrière Cloudflare) déclarait jusqu'à aujourd'hui une image de
> partage au format SVG sur ses 105 articles de blog. Aucun réseau social
> n'accepte le SVG : les articles partagés sortaient sans vignette. La balise
> pointe désormais sur https://quantum-agency.fr/og-image.png, un PNG de
> 1200x630 qui répond en 200. C'est corrigé dans le code et déployé.
>
> Problème restant. LinkedIn, X et Facebook gardent en cache l'ancienne
> réponse, parfois plusieurs semaines. Tant que l'adresse n'est pas re-scannée,
> un partage continue de sortir sans image.
>
> Ce que je te demande. Pour chacun des outils officiels de revalidation,
> soumettre les adresses de la liste ci-dessous et me dire, pour chacune, si
> l'aperçu affiche bien l'image :
>
> - LinkedIn Post Inspector : https://www.linkedin.com/post-inspector/
> - Validateur de cartes X : https://cards-dev.twitter.com/validator
> - Débogueur de partage Facebook : https://developers.facebook.com/tools/debug/
>
> Adresses à soumettre, dans cet ordre :
> 1. https://quantum-agency.fr/
> 2. https://quantum-agency.fr/expertise-comptable.html
> 3. https://quantum-agency.fr/services.html
> 4. https://quantum-agency.fr/blog.html
> 5. https://quantum-agency.fr/blog/audit-ia-guide.html
> 6. https://quantum-agency.fr/blog/roi-ia-pme.html
> 7. https://quantum-agency.fr/blog/ia-cabinet-expertise-comptable.html
> 8. https://quantum-agency.fr/blog/rgpd-ia-entreprise.html
>
> Le Post Inspector de LinkedIn demande une connexion au compte LinkedIn :
> demande-la-moi avant, ne crée aucun compte. Le validateur de X et le
> débogueur Facebook demandent un compte développeur ; si je n'en ai pas, ne
> m'en crée pas, dis-le simplement et passe.
>
> Ce que je veux en retour : un tableau de huit lignes, adresse par adresse,
> avec pour chaque outil « vignette affichée » ou le message d'erreur exact.
> Si une adresse échoue partout, donne l'en-tête HTTP et les balises og
> réellement servies, que je puisse corriger à la source.
>
> Ne modifie aucun fichier du site.

---

## 2. Relevé d'indexation dans la Search Console

> Contexte. quantum-agency.fr est un site statique de 120 adresses (6 pages
> principales, une page métier, 105 articles de blog, 7 pages en anglais). Une
> propriété de domaine est validée dans la Google Search Console et le plan du
> site https://quantum-agency.fr/sitemap.xml y est déclaré. La mesure d'audience
> passe par GA4, propriété G-2CZCESXSV6, avec Consent Mode v2. Le site est
> passé derrière Cloudflare il y a peu, et Lighthouse donne 100 en
> accessibilité, bonnes pratiques et référencement sur toutes les pages
> mesurées, avec un premier affichage mobile autour de 1,1 seconde.
>
> Ce que je te demande : un relevé, uniquement en lecture, de l'état réel de
> l'indexation. Rien à modifier, ni sur le site ni dans la Search Console.
>
> 1. Couverture : combien d'adresses indexées, combien découvertes mais non
>    indexées, combien explorées mais non indexées, combien en erreur. Pour
>    chaque catégorie non vide, la liste des adresses concernées et le motif
>    exact donné par Google.
> 2. Plan du site : date de la dernière lecture, nombre d'adresses lues,
>    nombre d'adresses indexées parmi elles, erreurs éventuelles.
> 3. Performances sur les 3 derniers mois : impressions, clics, position
>    moyenne. Les 30 requêtes qui rapportent le plus d'impressions, et les 20
>    pages qui rapportent le plus de clics.
> 4. Requêtes en position 5 à 20 : ce sont celles où un gain de contenu se
>    transforme vite en trafic. Donne-les avec leur page d'atterrissage.
> 5. Signaux web essentiels et ergonomie mobile : tout groupe d'adresses
>    signalé, avec le nom de la métrique en cause.
> 6. Actions manuelles et problèmes de sécurité : présents ou non.
> 7. Données structurées : tout type détecté en erreur ou en avertissement,
>    avec le nombre d'adresses concernées. Le site déclare Organization,
>    WebSite, Service, Course, FAQPage, BlogPosting et BreadcrumbList.
>
> Si un chiffre n'est pas disponible, écris-le. N'extrapole pas, et ne
> remplace jamais une donnée manquante par une estimation.
>
> Ce que je veux en retour : le relevé brut d'abord, ton interprétation
> ensuite, séparée et clairement identifiée comme telle. Puis les trois
> actions que tu ferais en premier, avec pour chacune la mesure de la Search
> Console qui la justifie.

---

## 3. Fiche d'établissement Google

Une décision m'appartient avant de lancer cette tâche : **quelle adresse
déclarer**. Google impose une adresse réelle, vérifiée par courrier ou par
vidéo. Une adresse fausse ou empruntée fait suspendre la fiche et cette
suspension est difficile à lever. Le statut « zone desservie », qui masque
l'adresse au public tout en la déclarant à Google, est le cas normal pour un
cabinet de conseil sans accueil de clientèle.

> Contexte. Quantum Consulting est un cabinet de conseil et de formation en
> intelligence artificielle pour les PME et ETI, basé à Paris, qui intervient
> partout en France. Site : https://quantum-agency.fr. Contact :
> contact@quantum-agency.fr. Prise de rendez-vous :
> https://calendly.com/younes_mh/audit. Le cabinet n'accueille pas de clientèle
> dans ses locaux : il se déplace ou travaille à distance.
>
> Ce que je te demande : préparer la création d'une fiche d'établissement
> Google en « zone desservie », c'est-à-dire avec une adresse déclarée à Google
> mais masquée au public.
>
> Étape 1, avant toute action : demande-moi l'adresse postale à déclarer et le
> numéro de téléphone à publier. Ne devine ni l'une ni l'autre, et ne reprends
> pas une adresse trouvée sur le web.
>
> Étape 2 : prépare et soumets-moi pour validation, en texte, avant toute
> saisie :
> - la catégorie principale et les catégories secondaires que tu proposes,
>   choisies dans la liste réelle de Google, pas inventées ;
> - la description de 750 caractères maximum ;
> - les zones desservies ;
> - les horaires ;
> - la liste des services à déclarer.
>
> La description doit être à la première personne du pluriel, sans jargon, et
> ne contenir aucun tiret long : c'est une règle ferme de ce projet.
>
> Étape 3, seulement après mon accord explicite sur chaque élément : crée la
> fiche. Arrête-toi net au moment de la vérification et dis-moi ce que Google
> demande. Ne saisis aucun code de vérification à ma place.
>
> Ce que je veux en retour : les propositions de l'étape 2 en un seul message,
> puis l'état exact de la fiche après création, avec le délai annoncé pour la
> vérification.

---

## 4. Liens entrants

C'est le frein principal aujourd'hui : le contenu, la technique et la vitesse
sont au maximum de ce que le site peut faire seul.

> Contexte. Quantum Consulting, cabinet de conseil et de formation en
> intelligence artificielle pour PME et ETI, basé à Paris, site
> https://quantum-agency.fr. Le site est techniquement irréprochable (100 en
> accessibilité, bonnes pratiques et référencement sur Lighthouse, premier
> affichage mobile autour de 1,1 s, 120 adresses dont 105 articles de blog) et
> ne reçoit presque aucun lien entrant. C'est le seul levier qui reste.
>
> Ce que je te demande, en deux temps.
>
> Premier temps, uniquement de la recherche, rien à soumettre. Établis la liste
> des annuaires et plateformes où un cabinet de conseil en IA basé en France a
> sa place, en vérifiant chacun sur le web avant de me le proposer. Pour chaque
> entrée : le nom, l'adresse exacte de la page d'inscription, ce que
> l'inscription coûte, ce qu'elle exige (numéro SIREN, certification, dossier,
> ancienneté), si le lien obtenu est suivi ou non par les moteurs, et le délai
> constaté. Vérifie que la page existe encore et que l'inscription est ouverte :
> ne me propose rien depuis ta mémoire.
>
> Pistes à examiner en priorité, à confirmer ou à écarter après vérification :
> - le répertoire des Activateurs France Num, portail public de la
>   transformation numérique des TPE et PME ;
> - la liste publique des organismes de formation du ministère du Travail, si
>   le cabinet détient un numéro de déclaration d'activité ;
> - les annuaires de la Chambre de commerce et d'industrie de Paris
>   Île-de-France ;
> - les places de marché de prestataires : Sortlist, Malt, Codeur, Bark ;
> - les annuaires d'entreprises alimentés par les données légales (Societe.com,
>   Pappers, Infogreffe), où une fiche existe probablement déjà sans être
>   revendiquée ;
> - la page entreprise LinkedIn, si elle n'existe pas encore ;
> - les réseaux d'entrepreneurs et clubs d'affaires parisiens qui publient un
>   annuaire de membres en ligne.
>
> Classe le tout par rapport entre l'effort demandé et la valeur du lien, et
> dis-moi franchement lesquelles ne valent pas le temps qu'elles coûtent.
>
> Second temps, seulement après que j'aie choisi dans ta liste. Pour chaque
> entrée retenue, prépare le texte de la fiche et soumets-le-moi avant toute
> saisie : description, catégories, services, mots-clés. Voix à la première
> personne du pluriel, public non technique, et **aucun tiret long**, c'est une
> règle ferme.
>
> Trois interdits, sans exception : ne crée aucun compte, ne soumets aucun
> formulaire et n'accepte aucune condition générale sans mon accord explicite
> à chaque fois. Si une inscription demande un paiement, arrête-toi et
> dis-le-moi.
>
> Écarte d'emblée tout ce qui relève de l'achat de liens, des fermes de liens
> et des échanges réciproques automatisés : Google les sanctionne et le risque
> n'est pas compensé par le gain.
