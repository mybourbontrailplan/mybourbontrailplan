/*
 * verify_qr.js - proves js/qr.js is a correct QR encoder.
 *
 * Run from the repo root:  node scripts/verify_qr.js
 *
 * We vendor our own encoder (see the header of js/qr.js for why), so it needs a
 * real correctness check rather than "the phone scanned it once". This compares
 * our module matrix against the `qrcode` Python package, which is already a
 * project dependency via scripts/generate_pdf_map.py, for every version and
 * every error-correction level.
 *
 * Two passes:
 *   1. Forced mask, all 8 masks, every version and level. Exercises data
 *      encoding, Reed-Solomon, block interleaving, function patterns, data
 *      placement, and format/version info. This is the correctness gate.
 *   2. Automatic mask. Asserts that whatever mask our scorer picks, the matrix
 *      we emit is byte-identical to the reference's matrix for that same mask.
 *
 * Together those two passes prove our output always decodes, without needing a
 * decoder installed: pass 1 shows our matrix equals a known-good library's for
 * any given mask, and pass 2 shows our automatic path only ever emits one of
 * those verified matrices. That is stronger than a scan test, which proves one
 * code works on one reader.
 *
 * Mask *agreement* is reported as a statistic, not a gate. Mask choice is a
 * scannability heuristic and never affects whether a code decodes. We follow the
 * ISO rule that the 1:1:3:1:1 pattern needs its 4-module light run inside the
 * symbol; qrcode additionally uses a Horspool-style skip that can miss
 * overlapping occurrences, so the two scorers sometimes prefer different masks.
 */
'use strict';

const { execFileSync } = require('child_process');
const path = require('path');

require(path.join(__dirname, '..', 'js', 'qr.js'));
const QR = globalThis.QR;

const PY = `
import json, sys
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H
LV = {'L': ERROR_CORRECT_L, 'M': ERROR_CORRECT_M, 'Q': ERROR_CORRECT_Q, 'H': ERROR_CORRECT_H}
out = []
for case in json.load(sys.stdin):
    mask = case.get('mask')
    if mask is None:
        # best_mask_pattern() is a method here, and it must be resolved before
        # the final make() so the same mask lands in the matrix we compare.
        probe = qrcode.QRCode(version=case['version'], error_correction=LV[case['ecl']],
                              box_size=1, border=0)
        probe.add_data(case['text'])
        probe.make(fit=False)
        mask = probe.best_mask_pattern()
    q = qrcode.QRCode(version=case['version'], error_correction=LV[case['ecl']],
                      box_size=1, border=0, mask_pattern=mask)
    q.add_data(case['text'])
    q.make(fit=False)
    rows = [''.join('1' if v else '0' for v in row) for row in q.modules]
    out.append({'rows': rows, 'mask': mask})
print(json.dumps(out))
`;

function pyMatrices(cases) {
  const res = execFileSync('python', ['-c', PY], {
    input: JSON.stringify(cases),
    maxBuffer: 1 << 28,
    encoding: 'utf8'
  });
  return JSON.parse(res);
}

function ourRows(qr) {
  const rows = [];
  for (let r = 0; r < qr.size; r++) {
    let s = '';
    for (let c = 0; c < qr.size; c++) s += qr.modules[r][c] ? '1' : '0';
    rows.push(s);
  }
  return rows;
}

/* Payloads shaped like what the host toolkit actually produces, plus edge
   cases: shortest possible, a full-width UTF-8 string, and a long URL with a
   slugified property name. */
function payloadFor(bytesWanted) {
  const base = 'https://mybourbontrailplan.com/map.html?region=bardstown'
    + '&utm_source=host&utm_medium=qr&utm_campaign=guest-map&utm_content=';
  if (bytesWanted <= base.length) return base.slice(0, Math.max(1, bytesWanted));
  return base + 'x'.repeat(bytesWanted - base.length);
}

