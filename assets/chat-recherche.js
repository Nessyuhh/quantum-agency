/* ============================================================================
   Quantum Consulting : recherche dans la base de connaissance de l'assistant
   Un seul fichier pour deux usages :
   - le Worker (formulaire/chat.js) s'en sert pour choisir les passages du
     site qu'il donne au modèle d'IA, ce qui l'empêche d'inventer ;
   - la fenêtre du chat (assets/chat.js) s'en sert pour répondre seule quand
     les modèles gratuits ont atteint leur quota du jour.
   Score BM25, le classique des moteurs de recherche, sur des mots ramenés à
   leur racine et débarrassés des accents.
   ========================================================================== */
(function (racine) {
  'use strict';

  var VIDES = ('a au aux avec ce ces cet cette dans de des du elle en est et eux il ils je la le les leur lui ma mais me meme mes moi mon ne nos notre nous on ou par pas pour qu que qui sa se ses son sur ta te tes toi ton tu un une vos votre vous y ' +
    'c d j l m n s t est sont ete etre avoir ai as avons avez ont fait faire peut peux pouvez puis quoi quel quelle quels quelles comment combien pourquoi quand ca cela ceci tres plus moins tout tous toute toutes si oui non bonjour merci fait faites faites etes suis sommes ete avez propose proposez offrez ' +
    'the of and to in is are be it for on with as at by an this that from or can do does what how why when which who you your we our us my me i').split(' ');
  var ESTVIDE = {};
  VIDES.forEach(function (m) { ESTVIDE[m] = 1; });

  /* Quelques équivalences, pour que « tarif » trouve « prix » et « IA »
     trouve « intelligence artificielle ». */
  var SYNONYMES = {
    tarif: 'prix', cout: 'prix', couter: 'prix', budget: 'prix', combien: 'prix', price: 'prix', cost: 'prix',
    ia: 'intelligence', ai: 'intelligence', llm: 'modele', model: 'modele', chatgpt: 'modele', claude: 'modele', mistral: 'modele',
    rgpd: 'rgpd', gdpr: 'rgpd', donnee: 'donnee', data: 'donnee', securite: 'securite', security: 'securite', confidentialite: 'securite',
    formation: 'former', former: 'former', form: 'former', formez: 'former', training: 'former', train: 'former',
    automatisation: 'automatis', automatiser: 'automatis', automate: 'automatis', automation: 'automatis',
    facture: 'factur', invoice: 'factur', devis: 'devis', quote: 'devis', relance: 'relanc', rdv: 'rendez', rendez: 'rendez', appel: 'rendez',
    site: 'site', website: 'site', vitrine: 'site'
  };

  function normaliser(texte) {
    return String(texte || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/[’']/g, ' ').replace(/[^a-z0-9]+/g, ' ').trim();
  }
  /* Racine grossière mais efficace en français comme en anglais : on retire
     les terminaisons courantes, puis on tronque à six lettres. */
  function racineMot(m) {
    if (SYNONYMES[m]) return SYNONYMES[m];
    var r = m.replace(/(ements?|ations?|ateurs?|atrices?|ements|ment|ions?|eurs?|euses?|ing|ies|es|s|x|e)$/, '');
    if (r.length < 3) r = m;
    r = r.slice(0, 6);
    return SYNONYMES[r] || r;
  }
  function mots(texte) {
    return normaliser(texte).split(' ').filter(function (m) { return m.length > 1 && !ESTVIDE[m]; }).map(racineMot);
  }

  function creer(entrees) {
    var docs = entrees.map(function (e) {
      var q = mots(e.q), r = mots(e.r);
      var tf = {};
      q.forEach(function (m) { tf[m] = (tf[m] || 0) + 3; });   // la question pèse triple
      r.forEach(function (m) { tf[m] = (tf[m] || 0) + 1; });
      return { e: e, tf: tf, long: q.length * 3 + r.length, cle: /\/blog\//.test(e.u) ? 1 : 1.35 };
    });
    var df = {};
    docs.forEach(function (d) { Object.keys(d.tf).forEach(function (m) { df[m] = (df[m] || 0) + 1; }); });
    var N = docs.length || 1;
    var moyenne = docs.reduce(function (s, d) { return s + d.long; }, 0) / N;

    function chercher(question, n) {
      var q = mots(question);
      if (!q.length) return [];
      var vus = {};
      q = q.filter(function (m) { if (vus[m]) return false; vus[m] = 1; return true; });
      var k1 = 1.4, b = 0.7;
      var res = [];
      docs.forEach(function (d) {
        var s = 0, trouves = 0;
        q.forEach(function (m) {
          var f = d.tf[m];
          if (!f) return;
          trouves++;
          var idf = Math.log(1 + (N - df[m] + 0.5) / (df[m] + 0.5));
          s += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * d.long / moyenne));
        });
        /* Couvrir plusieurs mots de la question vaut plus que répéter l'un d'eux. */
        if (s > 0) res.push({ entree: d.e, score: s * d.cle * (0.6 + 0.4 * trouves / q.length), couverture: trouves / q.length });
      });
      res.sort(function (a, b2) { return b2.score - a.score; });
      return res.slice(0, n || 5);
    }
    return { chercher: chercher };
  }

  var api = { creer: creer, mots: mots };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else racine.QuantumRecherche = api;
})(typeof self !== 'undefined' ? self : this);
