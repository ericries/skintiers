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