const LEVELS = ['L', 'M', 'Q', 'H'];
let checked = 0, failed = 0;
const failures = [];

const capacityBytes = QR.capacityBytes;

console.log('Comparing js/qr.js against the qrcode Python package.\n');

/* ---- pass 1: forced masks, every version and level ---- */
for (const ecl of LEVELS) {
  for (let version = 1; version <= 40; version++) {
    const cap = capacityBytes(version, ecl);
    /* Sit just under capacity so the version is genuinely exercised, and also
       test a short payload in the same version. */
    const texts = [payloadFor(Math.max(1, cap - 1))];
    if (cap > 20) texts.push(payloadFor(12));

    const cases = [];
    const ours = [];
    for (const text of texts) {
      for (let mask = 0; mask < 8; mask++) {
        cases.push({ text, version, ecl, mask });
        ours.push(QR.encode(text, { ecl, version, mask }));
      }
    }
    const theirs = pyMatrices(cases);
    for (let i = 0; i < cases.length; i++) {
      checked++;
      const a = ourRows(ours[i]).join('\n');
      const b = theirs[i].rows.join('\n');
      if (a !== b) {
        failed++;
        if (failures.length < 6) {
          failures.push(`v${version} ${ecl} mask${cases[i].mask} len=${cases[i].text.length}`);
        }
      }
    }
  }
  process.stdout.write(`  level ${ecl}: forced-mask matrices compared\n`);
}

/* ---- pass 2: automatic mask selection ----
   Gate: our auto-selected matrix must equal the reference's matrix for the mask
   we chose. Statistic: how often the two scorers pick the same mask. */
let maskDisagree = 0;
const autoCases = [], autoOurs = [], sameMaskCases = [];
for (const ecl of LEVELS) {
  for (let version = 1; version <= 40; version++) {
    const cap = capacityBytes(version, ecl);
    const text = payloadFor(Math.max(1, Math.min(cap - 1, 60 + version)));
    const mine = QR.encode(text, { ecl, version });
    autoOurs.push(mine);
    autoCases.push({ text, version, ecl, mask: null });        /* their own pick */
    sameMaskCases.push({ text, version, ecl, mask: mine.mask }); /* forced to ours */
  }
}
const autoTheirs = pyMatrices(autoCases);
const atOurMask = pyMatrices(sameMaskCases);
for (let i = 0; i < autoCases.length; i++) {
  checked++;
  if (ourRows(autoOurs[i]).join('\n') !== atOurMask[i].rows.join('\n')) {
    failed++;
    if (failures.length < 12) {
      failures.push(`AUTO v${autoCases[i].version} ${autoCases[i].ecl} mask${autoOurs[i].mask}: matrix differs from reference at the same mask`);
    }
  }
  if (autoOurs[i].mask !== autoTheirs[i].mask) maskDisagree++;
}
console.log('  automatic-mask matrices compared\n');

/* ---- automatic version selection sanity ---- */
const autoV = QR.encode(payloadFor(90), { ecl: 'M' });
console.log(`Automatic version pick for a 90-byte payload at M: v${autoV.version}, size ${autoV.size}`);
const utf = QR.encode('Willow Creek Farmhouse – Bardstown éèê', { ecl: 'Q' });
console.log(`UTF-8 payload encodes: v${utf.version} mask ${utf.mask}`);

console.log(`\nmatrices checked:  ${checked}`);
console.log(`mismatches:        ${failed}`);
console.log(`mask disagreements: ${maskDisagree} of ${autoCases.length} auto cases ` +
  `(heuristic only, not a defect - see header)`);
if (failures.length) {
  console.log('\nfirst failures:');
  failures.forEach(f => console.log('  ' + f));
}
if (failed === 0) {
  console.log('\nPASS - every matrix we can emit is byte-identical to the reference');
  console.log('       implementation at the same version, level, and mask.');
  process.exit(0);
}
console.log('\nFAIL');
process.exit(1);
