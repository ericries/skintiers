var assert = require('assert');
var path = require('path');
var fs = require('fs');
var rb = require(path.join(__dirname, '..', '..', 'assets', 'routine-builder.js'));
var vectors = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'fixtures', 'routine_vectors.json'), 'utf8'));

vectors.forEach(function (v) {
  assert.deepStrictEqual(rb.parseRoutine(v.path), v.model, 'parse mismatch for ' + v.path);
  assert.strictEqual(rb.encodeRoutine(v.model), v.path, 'encode mismatch for ' + v.path);
});
console.log('codec parity OK (' + vectors.length + ' vectors)');
var dc = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'fixtures', 'routine_dashboard_case.json'), 'utf8'));
assert.deepStrictEqual(rb.computeDashboard(dc.model, dc.catalog), dc.expected, 'dashboard mismatch');
console.log('dashboard parity OK');

// Redundancy / load flags: a routine with two retinoids (distinct actives, same
// family), a doubled irritant, and 3+ irritants must raise the three flags.
var flagCat = {
  v: 1,
  p: {
    '0': { s: 'tret', n: 'Tretinoin cream', c: 'Treatments', t: 'top', g: 4, a: ['tretinoin', 'azelaic-acid'], th: null, m: 'T' },
    '1': { s: 'retinal', n: 'Retinal serum', c: 'Treatments', t: 'top', g: 3, a: ['retinaldehyde'], th: null, m: 'R' },
    '2': { s: 'az', n: 'Azelaic gel', c: 'Treatments', t: 'top', g: 3, a: ['azelaic-acid'], th: null, m: 'A' }
  },
  i: {
    'tretinoin': { n: 'Tretinoin', ev: 'best', cl: 'retinoid', ir: 1 },
    'retinaldehyde': { n: 'Retinaldehyde', ev: 'good', cl: 'retinoid', ir: 1 },
    'azelaic-acid': { n: 'Azelaic acid', ev: 'good', ir: 1 }
  },
  notable: []
};
var flagModel = { phases: [{ key: 'pm', items: [{ code: '0', freq: 7 }, { code: '1', freq: 7 }, { code: '2', freq: 7 }] }] };
var fd = rb.computeDashboard(flagModel, flagCat);
var kinds = fd.flags.map(function (f) { return f.kind; }).sort();
assert.deepStrictEqual(kinds, ['class', 'dup', 'load'], 'expected dup+class+load flags, got ' + JSON.stringify(fd.flags));
var classFlag = fd.flags.filter(function (f) { return f.kind === 'class'; })[0];
assert.ok(/2 retinoids/.test(classFlag.text) && /Tretinoin/.test(classFlag.text) && /Retinaldehyde/.test(classFlag.text), 'class flag text: ' + classFlag.text);
var dupFlag = fd.flags.filter(function (f) { return f.kind === 'dup'; })[0];
assert.ok(/Azelaic acid is in 2/.test(dupFlag.text), 'dup flag text: ' + dupFlag.text);
// Evidence buckets: all three land in 'well' (best/good).
assert.deepStrictEqual(fd.evidence.map(function (b) { return b.key; }), ['well'], 'evidence buckets: ' + JSON.stringify(fd.evidence));
console.log('flags + evidence OK');
