/* Barre collante du résultat sur téléphone (RECETTE §5, règle du 2026-10-11).
   Tant que le bloc [data-resultat][data-barre] est sous l'écran, une barre en bas reprend
   son intitulé (premier <p>) et son chiffre clé ([data-barre-chiffre]). Construite côté client :
   aucun texte dupliqué dans le HTML. */
(function () {
  var card = document.querySelector('[data-resultat][data-barre]');
  if (!card || typeof IntersectionObserver === 'undefined') return;
  var label = card.querySelector('p');
  var fig = card.querySelector('[data-barre-chiffre]');
  if (!fig) return;
  var bar = document.createElement('button');
  bar.type = 'button';
  bar.setAttribute('aria-hidden', 'true');
  bar.tabIndex = -1;
  bar.style.cssText = 'position:fixed;left:0;right:0;bottom:0;z-index:40;display:none;align-items:baseline;justify-content:space-between;gap:12px;padding:12px 16px;border:0;border-top:1px solid #bae6fd;background:#f0f9ff;box-shadow:0 -4px 12px rgba(15,23,42,.08);text-align:left;font:inherit;cursor:pointer';
  var l = document.createElement('span');
  l.style.cssText = 'font-size:14px;font-weight:500;color:#0369a1';
  var v = document.createElement('span');
  v.style.cssText = 'font-size:20px;font-weight:700;color:#0f172a;font-variant-numeric:tabular-nums';
  bar.appendChild(l); bar.appendChild(v);
  function sync() { l.textContent = label ? label.textContent.trim() : ''; v.textContent = fig.textContent.trim(); }
  sync();
  new MutationObserver(sync).observe(fig, { childList: true, characterData: true, subtree: true });
  bar.addEventListener('click', function () { card.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
  document.body.appendChild(bar);
  var mq = window.matchMedia('(max-width: 1023px)');
  var below = false;
  // Le bouton « Voir mes résultats » existant remonte au-dessus de la barre quand elle s'affiche.
  var pill = document.getElementById('mobile-results-btn');
  function show() {
    var on = below && mq.matches;
    bar.style.display = on ? 'flex' : 'none';
    if (pill) pill.style.bottom = on ? (bar.offsetHeight + 12) + 'px' : '';
  }
  new IntersectionObserver(function (e) { below = !e[0].isIntersecting && e[0].boundingClientRect.top > 0; show(); }).observe(card);
  if (mq.addEventListener) mq.addEventListener('change', show);
})();
