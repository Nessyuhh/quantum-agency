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
