/* ============================================================================
   Repli des blocs longs, sur petit écran uniquement
   ----------------------------------------------------------------------------
   MESURE QUI MOTIVE CE FICHIER
   Sur mobile, les pages de service faisaient 9 à 11 écrans de défilement, soit
   environ 1,5 fois le desktop. La cause n'était pas le contenu mais sa mise à
   plat : 7 cartes de 957 px sur modeles-ia, 5 sections de 1 214 px sur
   agents-ia. Chaque bloc occupe un écran entier, et ils sont tous déployés.

   Un mobile ne doit pas être un desktop empilé. On y fait défiler, donc on
   choisit ce qu'on lit — on ne subit pas tout dans l'ordre.

   PROGRESSIF PAR CONSTRUCTION
   Sans JavaScript, rien ne change : tout reste ouvert, exactement comme
   aujourd'hui. Le repli est un enrichissement, jamais une condition d'accès au
   contenu. C'est aussi ce qui garantit que les moteurs de recherche voient
   l'intégralité du texte.
   ========================================================================== */

(function () {
  'use strict';

  var SEUIL_ECRAN = 640;      // au-delà, on ne replie rien
  var SEUIL_BLOC  = 520;      // un bloc plus court que ça ne gêne personne
  var GARDES      = 4;        // les premiers blocs restent ouverts : on ne veut
                              // pas accueillir le visiteur par un mur de titres.
                              // ⚠️ Ce compte ne porte QUE sur les blocs dépassant
                              // SEUIL_BLOC. Les sections courtes (trust-bar 80 px,
                              // stats 138 px) ne sont jamais candidates et ne
                              // consomment donc pas de garde — d'où l'écart entre
                              // « les 4 premières sections » et ce chiffre.
                              // À 4 : hero, expertises, Modèles & LLM et
                              // Consulting s'ouvrent d'emblée.

  /* On CHERCHE le conteneur des blocs répétés au lieu de le nommer.
     Viser « .content » ne suffisait pas : sur cas-usage les blocs sont un
     niveau plus bas, dans .sectors-grid, et faq-ia n'a pas de .content du tout.
     On descend donc l'arbre et on retient tout élément ayant au moins trois
     enfants dépassant le seuil — c'est la définition d'un mur de contenu,
     quel que soit son nom de classe. */
  function conteneursCandidats() {
    var racine = document.querySelector('main') || document.body;
    var trouves = [];
    (function descendre(e, profondeur) {
      if (profondeur > 6) return;
      var longs = Array.prototype.filter.call(e.children, function (x) {
        return x.getBoundingClientRect().height > SEUIL_BLOC;
      });
      if (longs.length >= 3) { trouves.push(e); return; }  // on ne descend plus
      Array.prototype.forEach.call(e.children, function (x) {
        descendre(x, profondeur + 1);
      });
    })(racine, 0);
    return trouves;
  }

  function replier() {
    if (window.innerWidth > SEUIL_ECRAN) return;

    conteneursCandidats().forEach(function (c) {
      var blocs = Array.prototype.filter.call(c.children, function (e) {
        return e.getBoundingClientRect().height > SEUIL_BLOC &&
               !e.hasAttribute('data-replie');
      });
      if (blocs.length < 3) return;   // deux blocs longs ne font pas un mur

      blocs.forEach(function (bloc, i) {
        if (i < GARDES) return;
        bloc.setAttribute('data-replie', 'ferme');

        // Le titre du bloc sert d'intitulé : on n'invente pas de libellé.
        var titre = bloc.querySelector('h2, h3, h4');
        var texte = titre ? titre.textContent.trim() : 'Lire la suite';

        var b = document.createElement('button');
        b.className = 'replier-btn';
        b.type = 'button';
        b.setAttribute('aria-expanded', 'false');
        b.innerHTML = '<span>' + texte + '</span><span class="replier-chev" aria-hidden="true">▾</span>';

        b.addEventListener('click', function () {
          var ferme = bloc.getAttribute('data-replie') === 'ferme';
          bloc.setAttribute('data-replie', ferme ? 'ouvert' : 'ferme');
          b.setAttribute('aria-expanded', ferme ? 'true' : 'false');
          if (!ferme) b.scrollIntoView({ block: 'nearest' });
        });

        bloc.parentNode.insertBefore(b, bloc);
      });
    });
  }

  // On attend que la mise en page soit stable : mesurer une hauteur avant que
  // les polices soient chargées donne des valeurs fausses.
  if (document.readyState === 'complete') replier();
  else window.addEventListener('load', replier);
})();
