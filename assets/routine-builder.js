(function (root) {
  'use strict';
  var CODE_RE = /^[0-9A-Za-z]+$/;
  var ANCHOR_RE = /^r(\d+)$/;
  var MARK_TO_KEY = { a: 'am', p: 'pm', w: 'wk' };
  var KEY_TO_MARK = { am: 'a', pm: 'p', wk: 'w' };
  var PHASE_ORDER = ['am', 'pm', 'wk'];

  function segments(s) {
    s = String(s).split('#')[0].split('?')[0];
    var parts = s.split('/').filter(function (x) { return x.length; });
    for (var i = 0; i < parts.length; i++) {
      if (ANCHOR_RE.test(parts[i])) return parts.slice(i);
    }
    return parts;
  }

  function parseBlock(body, width) {
    var items = [], i = 0, n = body.length;
    while (i < n) {
      var chunk = body.substr(i, width);
      if (chunk.length !== width || !CODE_RE.test(chunk)) throw new Error('bad code chunk: ' + chunk);
      i += width;
      var code = chunk.replace(/^0+/, '') || '0';
      var freq = 7;
      if (i < n && body.charAt(i) === '~') {
        i += 1;
        var d = body.charAt(i);
        if (!/[1-6]/.test(d)) throw new Error('cadence must be 1-6');
        freq = parseInt(d, 10); i += 1;
      }
      items.push({ code: code, freq: freq });
    }
    return items;
  }

  function parseRoutine(s) {
    var parts = segments(s);
    var m = parts.length ? parts[0].match(ANCHOR_RE) : null;
    if (!m) throw new Error('missing anchor rW');
    var width = parseInt(m[1], 10);
    if (width < 1) throw new Error('width must be >= 1');
    var phases = [], seen = {};
    for (var i = 1; i < parts.length; i++) {
      var seg = parts[i], mark = seg.charAt(0), body = seg.slice(1);
      var key = MARK_TO_KEY[mark];
      if (!key) throw new Error('unknown phase marker: ' + mark);
      if (seen[key]) throw new Error('duplicate phase: ' + key);
      seen[key] = true;
      phases.push({ key: key, items: parseBlock(body, width) });
    }
    return { phases: phases };
  }

  function encodeRoutine(model) {
    var byKey = {}, all = [];
    (model.phases || []).forEach(function (p) {
      byKey[p.key] = p.items;
      p.items.forEach(function (it) { all.push(it.code); });
    });
    var width = 1;
    all.forEach(function (c) {
      if (!CODE_RE.test(c)) throw new Error('invalid code: ' + c);
      if (c.length > width) width = c.length;
    });
    var segs = ['r' + width];
    PHASE_ORDER.forEach(function (key) {
      if (!(key in byKey)) return;
      var block = KEY_TO_MARK[key];
      byKey[key].forEach(function (it) {
        var freq = it.freq === undefined ? 7 : it.freq;
        var padded = it.code;
        while (padded.length < width) padded = '0' + padded;
        block += padded + (freq === 7 ? '' : '~' + freq);
      });
      segs.push(block);
    });
    return segs.join('/');
  }

  function computeDashboard(model, catalog) {
    var codes = [], seen = {};
    (model.phases || []).forEach(function (p) {
      p.items.forEach(function (it) {
        if (!seen[it.code]) { seen[it.code] = 1; codes.push(it.code); }
      });
    });
    var products = codes.map(function (c) { return catalog.p[c]; }).filter(Boolean);
    var segs = products.map(function (p) { return p.g || 0; });
    var mean = segs.length ? segs.reduce(function (a, b) { return a + b; }, 0) / segs.length : 0;
    var strength = mean >= 3 ? 'Strong' : mean >= 2.25 ? 'Solid' : mean >= 1.5 ? 'Moderate' : 'Light';

    var count = {}, name = {};
    products.forEach(function (p) {
      (p.a || []).forEach(function (slug) {
        count[slug] = (count[slug] || 0) + 1;
        name[slug] = (catalog.i[slug] && catalog.i[slug].n) || slug;
      });
    });
    var actives = [], filterEntries = [], bands = {};
    Object.keys(count).forEach(function (slug) {
      var meta = catalog.i[slug] || {};
      if (meta.f) {
        filterEntries.push({ slug: slug, name: name[slug] });
        if (meta.f === 'both') { bands.UVB = 1; bands.UVA = 1; }
        else bands[meta.f.toUpperCase()] = 1;
      } else {
        actives.push({ slug: slug, name: name[slug], count: count[slug] });
      }
    });
    actives.sort(function (a, b) {
      return (b.count - a.count) || a.name.toLowerCase().localeCompare(b.name.toLowerCase());
    });
    var coverage = ['UVB', 'UVA'].filter(function (b) { return bands[b]; }).join(' + ');
    var filters = filterEntries.length ? { coverage: coverage || 'UV', entries: filterEntries } : null;
    var absent = (catalog.notable || []).filter(function (pair) {
      return !pair[1].some(function (m) { return count[m]; });
    }).map(function (pair) { return pair[0]; });

    return { strength: strength, product_count: products.length, ingredients: actives, filters: filters, absent: absent };
  }

  var api = { parseRoutine: parseRoutine, encodeRoutine: encodeRoutine, computeDashboard: computeDashboard };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.RoutineBuilder = api;

  if (typeof document !== 'undefined') {
    (function () {
      var catalog = JSON.parse(document.getElementById('rb-catalog').textContent);
      var model;
      try { model = parseRoutine(location.pathname); }
      catch (e) { model = { phases: [] }; }

      function items(key) {
        var p = model.phases.filter(function (x) { return x.key === key; })[0];
        if (!p) { p = { key: key, items: [] }; model.phases.push(p); }
        return p.items;
      }
      function has(key, code) { return items(key).some(function (it) { return it.code === code; }); }
      function add(key, code) { if (catalog.p[code] && !has(key, code)) { items(key).push({ code: code, freq: 7 }); sync(); } }
      function remove(key, code) {
        var arr = items(key);
        for (var i = 0; i < arr.length; i++) { if (arr[i].code === code) { arr.splice(i, 1); break; } }
        sync();
      }

      function badge(p) {
        var cls = p.t === 'top' ? 'rb-top' : p.t === 'mid' ? 'rb-mid' : 'rb-entry';
        var inner = p.th ? '<img src="' + p.th + '" alt="">' : (p.m || '?');
        return '<span class="rb-badge ' + cls + '">' + inner + '</span>';
      }

      function renderPhase(key, elId) {
        var el = document.getElementById(elId);
        el.innerHTML = '';
        items(key).forEach(function (it) {
          var p = catalog.p[it.code];
          if (!p) return;                                   // unknown code -> skip silently
          var row = document.createElement('div');
          row.className = 'rb-step';
          row.innerHTML = badge(p) + '<span class="rb-name">' + p.n + '</span> <button aria-label="remove">✕</button>';
          row.querySelector('button').onclick = function () { remove(key, it.code); };
          el.appendChild(row);
        });
      }

      function renderDash() {
        var d = computeDashboard(model, catalog);
        var el = document.getElementById('rb-dash');
        if (!d.product_count) { el.innerHTML = '<span class="empty">Search to add your first product.</span>'; return; }
        var actives = d.ingredients.map(function (i) { return i.name + (i.count > 1 ? ' ×' + i.count : ''); }).join(', ');
        var html = '<strong>' + d.strength + '</strong> · ' + d.product_count + ' product' + (d.product_count === 1 ? '' : 's');
        if (d.filters) html += ' · Sun: ' + d.filters.coverage;
        if (actives) html += '<br>Actives: ' + actives;
        if (d.absent.length) html += '<br>Does not contain: ' + d.absent.join(', ');
        el.innerHTML = html;
      }

      function renderResults(q) {
        var el = document.getElementById('rb-results');
        el.innerHTML = '';
        q = (q || '').trim().toLowerCase();
        if (!q) return;
        Object.keys(catalog.p).forEach(function (code) {
          var p = catalog.p[code];
          if ((p.n + ' ' + (p.c || '')).toLowerCase().indexOf(q) === -1) return;
          var li = document.createElement('li');
          li.innerHTML = '<span>' + p.n + '</span><span><button data-k="am">+ AM</button> <button data-k="pm">+ PM</button></span>';
          li.querySelectorAll('button').forEach(function (b) {
            b.onclick = function () { add(b.getAttribute('data-k'), code); };
          });
          el.appendChild(li);
        });
      }

      function sync() {
        model.phases = model.phases.filter(function (p) { return p.items.length; });
        var path = encodeRoutine(model);
        history.replaceState(null, '', document.querySelector('base').getAttribute('href') + path);
        renderPhase('am', 'rb-am');
        renderPhase('pm', 'rb-pm');
        renderDash();
      }

      document.getElementById('rb-search').addEventListener('input', function (e) { renderResults(e.target.value); });
      document.getElementById('rb-clear').addEventListener('click', function () {
        model = { phases: [] };
        document.getElementById('rb-search').value = '';
        document.getElementById('rb-results').innerHTML = '';
        sync();
      });
      document.getElementById('rb-copy').addEventListener('click', function () {
        navigator.clipboard.writeText(location.href).then(function () {
          document.getElementById('rb-copied').textContent = 'Copied!';
          setTimeout(function () { document.getElementById('rb-copied').textContent = ''; }, 1500);
        });
      });
      sync();                                               // initial render from the URL
    })();
  }
})(this);
