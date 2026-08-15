// Client-side product filter for filter.html. Reads the inlined products-filter.json
// (built by build.py:filter_catalog), populates the category/active selects from the
// data, and filters entirely in the browser. It only SHOWS the site's own grades
// (effect strength 0-4, effect + evidence words); it never computes a ranking.
(function () {
  'use strict';
  if (typeof document === 'undefined') return;

  var node = document.getElementById('pf-catalog');
  if (!node) return;
  var products = (JSON.parse(node.textContent) || {}).products || [];

  var qEl = document.getElementById('pf-q');
  var catEl = document.getElementById('pf-cat');
  var activeEl = document.getElementById('pf-active');
  var priceEl = document.getElementById('pf-price');
  var tierEl = document.getElementById('pf-tier');
  var countEl = document.getElementById('pf-count');
  var listEl = document.getElementById('pf-results');
  var emptyEl = document.getElementById('pf-empty');

  // Build the category + active option lists from the catalog, so they match the data.
  function fillOptions() {
    var cats = {}, actives = {};
    products.forEach(function (p) {
      if (p.category) cats[p.category] = 1;
      (p.actives || []).forEach(function (a) { actives[a.slug] = a.name; });
    });
    Object.keys(cats).sort().forEach(function (c) {
      var o = document.createElement('option'); o.value = c; o.textContent = c;
      catEl.appendChild(o);
    });
    Object.keys(actives).sort(function (a, b) {
      return actives[a].toLowerCase().localeCompare(actives[b].toLowerCase());
    }).forEach(function (slug) {
      var o = document.createElement('option'); o.value = slug; o.textContent = actives[slug];
      activeEl.appendChild(o);
    });
  }

  function segs(n) {
    var out = '';
    for (var i = 0; i < 4; i++) out += '<i class="seg' + (i < n ? ' on' : '') + '"></i>';
    return '<span class="segs" aria-hidden="true">' + out + '</span>';
  }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }

  function gradeText(p) {
    if (!p.effect) return 'Not yet graded';
    var t = p.effect.charAt(0).toUpperCase() + p.effect.slice(1);
    if (p.evidence) t += ' effect, ' + p.evidence + ' evidence';
    return t;
  }

  function matches(p) {
    var q = (qEl.value || '').trim().toLowerCase();
    if (q && ((p.name || '') + ' ' + (p.brand || '')).toLowerCase().indexOf(q) === -1) return false;
    if (catEl.value && p.category !== catEl.value) return false;
    if (activeEl.value && !(p.actives || []).some(function (a) { return a.slug === activeEl.value; })) return false;
    var max = parseFloat(priceEl.value);
    if (!isNaN(max)) {
      if (p.price == null) return false;          // price not listed -> excluded under a max
      if (p.price > max) return false;
    }
    var minSeg = parseInt(tierEl.value, 10) || 0;
    if (minSeg && (p.segs || 0) < minSeg) return false;
    return true;
  }

  function row(p) {
    var li = document.createElement('li');
    li.className = 'pf-item';
    var price = p.price_display
      ? '<span class="pf-price">' + esc(p.price_display) + (p.price_size ? ' <small>· ' + esc(p.price_size) + '</small>' : '') + '</span>'
      : '<span class="pf-price pf-nolist">Price not listed</span>';
    var brand = p.brand ? '<span class="pf-brand">' + esc(p.brand) + '</span>' : '';
    li.innerHTML =
      '<a class="pf-link" href="' + esc(p.url) + '">' + esc(p.name) + '</a>'
      + brand
      + '<span class="pf-meta">' + esc(p.category || '') + '</span>'
      + '<span class="pf-grade" title="' + esc(gradeText(p)) + '">' + segs(p.segs || 0)
      + '<span class="pf-grade-t">' + esc(gradeText(p)) + '</span></span>'
      + price;
    return li;
  }

  function render() {
    var hits = products.filter(matches);
    listEl.innerHTML = '';
    hits.forEach(function (p) { listEl.appendChild(row(p)); });
    countEl.textContent = hits.length + ' of ' + products.length + ' products';
    emptyEl.hidden = hits.length !== 0;
  }

  fillOptions();
  [qEl, catEl, activeEl, priceEl, tierEl].forEach(function (el) {
    el.addEventListener('input', render);
    el.addEventListener('change', render);
  });
  render();
})();
